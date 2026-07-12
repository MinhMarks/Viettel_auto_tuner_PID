import numpy as np
from .base_objective import ObjectiveFunction
import sys
import os

# Add parent directory to path to import metrics
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.metrics import calculate_metrics

class TimeDomainObjectiveFunction(ObjectiveFunction):
    def __init__(self):
        super().__init__(
            name="Time-Domain Objective (MTE + Rise Time)",
            description="Focuses on Maximum Tracking Error (Peak Error) and Rise Time (only valid for Step response)."
        )

    def evaluate(self, env, controller, t_max, dt, trajectory_type, setpoint_pitch, setpoint_yaw, tuning_profile):
        steps = int(t_max / dt)
        state = [0.0, 0.0, 0.0, 0.0]
        
        cost = 0.0
        
        # Normalization Constants
        J1_MAX = 300.0 # ITAE
        MTE_MAX = 20.0 # Degrees
        RISE_TIME_MAX = 5.0 # Seconds
        J3_MAX = 1000.0 # Saturation
        
        # Default Weights (balanced)
        w_itae = 1.0
        w_mte = 5.0
        w_rise = 2.0
        w_saturation = 1.0
        
        if tuning_profile == 'aggressive':
            w_itae = 1.0
            w_mte = 3.0
            w_rise = 6.0
            w_saturation = 0.5
        elif tuning_profile == 'conservative':
            w_itae = 1.5
            w_mte = 8.0
            w_rise = 0.5
            w_saturation = 3.0
            
        history_t = []
        history_pitch = []
        history_yaw = []
        history_vp = []
        history_vy = []
        
        itae_sum = 0.0
        sat_sum = 0.0
        max_err_p = 0.0
        max_err_y = 0.0
        
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
            
            history_t.append(t)
            history_pitch.append(pitch)
            history_yaw.append(yaw)
            
            error_pitch = abs(sp_p - pitch)
            error_yaw = abs(sp_y - yaw)
            
            # Track Max Tracking Error
            if error_pitch > max_err_p: max_err_p = error_pitch
            if error_yaw > max_err_y: max_err_y = error_yaw
            
            # J1: ITAE
            itae_sum += (t * (error_pitch + error_yaw) * dt)
            
            if abs(pitch) > np.pi or abs(yaw) > np.pi:
                return 10000.0

            v_pitch_raw, v_yaw_raw = controller.compute(pitch, yaw, dt, sp_p, sp_y)
            
            history_vp.append(v_pitch_raw)
            history_vy.append(v_yaw_raw)
            
            v_pitch = np.clip(v_pitch_raw, env.V_min, env.V_max)
            v_yaw = np.clip(v_yaw_raw, env.V_min, env.V_max)
            
            # J3: Saturation Penalty
            oversaturation_p = max(0, abs(v_pitch_raw) - env.V_max)
            oversaturation_y = max(0, abs(v_yaw_raw) - env.V_max)
            if oversaturation_p > 0 or oversaturation_y > 0:
                sat_sum += ((oversaturation_p + oversaturation_y) * dt)
                
            state = env.simulate_step(state, v_pitch, v_yaw, dt)
            
        # Add ITAE & Saturation to cost
        cost += w_itae * (itae_sum / J1_MAX)
        cost += w_saturation * (sat_sum / J3_MAX)
        
        # Add Maximum Tracking Error (L-infinity norm) to cost
        cost += w_mte * ((max_err_p + max_err_y) / MTE_MAX)
        
        # Add Rise Time if trajectory is step
        if trajectory_type == 'step':
            m_pitch = calculate_metrics(history_t, history_pitch, setpoint_pitch, history_vp)
            m_yaw = calculate_metrics(history_t, history_yaw, setpoint_yaw, history_vy)
            
            rt_p = m_pitch.get('rise_time')
            rt_y = m_yaw.get('rise_time')
            
            rt_p_val = rt_p if rt_p is not None else RISE_TIME_MAX
            rt_y_val = rt_y if rt_y is not None else RISE_TIME_MAX
            
            cost += w_rise * ((rt_p_val + rt_y_val) / (2 * RISE_TIME_MAX))
            
        return cost
