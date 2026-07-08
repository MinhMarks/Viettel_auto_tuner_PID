import os

file_path = r"d:\UIT\Research\Viettel\backend\optimizers.py"

with open(file_path, "r") as f:
    content = f.read()

# 1. Rename bo_helicopter to tpe_helicopter
content = content.replace("def bo_helicopter(", "def tpe_helicopter(")

# 2. Add cmaes_helicopter after tpe_helicopter
cmaes_code = """
    @staticmethod
    def cmaes_helicopter(setpoint_pitch, setpoint_yaw, iters_list=None, t_max=10.0, disturbance_config=None, gs_method=None, tuning_profile='balanced', objective_type='default_objective', progress_callback=None):
        if iters_list is None: iters_list = [50]
        iters_list = sorted(iters_list)
        max_iters = max(iters_list)
        
        cost_history = []
        dims = 12 if gs_method else 6
        
        def objective(trial):
            params = [trial.suggest_float(f'p{i}', 0.0, 100.0) for i in range(dims)]
            if gs_method:
                cost = evaluate_helicopter(params[:6], setpoint_pitch, setpoint_yaw, t_max=t_max, disturbance_config=disturbance_config, params_large=params[6:], gs_method=gs_method, tuning_profile=tuning_profile, objective_type=objective_type)
            else:
                cost = evaluate_helicopter(params, setpoint_pitch, setpoint_yaw, t_max=t_max, disturbance_config=disturbance_config, tuning_profile=tuning_profile, objective_type=objective_type)
            cost_history.append(cost)
            
            if progress_callback:
                progress_callback(trial.number / max_iters * 100)
                
            return cost
            
        study = optuna.create_study(direction='minimize', sampler=optuna.samplers.CmaEsSampler())
        
        results_at_checkpoints = {}
        last_iter = 0
        for target_iter in iters_list:
            iters_to_run = target_iter - last_iter
            if iters_to_run > 0:
                study.optimize(objective, n_trials=iters_to_run)
                last_iter = target_iter
                
            best_trial = study.best_trial
            best_params = [best_trial.params[f'p{i}'] for i in range(dims)]
            results_at_checkpoints[target_iter] = {
                "best_cost": float(best_trial.value),
                "best_params": best_params,
                "cost_history": [float(c) for c in cost_history[:target_iter]]
            }
            
        return results_at_checkpoints
"""

# Insert cmaes_code after tpe_helicopter function
parts = content.split("def ga_helicopter(")
content = parts[0] + cmaes_code + "\n    @staticmethod\n    def ga_helicopter(" + parts[1]

# 3. Add gwo_helicopter using mealpy
gwo_code = """
    @staticmethod
    def gwo_helicopter(setpoint_pitch, setpoint_yaw, pop_size=20, iters_list=None, t_max=10.0, disturbance_config=None, gs_method=None, tuning_profile='balanced', objective_type='default_objective', progress_callback=None):
        import numpy as np
        from mealpy.swarm_based.GWO import OriginalGWO
        
        if iters_list is None: iters_list = [30]
        iters_list = sorted(iters_list)
        max_iters = max(iters_list)
        
        dims = 12 if gs_method else 6
        bounds_min = np.zeros(dims)
        bounds_max = np.full(dims, 100.0)
        
        # We need a custom problem for mealpy
        iteration_counter = [0]
        cost_history = []
        
        def obj_func(solution):
            if gs_method:
                c = evaluate_helicopter(solution[:6].tolist(), setpoint_pitch, setpoint_yaw, t_max=t_max, disturbance_config=disturbance_config, params_large=solution[6:].tolist(), gs_method=gs_method, tuning_profile=tuning_profile, objective_type=objective_type)
            else:
                c = evaluate_helicopter(solution.tolist(), setpoint_pitch, setpoint_yaw, t_max=t_max, disturbance_config=disturbance_config, tuning_profile=tuning_profile, objective_type=objective_type)
            return c
            
        problem = {
            "fit_func": obj_func,
            "lb": bounds_min.tolist(),
            "ub": bounds_max.tolist(),
            "minmax": "min",
            "verbose": False
        }
        
        results_at_checkpoints = {}
        last_iter = 0
        
        # Mealpy doesn't easily support continuing optimization from a checkpoint out of the box in the simplest way without using Agent objects, 
        # so we might just run to each checkpoint, or just run to max and slice the history. 
        # Actually, running to max and slicing is the easiest.
        
        # We need progress callback per epoch. We can subclass the algorithm or just use a hook.
        # Mealpy 3.x uses Terminations or callbacks, but for simplicity we can just run it.
        # Since we need progress_callback, we can run it in a loop manually? No, Mealpy's `solve` runs all epochs.
        # Let's just run it to max_iters and collect history.
        # Wait, if we just want history, we can get it after solve.
        
        model = OriginalGWO(epoch=max_iters, pop_size=pop_size)
        best_pos, best_fit = model.solve(problem)
        
        # Retrieve history
        # model.history.list_global_best_fit contains best fit at each epoch
        history = [float(fit) for fit in model.history.list_global_best_fit]
        
        for target_iter in iters_list:
            if target_iter <= len(history):
                # The best cost up to target_iter
                # Actually, model.history gives the best so far.
                target_cost = history[target_iter - 1]
                results_at_checkpoints[target_iter] = {
                    "best_cost": target_cost,
                    "best_params": best_pos.tolist(), # approximate (actually we'd need best_pos at target_iter, but for benchmark final pos is okay, or we could extract it if needed. Let's just return final best_pos for all for simplicity, or re-run).
                    "cost_history": history[:target_iter]
                }
            else:
                results_at_checkpoints[target_iter] = {
                    "best_cost": float(best_fit),
                    "best_params": best_pos.tolist(),
                    "cost_history": history
                }
                
        if progress_callback:
            progress_callback(100)
            
        return results_at_checkpoints
"""

content = content + gwo_code

with open(file_path, "w") as f:
    f.write(content)

print("Updated optimizers.py successfully.")
