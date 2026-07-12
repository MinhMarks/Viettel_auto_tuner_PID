import os
import csv
import json
import time
from datetime import datetime
import numpy as np
from core.helicopter_2dof_env import Helicopter2DOF
from core.pid_controller import DecentralizedPID
from core.metrics import calculate_metrics

LOG_DIR = os.path.join(os.path.dirname(__file__), 'experiment_logs')

def save_experiment_results(results_dict, req):
    """
    Saves the results of an experiment suite to a CSV file and full details to a JSON log.
    """
    os.makedirs(LOG_DIR, exist_ok=True)
    
    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if getattr(req, 'run_dir', None):
        run_dir = req.run_dir
    else:
        timestamp_file = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_dir = os.path.join(LOG_DIR, f'run_{timestamp_file}')
        
    os.makedirs(run_dir, exist_ok=True)
    
    csv_file = os.path.join(run_dir, 'experiment_summary.csv')
    file_exists = os.path.isfile(csv_file)
    
    # 1. Append to CSV
    # Define columns
    fieldnames = [
        'Timestamp',
        'Seed',
        'Algorithm',
        'Objective_Type',
        'Tuning_Profile',
        'Trajectory_Type',
        'Controller_Type',
        'GS_Method',
        'T_Max',
        'Setpoint_Pitch',
        'Setpoint_Yaw',
        'Disturbance_Wind_P',
        'Disturbance_Wind_Y',
        'Disturbance_Sensor_Noise',
        'Disturbance_Payload',
        'Iterations',
        'Best_Cost',
        'Kp_pitch', 'Ki_pitch', 'Kd_pitch',
        'Kp_yaw', 'Ki_yaw', 'Kd_yaw',
        'Execution_Time_sec',
        'Pitch_RiseTime', 'Pitch_SettlingTime', 'Pitch_Overshoot', 'Pitch_SSE', 'Pitch_CE', 'Pitch_ITAE',
        'Yaw_RiseTime', 'Yaw_SettlingTime', 'Yaw_Overshoot', 'Yaw_SSE', 'Yaw_CE', 'Yaw_ITAE'
    ]
    
    def simulate_for_metrics(params, sp_pitch, sp_yaw, t_max, dist_cfg, params_large, gs_method, trajectory_type='step'):
        env = Helicopter2DOF(disturbance_config=dist_cfg)
        controller = DecentralizedPID(params, sp_pitch, sp_yaw, params_large=params_large, gs_method=gs_method)
        state = [0.0, 0.0, 0.0, 0.0]
        time_step = 0.01
        steps = int(t_max / time_step)
        
        t_arr, p_arr, y_arr = [], [], []
        u_p_arr, u_y_arr = [], []
        current_time = 0.0
        
        sp_p_arr, sp_y_arr = [], []
        for _ in range(steps):
            t = current_time
            if trajectory_type == 'step':
                sp_p, sp_y = sp_pitch, sp_yaw
            elif trajectory_type == 'sine':
                import numpy as np
                sp_p = sp_pitch * np.sin(2 * np.pi * 0.25 * t)
                sp_y = sp_yaw * np.sin(2 * np.pi * 0.25 * t)
            elif trajectory_type == 'square':
                import numpy as np
                sp_p = sp_pitch if np.sin(2 * np.pi * 0.1 * t) > 0 else -sp_pitch
                sp_y = sp_yaw if np.sin(2 * np.pi * 0.1 * t) > 0 else -sp_yaw
            elif trajectory_type == 'multi-step':
                sp_p = sp_pitch * (min(int(t / 2.5) + 1, 4) / 4.0)
                sp_y = sp_yaw * (min(int(t / 2.5) + 1, 4) / 4.0)
            else:
                sp_p, sp_y = sp_pitch, sp_yaw
                
            t_arr.append(current_time)
            p_arr.append(state[0])
            y_arr.append(state[2])
            sp_p_arr.append(sp_p)
            sp_y_arr.append(sp_y)
            
            u = controller.compute(state[0], state[2], time_step, setpoint_pitch=sp_p, setpoint_yaw=sp_y)
            u_p_arr.append(u[0])
            u_y_arr.append(u[1])
            
            state = env.simulate_step(state, u[0], u[1], time_step)
            current_time += time_step
            
        m_pitch = calculate_metrics(t_arr, p_arr, sp_p_arr if trajectory_type != 'step' else sp_pitch, u_p_arr)
        m_yaw = calculate_metrics(t_arr, y_arr, sp_y_arr if trajectory_type != 'step' else sp_yaw, u_y_arr)
        return m_pitch, m_yaw
    
    with open(csv_file, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
            
        dist_cfg = req.disturbance_config or {}
            
        for algo, res in results_dict.items():
            if "iterations_data" in res:
                for iter_data in res["iterations_data"]:
                    params = iter_data["best_params"]
                    
                    # Fill missing params with None if less than 6 (should be exactly 6 or 12)
                    p = params + [None]*max(0, 6 - len(params))
                
                    # Calculate metrics
                    params_large = params[6:] if len(params) > 6 else None
                    m_pitch, m_yaw = simulate_for_metrics(params[:6], req.setpoint_pitch, req.setpoint_yaw, req.t_max, dist_cfg, params_large, req.gs_method, getattr(req, 'trajectory_type', 'step'))
                    
                    writer.writerow({
                        'Timestamp': timestamp_str,
                        'Seed': getattr(req, 'seed', 'None'),
                        'Algorithm': algo,
                        'Objective_Type': req.objective_type,
                        'Tuning_Profile': req.tuning_profile,
                        'Trajectory_Type': req.trajectory_type,
                        'Controller_Type': req.controller_type,
                        'GS_Method': req.gs_method or 'None',
                        'T_Max': req.t_max,
                        'Setpoint_Pitch': req.setpoint_pitch,
                        'Setpoint_Yaw': req.setpoint_yaw,
                        'Disturbance_Wind_P': dist_cfg.get('wind_torque_p', 0.0),
                        'Disturbance_Wind_Y': dist_cfg.get('wind_torque_y', 0.0),
                        'Disturbance_Sensor_Noise': dist_cfg.get('sensor_noise_std', 0.0),
                        'Disturbance_Payload': dist_cfg.get('mass_payload', 1.0),
                        'Iterations': iter_data['iters'],
                        'Best_Cost': iter_data['best_cost'],
                        'Kp_pitch': p[0], 'Ki_pitch': p[1], 'Kd_pitch': p[2],
                        'Kp_yaw': p[3], 'Ki_yaw': p[4], 'Kd_yaw': p[5],
                        'Execution_Time_sec': iter_data.get('time', 0.0),
                        'Pitch_RiseTime': m_pitch.get('rise_time'),
                        'Pitch_SettlingTime': m_pitch.get('settling_time'),
                        'Pitch_Overshoot': m_pitch.get('overshoot'),
                        'Pitch_SSE': m_pitch.get('steady_state_error'),
                        'Pitch_CE': m_pitch.get('control_energy'),
                        'Pitch_ITAE': m_pitch.get('itae'),
                        'Yaw_RiseTime': m_yaw.get('rise_time'),
                        'Yaw_SettlingTime': m_yaw.get('settling_time'),
                        'Yaw_Overshoot': m_yaw.get('overshoot'),
                        'Yaw_SSE': m_yaw.get('steady_state_error'),
                        'Yaw_CE': m_yaw.get('control_energy'),
                        'Yaw_ITAE': m_yaw.get('itae')
                    })
                
    # 2. Save full detail to JSON
    full_log_file = os.path.join(run_dir, 'full_log.json')
    log_data = {
        'metadata': {
            'timestamp': timestamp_str,
            'request_config': {
                'setpoint_pitch': req.setpoint_pitch,
                'setpoint_yaw': req.setpoint_yaw,
                't_max': req.t_max,
                'disturbance_config': req.disturbance_config,
                'tuning_profile': req.tuning_profile,
                'objective_type': req.objective_type,
                'gs_method': req.gs_method,
                'seed': getattr(req, 'seed', None)
            }
        },
        'results': results_dict
    }
    
    with open(full_log_file, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, indent=4)
        
    # 3. Save convergence history to CSV
    convergence_file = os.path.join(run_dir, 'convergence_history.csv')
    file_exists = os.path.isfile(convergence_file)
    algo_names = [algo for algo in results_dict.keys() if "best_overall" in results_dict[algo] and "cost_history" in results_dict[algo]["best_overall"]]
    if algo_names:
        max_iters_hist = 0
        for algo in algo_names:
            hist = results_dict[algo]["best_overall"]["cost_history"]
            if len(hist) > max_iters_hist:
                max_iters_hist = len(hist)
        
        with open(convergence_file, mode='a', newline='', encoding='utf-8') as f:
            fieldnames = ['Seed', 'Objective_Type', 'Tuning_Profile', 'Controller_Type', 'GS_Method', 'Iteration'] 
            for algo in algo_names:
                fieldnames.append(f"{algo}_Cost")
                fieldnames.append(f"{algo}_Time")
                
            writer2 = csv.DictWriter(f, fieldnames=fieldnames)
            
            if not file_exists:
                writer2.writeheader()
            
            for i in range(max_iters_hist):
                row_dict = {
                    'Seed': getattr(req, 'seed', 'None'),
                    'Objective_Type': req.objective_type,
                    'Tuning_Profile': req.tuning_profile,
                    'Controller_Type': req.controller_type,
                    'GS_Method': req.gs_method or 'None',
                    'Iteration': i + 1
                }
                for algo in algo_names:
                    hist = results_dict[algo]["best_overall"]["cost_history"]
                    time_hist = results_dict[algo]["best_overall"].get("time_history", [])
                    
                    if i < len(hist):
                        row_dict[f"{algo}_Cost"] = hist[i]
                    else:
                        row_dict[f"{algo}_Cost"] = hist[-1] if hist else ""
                        
                    if i < len(time_hist):
                        row_dict[f"{algo}_Time"] = time_hist[i]
                    else:
                        row_dict[f"{algo}_Time"] = time_hist[-1] if time_hist else ""
                        
                writer2.writerow(row_dict)
            
    print(f"Logged experiment to {csv_file}, {convergence_file}, and full detail to {full_log_file}")
        
    return run_dir

def save_robustness_results(all_test_metrics, run_dir):
    """
    Saves robustness testing metrics into a CSV matching the experiment logger standard.
    """
    if not all_test_metrics or not run_dir or not os.path.exists(run_dir):
        return

    csv_path = os.path.join(run_dir, "robustness_test_results.csv")
    
    file_exists = os.path.exists(csv_path)
    
    with open(csv_path, mode='a', newline='', encoding='utf-8') as f:
        fieldnames = ["Algorithm", "Tuning_Objective", "Tuning_Profile", "Controller_Type", "GS_Method", "Tuning_Disturbance", "Test_Trajectory", "Configuration", "Seed",
                      "Disturbance_Wind_P", "Disturbance_Wind_Y", "Disturbance_Sensor_Noise", "Disturbance_Payload",
                      "Pitch_RiseTime", "Pitch_SettlingTime", "Pitch_Overshoot", "Pitch_SSE", "Pitch_CE", "Pitch_ITAE",
                      "Yaw_RiseTime", "Yaw_SettlingTime", "Yaw_Overshoot", "Yaw_SSE", "Yaw_CE", "Yaw_ITAE"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        for row in all_test_metrics:
            writer.writerow(row)
    print(f"Robustness Test results saved to {csv_path}")
