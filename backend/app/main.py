from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import time
import json
import asyncio
import numpy as np

from core.helicopter_2dof_env import Helicopter2DOF
from core.pid_controller import DecentralizedPID, MIMOLQRController
from core.optimizers import TuningOptimizers
from core.metrics import calculate_metrics
from core.analytical_baseline import compute_lqr_pid_baseline, compute_mimo_lqr_baseline
from app.database import log_history, get_history, clear_history, get_stats

import os

app = FastAPI(title="Helicopter 2-DOF PID Tuning API")

progress_tracker = {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class SimulateRequest(BaseModel):
    params: List[float]  # [Kp_p, Ki_p, Kd_p, Kp_y, Ki_y, Kd_y]
    params_large: Optional[List[float]] = None
    setpoint_pitch: float
    setpoint_yaw: float
    t_max: float = 10.0
    disturbance_config: Optional[dict] = None
    trajectory_type: str = 'step'
    gs_method: str = 'step'
    controller_type: str = 'classic'
    tuning_profile: str = 'balanced'
    objective_type: str = 'default_objective'

class TuneRequest(BaseModel):
    task_id: Optional[str] = None
    algorithm: str # "pso" or "bo"
    setpoint_pitch: float
    setpoint_yaw: float
    iters: int = 30
    disturbance_config: Optional[dict] = None
    trajectory_type: str = 'step'
    t_max: float = 10.0
    tuning_profile: str = 'balanced'
    objective_type: str = 'default_objective'

class BenchmarkRequest(BaseModel):
    algorithm: str # currently supports "pso"
    iters: int = 50

class CompareRequest(BaseModel):
    task_id: Optional[str] = None
    setpoint_pitch: float
    setpoint_yaw: float
    iters_dict: dict
    trajectory_type: str = 'step'
    t_max: float = 10.0
    disturbance_config: Optional[dict] = None
    gs_method: Optional[str] = None
    controller_type: str = 'classic'
    tuning_profile: str = 'balanced'
    objective_type: str = 'default_objective'
    run_dir: Optional[str] = None
    seed: Optional[int] = None

class TestSuiteRequest(BaseModel):
    params: List[float]
    params_large: Optional[List[float]] = None
    setpoint_pitch: float
    setpoint_yaw: float
    t_max: float = 10.0
    trajectory_type: str = 'step'
    gs_method: str = 'step'

class RobustnessSweepRequest(BaseModel):
    params: List[float]
    params_large: Optional[List[float]] = None
    setpoint_pitch: float
    setpoint_yaw: float
    base_disturbance_config: Optional[dict] = None
    step_increments: dict
    steps: int
    t_max: float = 10.0
    trajectory_type: str = 'step'
    gs_method: str = 'step'
    controller_type: str = 'classic'

class LQRCompareRequest(BaseModel):
    disturbance_config: Optional[dict] = None
    t_max: float = 10.0
    sp_pitch_step: float = 0.5
    sp_yaw_fixed: float = 0.0
    sine_amplitude: float = 0.4
    sine_freq: float = 0.25

@app.post("/api/compare_lqr_pid")
def compare_lqr_pid(req: LQRCompareRequest):
    """
    Chay so sanh LQR (MIMO) vs Decentralized PID (SISO).
    Tra ve du lieu chuoi thoi gian cho 2 kich ban:
      - Scenario 1: Asymmetric Step Test
      - Scenario 3: Sine Trajectory Tracking
    """
    import sys as _sys, os as _os
    _sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), '..', 'scripts'))
    from compare_lqr_pid import run_comparison

    dist = req.disturbance_config or {
        "wind_torque_p": 0.01, "wind_torque_y": 0.01,
        "sensor_noise_std": 0.005, "mass_payload": 0.01
    }

    results = run_comparison(
        disturbance_config=dist,
        t_max=req.t_max,
        dt=0.002,
        sp_pitch_step=req.sp_pitch_step,
        sp_yaw_fixed=req.sp_yaw_fixed,
        sine_amplitude=req.sine_amplitude,
        sine_freq=req.sine_freq,
        output_dir=_os.path.join(_os.path.dirname(__file__), '..', 'scripts')
    )

    # Downsample to reduce payload (keep every 5th point)
    def ds(arr): return arr[::5]

    return {
        "scenario1": {
            "label": results["scenario1"]["label"],
            "time": ds(results["scenario1"]["lqr_time"]),
            "lqr_pitch": ds(results["scenario1"]["lqr_pitch"]),
            "lqr_yaw": ds(results["scenario1"]["lqr_yaw"]),
            "pid_pitch": ds(results["scenario1"]["pid_pitch"]),
            "pid_yaw": ds(results["scenario1"]["pid_yaw"]),
            "sp_pitch": ds(results["scenario1"]["lqr_sp_pitch"]),
            "sp_yaw": ds(results["scenario1"]["lqr_sp_yaw"]),
            "metrics": results["scenario1"]["metrics"],
        },
        "scenario3": {
            "label": results["scenario3"]["label"],
            "time": ds(results["scenario3"]["lqr_time"]),
            "lqr_pitch": ds(results["scenario3"]["lqr_pitch"]),
            "lqr_yaw": ds(results["scenario3"]["lqr_yaw"]),
            "pid_pitch": ds(results["scenario3"]["pid_pitch"]),
            "pid_yaw": ds(results["scenario3"]["pid_yaw"]),
            "sp_pitch": ds(results["scenario3"]["lqr_sp_pitch"]),
            "sp_yaw": ds(results["scenario3"]["lqr_sp_yaw"]),
            "metrics": results["scenario3"]["metrics"],
        }
    }

@app.post("/api/simulate")
def simulate(req: SimulateRequest):
    env = Helicopter2DOF(disturbance_config=req.disturbance_config)
    if not req.params or len(req.params) < 3:
        print(f"[ERROR] simulate called with invalid params: {req.params}")
    
    if req.controller_type == 'mimo_lqr':
        controller = MIMOLQRController(req.params, v_limits=(env.V_min, env.V_max))
    else:
        controller = DecentralizedPID(req.params, req.setpoint_pitch, req.setpoint_yaw, controller_type=req.controller_type)
    
    dt = 0.002
    steps = int(req.t_max / dt)
    state = [0.0, 0.0, 0.0, 0.0]
    
    history_t = []
    history_pitch = []
    history_yaw = []
    history_sp_p = []
    history_sp_y = []
    history_vp = []
    history_vy = []
    
    for i in range(steps):
        t = i * dt
        # Determine current setpoint based on trajectory type
        import numpy as np
        if req.trajectory_type == 'step':
            sp_p = req.setpoint_pitch
            sp_y = req.setpoint_yaw
        elif req.trajectory_type == 'sine':
            sp_p = req.setpoint_pitch * np.sin(2 * np.pi * 0.25 * t)
            sp_y = req.setpoint_yaw * np.sin(2 * np.pi * 0.25 * t)
        elif req.trajectory_type == 'square':
            sp_p = req.setpoint_pitch if np.sin(2 * np.pi * 0.1 * t) > 0 else -req.setpoint_pitch
            sp_y = req.setpoint_yaw if np.sin(2 * np.pi * 0.1 * t) > 0 else -req.setpoint_yaw
        elif req.trajectory_type == 'multi-step':
            sp_p = req.setpoint_pitch * (min(int(t / 2.5) + 1, 4) / 4.0)
            sp_y = req.setpoint_yaw * (min(int(t / 2.5) + 1, 4) / 4.0)
        else:
            sp_p, sp_y = req.setpoint_pitch, req.setpoint_yaw

        pitch, _, yaw, _ = state
        history_t.append(t)
        history_pitch.append(pitch)
        history_yaw.append(yaw)
        history_sp_p.append(sp_p)
        history_sp_y.append(sp_y)
        
        # Calculate control signal (Gain Scheduling is handled internally if configured)
        v_pitch, v_yaw = controller.compute(pitch, yaw, dt, sp_p, sp_y)
        
        if req.controller_type == 'mimo_lqr':
            gravity_ff = env.K_g * np.cos(pitch) / env.K_pp
            v_pitch += gravity_ff
            v_pitch = np.clip(v_pitch, env.V_min, env.V_max)
            
        history_vp.append(v_pitch)
        history_vy.append(v_yaw)
        
        state = env.simulate_step(state, v_pitch, v_yaw, dt)
        
    metrics_pitch = calculate_metrics(history_t, history_pitch, req.setpoint_pitch, history_vp)
    metrics_yaw = calculate_metrics(history_t, history_yaw, req.setpoint_yaw, history_vy)
        
    
    return {
        "time": history_t,
        "pitch": history_pitch,
        "yaw": history_yaw,
        "sp_pitch": history_sp_p,
        "sp_yaw": history_sp_y,
        "metrics": {
            "pitch": metrics_pitch,
            "yaw": metrics_yaw
        }
    }

@app.get("/api/progress")
def get_progress(task_id: str):
    return {"progress": progress_tracker.get(task_id, 0)}

from pydantic import BaseModel
from typing import List, Any

class ExperimentRun(BaseModel):
    condition: str = ""
    algorithm: str = ""
    params: List[float] = []
    params_large: List[float] | None = None
    disturbances: dict = {}
    metrics: dict = {}
    cost_history: List[float] = []

class ExperimentLog(BaseModel):
    experiment_name: str
    tuning_method: str = ""
    objective_type: str = "default_objective"
    runs: List[ExperimentRun] = []

@app.post("/api/history")
def api_post_history(exp: ExperimentLog):
    # Log whole experiment
    log_history(exp.dict())
    return {"status": "logged"}

@app.get("/api/history")
def api_get_history():
    return {"history": get_history(limit=100)}

@app.delete("/api/history")
def api_clear_history():
    deleted = clear_history()
    return {"status": "cleared", "deleted_count": deleted}

@app.get("/api/history/stats")
def api_history_stats():
    return {"stats": get_stats()}

@app.get("/api/lqr_baseline")
def get_lqr_baseline():
    baseline_params = compute_lqr_pid_baseline()
    return {"baseline_params": baseline_params}

@app.get("/api/mimo_lqr_baseline")
def get_mimo_lqr_baseline():
    baseline_params = compute_mimo_lqr_baseline()
    return {"baseline_params": baseline_params}

@app.get("/api/objective_functions")
def get_objective_functions():
    from objective_functions.registry import registry
    return {"objectives": registry.get_all_info()}

@app.post("/api/tune")
def tune(req: TuneRequest):
    import time
    t0 = time.time()
    
    if req.task_id:
        progress_tracker[req.task_id] = 0
        
    def progress_cb(pct):
        if req.task_id:
            progress_tracker[req.task_id] = pct
            
    if req.algorithm.lower() == "pso":
        checkpoint_results = TuningOptimizers.pso_helicopter(
            req.setpoint_pitch, req.setpoint_yaw, n_particles=20, iters_list=[req.iters],
            t_max=req.t_max, disturbance_config=req.disturbance_config, tuning_profile=req.tuning_profile, objective_type=req.objective_type, progress_callback=progress_cb
        )
    elif req.algorithm.lower() == "ga":
        checkpoint_results = TuningOptimizers.ga_helicopter(
            req.setpoint_pitch, req.setpoint_yaw, pop_size=20, iters_list=[req.iters],
            t_max=req.t_max, disturbance_config=req.disturbance_config, tuning_profile=req.tuning_profile, objective_type=req.objective_type, progress_callback=progress_cb
        )
    else: # bo
        checkpoint_results = TuningOptimizers.bo_helicopter(
            req.setpoint_pitch, req.setpoint_yaw, iters_list=[req.iters],
            t_max=req.t_max, disturbance_config=req.disturbance_config, tuning_profile=req.tuning_profile, objective_type=req.objective_type, progress_callback=progress_cb
        )
    
    res = checkpoint_results[req.iters]
    best_cost = res['best_cost']
    best_pos = res['best_params']
    cost_history = res['cost_history']
    
    t1 = time.time()
    
    if req.task_id:
        progress_tracker[req.task_id] = 100
        

    
    return {
        "best_cost": float(best_cost),
        "best_params": best_pos,
        "cost_history": [float(c) for c in cost_history],
        "time": t1 - t0
    }

@app.post("/api/tune_gs")
def tune_gs(req: TuneRequest):
    import time
    t0 = time.time()
    
    gs_method = 'sigmoid' # Hardcoded to the best method for tuning to save time
    
    if req.task_id:
        progress_tracker[req.task_id] = 0
        
    def progress_cb(pct):
        if req.task_id:
            progress_tracker[req.task_id] = pct
            
    if req.algorithm.lower() == "pso":
        checkpoint_results = TuningOptimizers.pso_helicopter(
            req.setpoint_pitch, req.setpoint_yaw, n_particles=20, iters_list=[req.iters],
            t_max=req.t_max, disturbance_config=req.disturbance_config, gs_method=gs_method, tuning_profile=req.tuning_profile, objective_type=req.objective_type, progress_callback=progress_cb
        )
    elif req.algorithm.lower() == "ga":
        checkpoint_results = TuningOptimizers.ga_helicopter(
            req.setpoint_pitch, req.setpoint_yaw, pop_size=20, iters_list=[req.iters],
            t_max=req.t_max, disturbance_config=req.disturbance_config, gs_method=req.gs_method, tuning_profile=req.tuning_profile, objective_type=req.objective_type, progress_callback=progress_cb
        )
    else: # bo
        checkpoint_results = TuningOptimizers.bo_helicopter(
            req.setpoint_pitch, req.setpoint_yaw, iters_list=[req.iters],
            t_max=req.t_max, disturbance_config=req.disturbance_config, gs_method=req.gs_method, tuning_profile=req.tuning_profile, objective_type=req.objective_type, progress_callback=progress_cb
        )
        
    res = checkpoint_results[req.iters]
    best_cost = res['best_cost']
    best_pos = res['best_params']
    cost_history = res['cost_history']
    
    t1 = time.time()
    
    if req.task_id:
        progress_tracker[req.task_id] = 100
        

    return {
        "best_cost": float(best_cost),
        "best_params": best_pos[:6],
        "best_params_large": best_pos[6:],
        "cost_history": [float(c) for c in cost_history],
        "time": t1 - t0
    }

@app.post("/api/benchmark")
def benchmark(req: BenchmarkRequest):
    if req.algorithm.lower() == "pso":
        best_cost, best_pos, cost_history, pos_history = TuningOptimizers.pso_benchmark(
            n_particles=30, iters=req.iters
        )
        return {
            "best_cost": best_cost,
            "best_params": best_pos,
            "cost_history": cost_history,
            "pos_history": pos_history
        }
    return {"error": "Algorithm not supported for benchmark"}

@app.post("/api/compare_algorithms")
def compare_algorithms(req: CompareRequest):
    results = {}
    
    if req.task_id:
        progress_tracker[req.task_id] = 0
        
    active_algos = [algo for algo in req.iters_dict.keys() if algo.upper() in ["GA", "PSO", "TPE", "CMA-ES", "GWO"]]
    total_runs = len(active_algos)
    completed_runs = 0
    
    def get_progress_cb(completed):
        def cb(pct):
            if req.task_id:
                progress_tracker[req.task_id] = ((completed + pct/100.0) / total_runs) * 100.0
        return cb
    
    for algo, iters_list in req.iters_dict.items():
        if algo.upper() not in ["GA", "PSO", "TPE", "CMA-ES", "GWO"]:
            continue
            
        results[algo.upper()] = {
            "iterations_data": [],
            "best_overall": None
        }
        
        overall_best_cost = float('inf')
        
        t0 = time.time()
        cb = get_progress_cb(completed_runs)
        
        seed_val = req.seed
        
        if algo.upper() == "PSO":
            checkpoint_results = TuningOptimizers.pso_helicopter(
                req.setpoint_pitch, req.setpoint_yaw, n_particles=20, iters_list=iters_list, 
                t_max=req.t_max, disturbance_config=req.disturbance_config, 
                gs_method=req.gs_method, tuning_profile=req.tuning_profile, objective_type=req.objective_type, trajectory_type=req.trajectory_type, progress_callback=cb, seed=seed_val
            )
        elif algo.upper() == "GA":
            checkpoint_results = TuningOptimizers.ga_helicopter(
                req.setpoint_pitch, req.setpoint_yaw, pop_size=20, iters_list=iters_list, 
                t_max=req.t_max, disturbance_config=req.disturbance_config, 
                gs_method=req.gs_method, tuning_profile=req.tuning_profile, objective_type=req.objective_type, trajectory_type=req.trajectory_type, progress_callback=cb, seed=seed_val
            )
        elif algo.upper() == "TPE":
            checkpoint_results = TuningOptimizers.tpe_helicopter(
                req.setpoint_pitch, req.setpoint_yaw, iters_list=iters_list, 
                t_max=req.t_max, disturbance_config=req.disturbance_config, 
                gs_method=req.gs_method, tuning_profile=req.tuning_profile, objective_type=req.objective_type, trajectory_type=req.trajectory_type, progress_callback=cb, seed=seed_val
            )
        elif algo.upper() == "CMA-ES":
            checkpoint_results = TuningOptimizers.cmaes_helicopter(
                req.setpoint_pitch, req.setpoint_yaw, iters_list=iters_list, 
                t_max=req.t_max, disturbance_config=req.disturbance_config, 
                gs_method=req.gs_method, tuning_profile=req.tuning_profile, objective_type=req.objective_type, trajectory_type=req.trajectory_type, progress_callback=cb, seed=seed_val
            )
        elif algo.upper() == "GWO":
            checkpoint_results = TuningOptimizers.gwo_helicopter(
                req.setpoint_pitch, req.setpoint_yaw, pop_size=20, iters_list=iters_list, 
                t_max=req.t_max, disturbance_config=req.disturbance_config, 
                gs_method=req.gs_method, tuning_profile=req.tuning_profile, objective_type=req.objective_type, trajectory_type=req.trajectory_type, progress_callback=cb, seed=seed_val
            )
            
        t1 = time.time()
        
        for num_iters in sorted(iters_list):
            if num_iters not in checkpoint_results: continue
            res = checkpoint_results[num_iters]
            
            run_result = {
                "iters": num_iters,
                "time": t1 - t0, # Time for the total run up to max_iters
                "best_cost": res["best_cost"],
                "cost_history": res["cost_history"],
                "time_history": res.get("time_history", []),
                "best_params": res["best_params"]
            }
            results[algo.upper()]["iterations_data"].append(run_result)
            
            if res["best_cost"] < overall_best_cost:
                overall_best_cost = res["best_cost"]
                results[algo.upper()]["best_overall"] = {
                    "iters": num_iters,
                    "time": t1 - t0,
                    "best_cost": res["best_cost"],
                    "best_params": res["best_params"],
                    "cost_history": res["cost_history"],
                    "time_history": res.get("time_history", [])
                }
                
                
        completed_runs += 1
            
    if req.task_id:
        progress_tracker[req.task_id] = 100
        
    try:
        from visualization.plot_utils import generate_and_save_paper_plots
        from core.experiment_logger import save_experiment_results
        
        generate_and_save_paper_plots(results, req.setpoint_pitch, req.setpoint_yaw, req.t_max, req.disturbance_config, req.gs_method)
        run_dir = save_experiment_results(results, req)
        results["_metadata"] = {"run_dir": run_dir}
    except Exception as e:
        import traceback
        print("Failed to save paper plots:", e)
        traceback.print_exc()
        
    return results

@app.post("/api/test_suite")
def test_suite(req: TestSuiteRequest):
    scenarios = {
        "Normal": {},
        "Wind Disturbance": {"wind_torque_p": 2.0, "wind_torque_y": 1.0},
        "Sensor Noise": {"sensor_noise_std": 0.05},
        "Payload +30%": {"mass_payload": 0.3}
    }
    
    results = {}
    import numpy as np
    for name, conf in scenarios.items():
        env = Helicopter2DOF(disturbance_config=conf)
        controller = DecentralizedPID(req.params, req.setpoint_pitch, req.setpoint_yaw)
            
        dt = 0.002
        steps = int(req.t_max / dt)
        state = [0.0, 0.0, 0.0, 0.0]
        
        history_t = []
        history_pitch = []
        history_yaw = []
        history_sp_p = []
        history_sp_y = []
        history_vp = []
        history_vy = []
        
        for i in range(steps):
            t = i * dt
            
            if req.trajectory_type == 'step':
                sp_p = req.setpoint_pitch
                sp_y = req.setpoint_yaw
            elif req.trajectory_type == 'sine':
                sp_p = req.setpoint_pitch * np.sin(2 * np.pi * 0.25 * t)
                sp_y = req.setpoint_yaw * np.sin(2 * np.pi * 0.25 * t)
            elif req.trajectory_type == 'square':
                sp_p = req.setpoint_pitch if np.sin(2 * np.pi * 0.1 * t) > 0 else -req.setpoint_pitch
                sp_y = req.setpoint_yaw if np.sin(2 * np.pi * 0.1 * t) > 0 else -req.setpoint_yaw
            elif req.trajectory_type == 'multi-step':
                sp_p = req.setpoint_pitch * (min(int(t / 2.5) + 1, 4) / 4.0)
                sp_y = req.setpoint_yaw * (min(int(t / 2.5) + 1, 4) / 4.0)
            else:
                sp_p, sp_y = req.setpoint_pitch, req.setpoint_yaw

            pitch, _, yaw, _ = state
            history_t.append(t)
            history_pitch.append(pitch)
            history_yaw.append(yaw)
            history_sp_p.append(sp_p)
            history_sp_y.append(sp_y)
            
            if req.params_large is not None:
                theta = max(abs(sp_p), abs(sp_y))
                if req.gs_method == 'step':
                    alpha = 1.0 if theta > 0.5 else 0.0
                elif req.gs_method == 'linear':
                    alpha = np.clip((theta - 0.26) / (0.78 - 0.26), 0.0, 1.0)
                elif req.gs_method == 'sigmoid':
                    k = 15.0
                    alpha = 1.0 / (1.0 + np.exp(-k * (theta - 0.52)))
                else:
                    alpha = 0.0
                    
                blended_params = [(1 - alpha) * p1 + alpha * p2 for p1, p2 in zip(req.params, req.params_large)]
                controller.pid_pitch.Kp = blended_params[0]
                controller.pid_pitch.Ki = blended_params[1]
                controller.pid_pitch.Kd = blended_params[2]
                controller.pid_yaw.Kp = blended_params[3]
                controller.pid_yaw.Ki = blended_params[4]
                controller.pid_yaw.Kd = blended_params[5]
                
            v_pitch, v_yaw = controller.compute(pitch, yaw, dt, sp_p, sp_y)
                
            history_vp.append(v_pitch)
            history_vy.append(v_yaw)
            
            state = env.simulate_step(state, v_pitch, v_yaw, dt)
            
        metrics_pitch = calculate_metrics(history_t, history_pitch, req.setpoint_pitch, history_vp)
        metrics_yaw = calculate_metrics(history_t, history_yaw, req.setpoint_yaw, history_vy)
        
        results[name] = {
            "metrics": {
                "pitch": metrics_pitch,
                "yaw": metrics_yaw
            }
        }
    return results

@app.post("/api/robustness_sweep")
def robustness_sweep(req: RobustnessSweepRequest):
    results = {}
    
    base_params = req.params
    large_params = req.params_large
    if len(req.params) == 12:
        base_params = req.params[:6]
        large_params = req.params[6:]
        
    for i in range(req.steps):
        conf = req.base_disturbance_config.copy()
        for k in req.step_increments:
            conf[k] = conf.get(k, 0.0) + i * req.step_increments[k]
            
        env = Helicopter2DOF(disturbance_config=conf)
        
        # Initialize Controller with Gain Scheduling capabilities
        controller = DecentralizedPID(
            base_params, req.setpoint_pitch, req.setpoint_yaw, 
            controller_type=req.controller_type, 
            params_large=large_params, 
            gs_method=req.gs_method
        )
    
        dt = 0.002
        sim_steps = int(req.t_max / dt)
        state = [0.0, 0.0, 0.0, 0.0]
        
        history_t = []
        history_pitch = []
        history_yaw = []
        history_sp_p = []
        history_sp_y = []
        history_vp = []
        history_vy = []
        
        for step_idx in range(sim_steps):
            t = step_idx * dt
            sp_p, sp_y = req.setpoint_pitch, req.setpoint_yaw
            
            if req.trajectory_type == 'step':
                sp_p = req.setpoint_pitch
                sp_y = req.setpoint_yaw
            elif req.trajectory_type == 'sine':
                sp_p = req.setpoint_pitch * np.sin(2 * np.pi * 0.25 * t)
                sp_y = req.setpoint_yaw * np.sin(2 * np.pi * 0.25 * t)
            elif req.trajectory_type == 'square':
                sp_p = req.setpoint_pitch if np.sin(2 * np.pi * 0.1 * t) > 0 else -req.setpoint_pitch
                sp_y = req.setpoint_yaw if np.sin(2 * np.pi * 0.1 * t) > 0 else -req.setpoint_yaw
            
            pitch, _, yaw, _ = state
            
            if req.params_large is not None:
                theta = max(abs(sp_p), abs(sp_y))
                if req.gs_method == 'step': alpha = 1.0 if theta > 0.5 else 0.0
                elif req.gs_method == 'linear': alpha = np.clip((theta - 0.26) / (0.78 - 0.26), 0.0, 1.0)
                elif req.gs_method == 'sigmoid': alpha = 1.0 / (1.0 + np.exp(-15.0 * (theta - 0.52)))
                else: alpha = 0.0
                
                blended_params = [(1 - alpha) * p1 + alpha * p2 for p1, p2 in zip(req.params, req.params_large)]
                controller.pid_pitch.kp = blended_params[0]
                controller.pid_pitch.ki = blended_params[1]
                controller.pid_pitch.kd = blended_params[2]
                controller.pid_yaw.kp = blended_params[3]
                controller.pid_yaw.ki = blended_params[4]
                controller.pid_yaw.kd = blended_params[5]
                
            v_pitch, v_yaw = controller.compute(pitch, yaw, dt, sp_p, sp_y)
            state = env.simulate_step(state, v_pitch, v_yaw, dt)
            
            history_t.append(t)
            history_pitch.append(pitch)
            history_yaw.append(yaw)
            history_sp_p.append(sp_p)
            history_sp_y.append(sp_y)
            history_vp.append(v_pitch)
            history_vy.append(v_yaw)
            
        metrics_pitch = calculate_metrics(history_t, history_pitch, req.setpoint_pitch, history_vp)
        metrics_yaw = calculate_metrics(history_t, history_yaw, req.setpoint_yaw, history_vy)
        
        results[f"Conf {i+1}"] = {
            "config": conf,
            "metrics": {
                "pitch": metrics_pitch,
                "yaw": metrics_yaw
            }
        }
    
    return results

@app.get("/api/baseline")
def get_baseline():
    baseline = compute_lqr_pid_baseline()
    return {"baseline_params": baseline}

@app.websocket("/api/ws/simulate")
async def websocket_simulate(websocket: WebSocket):
    await websocket.accept()
    
    env = Helicopter2DOF()
    state = [0.0, 0.0, 0.0, 0.0]
    controller = DecentralizedPID([30.0, 15.0, 10.0, 40.0, 10.0, 15.0], 0.0, 0.0)
    
    # Shared state between tasks
    sim_config = {
        "params": [30.0, 15.0, 10.0, 40.0, 10.0, 15.0],
        "sp_p": 0.0,
        "sp_y": 0.0,
        "dist": {}
    }

    async def receive_task():
        try:
            while True:
                data = await websocket.receive_text()
                parsed = json.loads(data)
                sim_config["params"] = parsed.get("params", sim_config["params"])
                sim_config["sp_p"] = parsed.get("setpoint_pitch", sim_config["sp_p"])
                sim_config["sp_y"] = parsed.get("setpoint_yaw", sim_config["sp_y"])
                sim_config["dist"] = parsed.get("disturbances", sim_config["dist"])
        except WebSocketDisconnect:
            pass # Normal disconnect
        except Exception as e:
            print(f"WS Receive Error: {e}")
            
    async def physics_task():
        nonlocal state
        dt = 0.033 # ~30 FPS
        try:
            while True:
                env.disturbance_config = sim_config["dist"]
                env.wind_torque_p = float(sim_config["dist"].get("wind_torque_p") or 0.0)
                env.wind_torque_y = float(sim_config["dist"].get("wind_torque_y") or 0.0)
                env.sensor_noise_std = float(sim_config["dist"].get("sensor_noise_std") or 0.0)
                
                payload_ratio = float(sim_config["dist"].get("mass_payload") or 0.0)
                env.J_p = env.J_p_base * (1.0 + payload_ratio)
                env.J_y = env.J_y_base * (1.0 + payload_ratio)
                
                # Update controller params dynamically
                params = sim_config["params"]
                if params and len(params) == 6:
                    controller.pid_pitch.Kp = params[0]
                    controller.pid_pitch.Ki = params[1]
                    controller.pid_pitch.Kd = params[2]
                    controller.pid_yaw.Kp = params[3]
                    controller.pid_yaw.Ki = params[4]
                    controller.pid_yaw.Kd = params[5]
                
                sp_p = float(sim_config.get("sp_p", 0.0))
                sp_y = float(sim_config.get("sp_y", 0.0))
                
                pitch, _, yaw, _ = state
                v_pitch, v_yaw = controller.compute(pitch, yaw, dt, sp_p, sp_y)
                
                state = env.simulate_step(state, v_pitch, v_yaw, dt)
                
                await websocket.send_json({
                    "pitch": float(state[0]),
                    "yaw": float(state[2]),
                    "sp_p": sp_p,
                    "sp_y": sp_y
                })
                
                await asyncio.sleep(dt)
        except WebSocketDisconnect:
            pass # Disconnected while sending
        except asyncio.CancelledError:
            pass # Task cancelled
        except RuntimeError as e:
            if "close" not in str(e).lower() and "closed" not in str(e).lower():
                print(f"Physics Runtime Error: {e}")
        except Exception as e:
            import traceback
            print("Physics task error:")
            traceback.print_exc()

    rx_task = asyncio.create_task(receive_task())
    sim_task = asyncio.create_task(physics_task())
    
    done, pending = await asyncio.wait(
        [rx_task, sim_task],
        return_when=asyncio.FIRST_COMPLETED,
    )
    for task in pending:
        task.cancel()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)



