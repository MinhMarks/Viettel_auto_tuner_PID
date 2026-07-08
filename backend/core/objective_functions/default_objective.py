import numpy as np
from .base_objective import ObjectiveFunction

class DefaultObjectiveFunction(ObjectiveFunction):
    def __init__(self):
        super().__init__(
            name="Default Multi-Objective (J1+J2+J3)",
            description="The classic multi-objective function using ITAE, Energy, Smoothness and Saturation Penalty."
        )

    def evaluate(self, env, controller, t_max, dt, trajectory_type, setpoint_pitch, setpoint_yaw, tuning_profile):
        steps = int(t_max / dt)
        state = [0.0, 0.0, 0.0, 0.0]
        
        cost = 0.0
        prev_v_pitch = 0.0
        prev_v_yaw = 0.0
        
        # Normalization Constants (J_max)
        J1_MAX = 300.0
        J2_E_MAX = 11520.0
        J2_S_MAX = 46080.0
        J3_MAX = 1000.0
        
        # Weights
        if tuning_profile == 'aggressive':
            w_itae, w_energy, w_smoothness, w_saturation = 5.0, 1.0, 2.0, 1.0
        elif tuning_profile == 'eco':
            w_itae, w_energy, w_smoothness, w_saturation = 1.0, 5.0, 10.0, 1.0
        elif tuning_profile == 'safety':
            w_itae, w_energy, w_smoothness, w_saturation = 1.0, 1.0, 1.0, 50.0
        else: # balanced
            w_itae, w_energy, w_smoothness, w_saturation = 1.0, 1.0, 1.0, 1.0
            
        for i in range(steps):
            t = i * dt
            
            # Target Setpoint
            if trajectory_type == 'step':
                sp_p, sp_y = setpoint_pitch, setpoint_yaw
            elif trajectory_type == 'sine':
                sp_p = setpoint_pitch * np.sin(2 * np.pi * 0.25 * t)
                sp_y = setpoint_yaw * np.sin(2 * np.pi * 0.25 * t)
            elif trajectory_type == 'square':
                sp_p = setpoint_pitch if np.sin(2 * np.pi * 0.1 * t) > 0 else -setpoint_pitch
                sp_y = setpoint_yaw if np.sin(2 * np.pi * 0.1 * t) > 0 else -setpoint_yaw
            elif trajectory_type == 'multi-step':
                sp_p = setpoint_pitch * (min(int(t / 2.5) + 1, 4) / 4.0)
                sp_y = setpoint_yaw * (min(int(t / 2.5) + 1, 4) / 4.0)
            else:
                sp_p, sp_y = setpoint_pitch, setpoint_yaw

            pitch, _, yaw, _ = state
            
            error_pitch = abs(sp_p - pitch)
            error_yaw = abs(sp_y - yaw)
            
            # J1: ITAE
            cost += w_itae * ((t * (error_pitch + error_yaw) * dt) / J1_MAX)
            
            if abs(pitch) > np.pi or abs(yaw) > np.pi:
                cost += 10000.0
                break

            v_pitch_raw, v_yaw_raw = controller.compute(pitch, yaw, dt, sp_p, sp_y)
            
            v_pitch = np.clip(v_pitch_raw, env.V_min, env.V_max)
            v_yaw = np.clip(v_yaw_raw, env.V_min, env.V_max)
            
            # J2: Energy & Smoothness
            cost += w_energy * (((v_pitch**2 + v_yaw**2) * dt) / J2_E_MAX)
            cost += w_smoothness * ((((v_pitch - prev_v_pitch)**2 + (v_yaw - prev_v_yaw)**2) * dt) / J2_S_MAX)
            
            # J3: Saturation Penalty
            oversaturation_p = max(0, abs(v_pitch_raw) - env.V_max)
            oversaturation_y = max(0, abs(v_yaw_raw) - env.V_max)
            if oversaturation_p > 0 or oversaturation_y > 0:
                cost += w_saturation * (((oversaturation_p + oversaturation_y) * dt) / J3_MAX)
                
            prev_v_pitch = v_pitch
            prev_v_yaw = v_yaw
            
            state = env.simulate_step(state, v_pitch, v_yaw, dt)
            
        return cost
