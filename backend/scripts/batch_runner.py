import itertools
import requests
import time
import csv
import os

URL_TUNE = "http://localhost:8088/api/compare_algorithms"
URL_TEST = "http://localhost:8088/api/robustness_sweep"

from datetime import datetime
batch_run_dir = os.path.join(os.path.dirname(__file__), 'experiment_logs', f'batch_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
os.makedirs(batch_run_dir, exist_ok=True)

# ----------------- 1. TUNING CONFIGURATION -----------------
objectives_and_profiles = {
    # "default_objective": ["balanced"], # "aggressive", "eco", "safety"],
    "time_domain_objective": ["balanced", "aggressive"] # , "conservative"]
}

controller_types = ["classic"] # , "fuzzy", "model_based"] # Các loại bộ điều khiển (không phải phương pháp Gain Scheduling)
gs_methods = ["", "linear" ] # , "step" , "sigmoid"] # Test all Gain Scheduling methods and without GS

# Base tuning disturbances
training_disturbances = [
    {"name": "No Noise", "config": {}},
]

training_trajectories = ["step"] # Training is strictly on step

iterations = {
    # "GA": [50],       # Thường hội tụ sau 30-50 vòng lặp (epochs/generations)
    "PSO": [50],      # Thường hội tụ sau 30-50 vòng lặp
    "TPE": [75],      # Bayesian Optimization (Optuna), thường cần 50-100 trials để quét đủ không gian
    "CMA-ES": [50],   # Rất mạnh và nhanh cho không gian liên tục, thường hội tụ sau 30-50 vòng
    "GWO": [50]       # Grey Wolf Optimizer, thường hội tụ sau 30-50 vòng
}

# ----------------- 2. TESTING CONFIGURATION -----------------
testing_config = {
    "trajectory_type": "multi-step",
    "base_disturbance_config": {"wind_torque_p": 0.01, "wind_torque_y": 0.01, "sensor_noise_std": 0.005, "mass_payload": 0.01},
    "step_increments": {"wind_torque_p": 0.01, "wind_torque_y": 0.01, "sensor_noise_std": 0.005, "mass_payload": 0.01},
    "steps": 7, #1,
    "t_max": 20.0
}


# ----------------- 3. GENERATE COMBINATIONS -----------------
seeds = [42, 43, 44, 45, 46, 1, 2, 3 ,4 ,5, 6] # N=5. N=10 to 30 for serious statistical publications

combinations = []
for seed in seeds:
    for obj, profiles in objectives_and_profiles.items():
        for profile in profiles:
            for c_type in controller_types:
                for gs in gs_methods:
                    for dist in training_disturbances:
                        for traj in training_trajectories:
                            combinations.append((seed, obj, profile, c_type, gs, dist, traj))

print(f"Total experiments to run: {len(combinations)}")
print("-" * 50)

for i, (seed, obj, profile, c_type, gs, dist, traj) in enumerate(combinations):
    print(f"\n--- Running Experiment {i+1}/{len(combinations)} ---")
    print(f"Tuning Config: Seed={seed}, Objective={obj}, Profile={profile}, Controller={c_type}, GS={gs if gs else 'None'}, Disturbance={dist['name']}")
    
    # ----------------- PHASE 1: TUNING -----------------
    tune_payload = {
        "iters_dict": iterations,
        "setpoint_pitch": 0.436, #0.81, # ~25 degrees
        "setpoint_yaw": 0.52,   # ~30 degrees
        "t_max": 20.0,
        "disturbance_config": dist["config"],
        "tuning_profile": profile,
        "objective_type": obj,
        "trajectory_type": traj,
        "controller_type": c_type,
        "gs_method": gs,
        "run_dir": batch_run_dir,
        "seed": seed
    }
    
    t0 = time.time()
    try:
        tune_res = requests.post(URL_TUNE, json=tune_payload)
        if tune_res.status_code == 200:
            results = tune_res.json()
            run_dir = results.get("_metadata", {}).get("run_dir", "")
            print(f"Tuning completed in {time.time()-t0:.2f}s. Saved to: {run_dir}")
            
            # Extract Best PIDs
            tuned_pids = {}
            for algo, data in results.items():
                if algo == "_metadata": continue
                if data and data.get("best_overall"):
                    best_params = data["best_overall"]["best_params"]
                    tuned_pids[algo] = best_params
            
            if not tuned_pids:
                print("No PIDs found. Skipping testing.")
                continue
                
            # ----------------- PHASE 2: TESTING -----------------
            print(f"Starting Robustness Test on trajectory: {testing_config['trajectory_type']}...")
            
            all_test_metrics = []
            
            for algo, params in tuned_pids.items():
                test_payload = {
                    "params": params,
                    "setpoint_pitch": 0.436, # 0.81, ~25 degrees
                    "setpoint_yaw": 0.52,
                    "base_disturbance_config": testing_config["base_disturbance_config"],
                    "step_increments": testing_config["step_increments"],
                    "steps": testing_config["steps"],
                    "t_max": testing_config["t_max"],
                    "trajectory_type": testing_config["trajectory_type"],
                    "gs_method": gs,
                    "controller_type": c_type
                }
                
                test_res = requests.post(URL_TEST, json=test_payload)
                if test_res.status_code == 200:
                    test_data = test_res.json()
                    # test_data is dict: {"Conf 1": {"metrics": {"pitch": {...}, "yaw": {...}}}, ...}
                    for conf_name, conf_data in test_data.items():
                        conf_dict = conf_data.get("config", {})
                        m_pitch = conf_data["metrics"]["pitch"]
                        m_yaw = conf_data["metrics"]["yaw"]
                        all_test_metrics.append({
                            "Algorithm": algo,
                            "Tuning_Objective": obj,
                            "Tuning_Profile": profile,
                            "Controller_Type": c_type,
                            "GS_Method": gs if gs else 'None',
                            "Tuning_Disturbance": dist['name'],
                            "Test_Trajectory": testing_config["trajectory_type"],
                            "Configuration": conf_name,
                            "Seed": seed,
                            "Disturbance_Wind_P": conf_dict.get("wind_torque_p", 0.0),
                            "Disturbance_Wind_Y": conf_dict.get("wind_torque_y", 0.0),
                            "Disturbance_Sensor_Noise": conf_dict.get("sensor_noise_std", 0.0),
                            "Disturbance_Payload": conf_dict.get("mass_payload", 1.0),
                            "Pitch_RiseTime": m_pitch.get("rise_time", ""),
                            "Pitch_SettlingTime": m_pitch.get("settling_time", ""),
                            "Pitch_Overshoot": m_pitch.get("overshoot", ""),
                            "Pitch_SSE": m_pitch.get("steady_state_error", ""),
                            "Pitch_CE": m_pitch.get("control_energy", ""),
                            "Pitch_ITAE": m_pitch.get("itae", ""),
                            "Yaw_RiseTime": m_yaw.get("rise_time", ""),
                            "Yaw_SettlingTime": m_yaw.get("settling_time", ""),
                            "Yaw_Overshoot": m_yaw.get("overshoot", ""),
                            "Yaw_SSE": m_yaw.get("steady_state_error", ""),
                            "Yaw_CE": m_yaw.get("control_energy", ""),
                            "Yaw_ITAE": m_yaw.get("itae", "")
                        })
                else:
                    print(f"Test Error {test_res.status_code} for {algo}")
            
            # Save Test Results to CSV
            from experiment_logger import save_robustness_results
            save_robustness_results(all_test_metrics, run_dir)
            
        else:
            print(f"Error {tune_res.status_code}: {tune_res.text}")
    except Exception as e:
        print(f"Request failed: {e}")
