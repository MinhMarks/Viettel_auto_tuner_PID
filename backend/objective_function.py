import numpy as np
from helicopter_2dof_env import Helicopter2DOF
from pid_controller import DecentralizedPID

def evaluate_helicopter(params, setpoint_pitch, setpoint_yaw, t_max=10.0, dt=0.02, disturbance_config=None, trajectory_type='step', params_large=None, gs_method='step', controller_type='classic', tuning_profile='aggressive'):
    """
    Simulate the 2-DOF Helicopter with given PID params and compute the ITAE cost.
    params: [Kp_p, Ki_p, Kd_p, Kp_y, Ki_y, Kd_y] for small/normal angles.
    params_large: optional [Kp_p, Ki_p, Kd_p, Kp_y, Ki_y, Kd_y] for large angles.
    gs_method: Gain scheduling method ('step', 'linear', 'sigmoid').
    """
    env = Helicopter2DOF(disturbance_config=disturbance_config)
    controller = DecentralizedPID(params, setpoint_pitch, setpoint_yaw, controller_type=controller_type, params_large=params_large, gs_method=gs_method)
    
    steps = int(t_max / dt)
    state = [0.0, 0.0, 0.0, 0.0]
    
    cost = 0.0
    
    prev_v_pitch = 0.0
    prev_v_yaw = 0.0
    
    # Normalization Constants (J_max) to bring all components to ~[0, 1] scale
    J1_MAX = 300.0     # Max nominal ITAE (e.g. 180 deg error over 10s)
    J2_E_MAX = 11520.0 # Max Energy (24^2 + 24^2) * 10s
    J2_S_MAX = 46080.0 # Max Smoothness chatter (48^2 + 48^2) * 10s
    J3_MAX = 1000.0    # Nominal max saturation penalty
    
    # Configure weights based on tuning_profile
    if tuning_profile == 'aggressive':
        w_itae = 5.0
        w_energy = 1.0
        w_smoothness = 2.0
        w_saturation = 1.0
    elif tuning_profile == 'eco':
        w_itae = 1.0
        w_energy = 5.0
        w_smoothness = 10.0
        w_saturation = 1.0
    elif tuning_profile == 'safety':
        w_itae = 1.0
        w_energy = 1.0
        w_smoothness = 1.0
        w_saturation = 50.0
    else: # balanced
        w_itae = 1.0
        w_energy = 1.0
        w_smoothness = 1.0
        w_saturation = 1.0
        
    for i in range(steps):
        t = i * dt
        
        # Determine current setpoint based on trajectory type
        if trajectory_type == 'step':
            sp_p = setpoint_pitch
            sp_y = setpoint_yaw
        elif trajectory_type == 'sine':
            # 0.25 Hz sine wave
            sp_p = setpoint_pitch * np.sin(2 * np.pi * 0.25 * t)
            sp_y = setpoint_yaw * np.sin(2 * np.pi * 0.25 * t)
        elif trajectory_type == 'square':
            # 0.1 Hz square wave
            sp_p = setpoint_pitch if np.sin(2 * np.pi * 0.1 * t) > 0 else -setpoint_pitch
            sp_y = setpoint_yaw if np.sin(2 * np.pi * 0.1 * t) > 0 else -setpoint_yaw
        elif trajectory_type == 'multi-step':
            sp_p = setpoint_pitch * (min(int(t / 2.5) + 1, 4) / 4.0)
            sp_y = setpoint_yaw * (min(int(t / 2.5) + 1, 4) / 4.0)
        else:
            sp_p, sp_y = setpoint_pitch, setpoint_yaw

        pitch, _, yaw, _ = state
        
        # Calculate Absolute Error
        error_pitch = abs(sp_p - pitch)
        error_yaw = abs(sp_y - yaw)
        
        # --- J1: Performance (ITAE) ---
        j1_step = (t * (error_pitch + error_yaw) * dt) / J1_MAX
        cost += w_itae * j1_step
        
        # Penalty for massive overshoot or instability (Safety Constraint)
        if abs(pitch) > np.pi or abs(yaw) > np.pi:
            cost += 10000.0  # Heavy penalty for diverging
            break

        # Calculate requested control signal (Gain Scheduling and other advanced control types are now handled intrinsically in DecentralizedPID)
        v_pitch_raw, v_yaw_raw = controller.compute(pitch, yaw, dt, sp_p, sp_y)
        
        # Clip to actual actuator capabilities
        v_pitch = np.clip(v_pitch_raw, env.V_min, env.V_max)
        v_yaw = np.clip(v_yaw_raw, env.V_min, env.V_max)
        
        # --- J2: Actuator Protection (Energy & Smoothness) ---
        j2_e_step = ((v_pitch**2 + v_yaw**2) * dt) / J2_E_MAX
        j2_s_step = (((v_pitch - prev_v_pitch)**2 + (v_yaw - prev_v_yaw)**2) * dt) / J2_S_MAX
        cost += w_energy * j2_e_step
        cost += w_smoothness * j2_s_step
        
        # --- J3: Physical Constraint (Saturation Penalty) ---
        # Penalize the optimizer if it requests voltages beyond physical limits
        oversaturation_p = max(0, abs(v_pitch_raw) - env.V_max)
        oversaturation_y = max(0, abs(v_yaw_raw) - env.V_max)
        if oversaturation_p > 0 or oversaturation_y > 0:
            j3_step = ((oversaturation_p + oversaturation_y) * dt) / J3_MAX
            cost += w_saturation * j3_step
            
        prev_v_pitch = v_pitch
        prev_v_yaw = v_yaw
        
        # Step env (using clipped realistic voltages)
        state = env.simulate_step(state, v_pitch, v_yaw, dt)
        
    return cost

def evaluate_schaffer_f6(params):
    """
    Schaffer F6 benchmark function.
    Args:
        params (list): [x, y] coordinates
    Returns:
        float: Function value
    """
    x, y = params[0], params[1]
    r2 = x**2 + y**2
    numerator = np.sin(np.sqrt(r2))**2 - 0.5
    denominator = (1 + 0.001 * r2)**2
    return 0.5 + numerator / denominator
