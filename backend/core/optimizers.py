import numpy as np
import pyswarms as ps
import optuna
from concurrent.futures import ProcessPoolExecutor
from core.objective_function import evaluate_helicopter, evaluate_schaffer_f6

def _eval_particle_helicopter(args):
    particle, setpoint_pitch, setpoint_yaw, t_max, disturbance_config, gs_method, tuning_profile, objective_type, trajectory_type = args
    if gs_method:
        return evaluate_helicopter(particle[:6], setpoint_pitch, setpoint_yaw, t_max=t_max, disturbance_config=disturbance_config, params_large=particle[6:], gs_method=gs_method, tuning_profile=tuning_profile, objective_type=objective_type, trajectory_type=trajectory_type)
    else:
        return evaluate_helicopter(particle, setpoint_pitch, setpoint_yaw, t_max=t_max, disturbance_config=disturbance_config, tuning_profile=tuning_profile, objective_type=objective_type, trajectory_type=trajectory_type)

class TuningOptimizers:
    @staticmethod
    def pso_helicopter(setpoint_pitch, setpoint_yaw, n_particles=20, iters_list=None, t_max=10.0, disturbance_config=None, gs_method=None, tuning_profile='balanced', trajectory_type='step', objective_type='default_objective', progress_callback=None, seed=None):
        import time
        import random
        if seed is not None:
            np.random.seed(seed)
            random.seed(seed)
        if iters_list is None: iters_list = [30]
        iters_list = sorted(iters_list)
        max_iters = max(iters_list)
        
        dims = 12 if gs_method else 6
        max_bound = np.full(dims, 100.0)
        min_bound = np.zeros(dims)
        bounds = (min_bound, max_bound)
        
        options = {'c1': 1.5, 'c2': 1.5, 'w': 0.7}
        optimizer = ps.single.GlobalBestPSO(n_particles=n_particles, dimensions=dims, options=options, bounds=bounds)
        
        iteration_counter = [0]
        time_history = []
        start_time = time.time()
        
        def obj_func(swarm):
            args_list = [(particle.tolist(), setpoint_pitch, setpoint_yaw, t_max, disturbance_config, gs_method, tuning_profile, objective_type, trajectory_type) for particle in swarm]
            with ProcessPoolExecutor() as executor:
                costs = list(executor.map(_eval_particle_helicopter, args_list))
                
            if progress_callback:
                iteration_counter[0] += 1
                progress_callback(iteration_counter[0] / max_iters * 100)
            
            time_history.append(time.time() - start_time)
            return np.array(costs)
            
        results_at_checkpoints = {}
        last_iter = 0
        for target_iter in iters_list:
            iters_to_run = target_iter - last_iter
            if iters_to_run > 0:
                best_cost, best_pos = optimizer.optimize(obj_func, iters=iters_to_run)
                last_iter = target_iter
                
            results_at_checkpoints[target_iter] = {
                "best_cost": float(best_cost),
                "best_params": best_pos.tolist(),
                "cost_history": [float(c) for c in optimizer.cost_history],
                "time_history": [float(t) for t in time_history[:target_iter]]
            }
            
        return results_at_checkpoints

    @staticmethod
    def tpe_helicopter(setpoint_pitch, setpoint_yaw, iters_list=None, t_max=10.0, disturbance_config=None, gs_method=None, tuning_profile='balanced', trajectory_type='step', objective_type='default_objective', progress_callback=None, seed=None):
        if seed is not None:
            import random
            np.random.seed(seed)
            random.seed(seed)
        if iters_list is None: iters_list = [50]
        iters_list = sorted(iters_list)
        max_iters = max(iters_list)
        
        dims = 12 if gs_method else 6
        
        def objective(trial):
            params = [trial.suggest_float(f'p{i}', 0.0, 100.0) for i in range(dims)]
            if gs_method:
                cost = evaluate_helicopter(params[:6], setpoint_pitch, setpoint_yaw, t_max=t_max, disturbance_config=disturbance_config, params_large=params[6:], gs_method=gs_method, tuning_profile=tuning_profile, objective_type=objective_type, trajectory_type=trajectory_type)
            else:
                cost = evaluate_helicopter(params, setpoint_pitch, setpoint_yaw, t_max=t_max, disturbance_config=disturbance_config, tuning_profile=tuning_profile, objective_type=objective_type, trajectory_type=trajectory_type)
            
            if progress_callback:
                progress_callback(trial.number / max_iters * 100)
                
            return cost
            
        sampler = optuna.samplers.TPESampler(seed=seed) if seed is not None else optuna.samplers.TPESampler()
        study = optuna.create_study(direction='minimize', sampler=sampler)
        
        results_at_checkpoints = {}
        last_iter = 0
        for target_iter in iters_list:
            iters_to_run = target_iter - last_iter
            if iters_to_run > 0:
                study.optimize(objective, n_trials=iters_to_run, n_jobs=-1)
                last_iter = target_iter
                
            best_trial = study.best_trial
            best_params = [best_trial.params[f'p{i}'] for i in range(dims)]
            
            sorted_trials = sorted(study.trials, key=lambda t: t.number)
            cost_history = []
            time_history = []
            current_best = float('inf')
            
            if len(sorted_trials) > 0 and sorted_trials[0].datetime_start:
                start_time = sorted_trials[0].datetime_start
            else:
                import datetime
                start_time = datetime.datetime.now()
                
            for t in sorted_trials:
                if t.value is not None and t.value < current_best:
                    current_best = t.value
                cost_history.append(current_best)
                if t.datetime_complete:
                    time_history.append((t.datetime_complete - start_time).total_seconds())
                else:
                    time_history.append(len(time_history))
                
            results_at_checkpoints[target_iter] = {
                "best_cost": float(best_trial.value),
                "best_params": best_params,
                "cost_history": [float(c) for c in cost_history[:target_iter]],
                "time_history": [float(t) for t in time_history[:target_iter]]
            }
            
        return results_at_checkpoints

    @staticmethod
    def cmaes_helicopter(setpoint_pitch, setpoint_yaw, iters_list=None, t_max=10.0, disturbance_config=None, gs_method=None, tuning_profile='balanced', trajectory_type='step', objective_type='default_objective', progress_callback=None, seed=None):
        if seed is not None:
            import random
            np.random.seed(seed)
            random.seed(seed)
        if iters_list is None: iters_list = [50]
        iters_list = sorted(iters_list)
        max_iters = max(iters_list)
        
        dims = 12 if gs_method else 6
        
        def objective(trial):
            params = [trial.suggest_float(f'p{i}', 0.0, 100.0) for i in range(dims)]
            if gs_method:
                cost = evaluate_helicopter(params[:6], setpoint_pitch, setpoint_yaw, t_max=t_max, disturbance_config=disturbance_config, params_large=params[6:], gs_method=gs_method, tuning_profile=tuning_profile, objective_type=objective_type, trajectory_type=trajectory_type)
            else:
                cost = evaluate_helicopter(params, setpoint_pitch, setpoint_yaw, t_max=t_max, disturbance_config=disturbance_config, tuning_profile=tuning_profile, objective_type=objective_type, trajectory_type=trajectory_type)
            
            if progress_callback:
                progress_callback(trial.number / max_iters * 100)
                
            return cost
            
        sampler = optuna.samplers.CmaEsSampler(seed=seed) if seed is not None else optuna.samplers.CmaEsSampler()
        study = optuna.create_study(direction='minimize', sampler=sampler)
        
        results_at_checkpoints = {}
        last_iter = 0
        for target_iter in iters_list:
            iters_to_run = target_iter - last_iter
            if iters_to_run > 0:
                study.optimize(objective, n_trials=iters_to_run, n_jobs=-1)
                last_iter = target_iter
                
            best_trial = study.best_trial
            best_params = [best_trial.params[f'p{i}'] for i in range(dims)]
            
            sorted_trials = sorted(study.trials, key=lambda t: t.number)
            cost_history = []
            time_history = []
            current_best = float('inf')
            
            if len(sorted_trials) > 0 and sorted_trials[0].datetime_start:
                start_time = sorted_trials[0].datetime_start
            else:
                import datetime
                start_time = datetime.datetime.now()
                
            for t in sorted_trials:
                if t.value is not None and t.value < current_best:
                    current_best = t.value
                cost_history.append(current_best)
                if t.datetime_complete:
                    time_history.append((t.datetime_complete - start_time).total_seconds())
                else:
                    time_history.append(len(time_history))
                
            results_at_checkpoints[target_iter] = {
                "best_cost": float(best_trial.value),
                "best_params": best_params,
                "cost_history": [float(c) for c in cost_history[:target_iter]],
                "time_history": [float(t) for t in time_history[:target_iter]]
            }
            
        return results_at_checkpoints

    @staticmethod
    def ga_helicopter(setpoint_pitch, setpoint_yaw, pop_size=20, iters_list=None, t_max=10.0, disturbance_config=None, gs_method=None, tuning_profile='balanced', trajectory_type='step', objective_type='default_objective', progress_callback=None, seed=None):
        import numpy as np
        import random
        if seed is not None:
            np.random.seed(seed)
            random.seed(seed)
        if iters_list is None: iters_list = [30]
        iters_list = sorted(iters_list)
        max_iters = max(iters_list)
        
        dims = 12 if gs_method else 6
        bounds_min = np.zeros(dims)
        bounds_max = np.full(dims, 100.0)
        
        population = np.random.uniform(bounds_min, bounds_max, (pop_size, dims))
        
        import time
        cost_history = []
        time_history = []
        best_pos = None
        best_cost = float('inf')
        results_at_checkpoints = {}
        
        start_time = time.time()
        for generation in range(max_iters):
            if progress_callback:
                progress_callback(generation / max_iters * 100)
                
            args_list = [(p.tolist(), setpoint_pitch, setpoint_yaw, t_max, disturbance_config, gs_method, tuning_profile, objective_type, trajectory_type) for p in population]
            with ProcessPoolExecutor() as executor:
                costs = list(executor.map(_eval_particle_helicopter, args_list))
            costs = np.array(costs)
            
            min_cost_idx = np.argmin(costs)
            if costs[min_cost_idx] < best_cost:
                best_cost = costs[min_cost_idx]
                best_pos = population[min_cost_idx].copy()
                
            cost_history.append(best_cost)
            time_history.append(time.time() - start_time)
            
            if (generation + 1) in iters_list:
                results_at_checkpoints[generation + 1] = {
                    "best_cost": float(best_cost),
                    "best_params": best_pos.tolist(),
                    "cost_history": [float(c) for c in cost_history],
                    "time_history": [float(t) for t in time_history]
                }
                
            selected = []
            for _ in range(pop_size):
                idx1, idx2 = np.random.choice(pop_size, 2, replace=False)
                winner = idx1 if costs[idx1] < costs[idx2] else idx2
                selected.append(population[winner])
            selected = np.array(selected)
            
            next_gen = []
            for i in range(0, pop_size, 2):
                p1 = selected[i]
                p2 = selected[(i + 1) % pop_size]
                if np.random.rand() < 0.8:
                    alpha = np.random.rand(dims)
                    c1 = alpha * p1 + (1 - alpha) * p2
                    c2 = alpha * p2 + (1 - alpha) * p1
                else:
                    c1, c2 = p1.copy(), p2.copy()
                next_gen.extend([c1, c2])
            next_gen = np.array(next_gen)
            
            mutation_rate = 0.1
            for i in range(pop_size):
                for j in range(dims):
                    if np.random.rand() < mutation_rate:
                        next_gen[i, j] += np.random.normal(0, 5.0)
            
            population = np.clip(next_gen, bounds_min, bounds_max)
            population[0] = best_pos
            
        return results_at_checkpoints

    @staticmethod
    def pso_benchmark(n_particles=30, iters=50):
        max_bound = np.array([100.0, 100.0])
        min_bound = np.array([-100.0, -100.0])
        bounds = (min_bound, max_bound)
        
        options = {'c1': 1.5, 'c2': 1.5, 'w': 0.7}
        optimizer = ps.single.GlobalBestPSO(n_particles=n_particles, dimensions=2, options=options, bounds=bounds)
        
        def obj_func(swarm):
            costs = []
            for particle in swarm:
                c = evaluate_schaffer_f6(particle)
                costs.append(c)
            return np.array(costs)
            
        best_cost, best_pos = optimizer.optimize(obj_func, iters=iters)
        
        pos_history_list = [pos.tolist() for pos in optimizer.pos_history]
        return best_cost, best_pos.tolist(), optimizer.cost_history, pos_history_list

    @staticmethod
    def gwo_helicopter(setpoint_pitch, setpoint_yaw, pop_size=20, iters_list=None, t_max=10.0, disturbance_config=None, gs_method=None, tuning_profile='balanced', trajectory_type='step', objective_type='default_objective', progress_callback=None, seed=None):
        import numpy as np
        import random
        if seed is not None:
            np.random.seed(seed)
            random.seed(seed)
        from mealpy.swarm_based.GWO import OriginalGWO
        from mealpy import FloatVar
        
        if iters_list is None: iters_list = [30]
        iters_list = sorted(iters_list)
        max_iters = max(iters_list)
        
        dims = 12 if gs_method else 6
        bounds_min = np.zeros(dims)
        bounds_max = np.full(dims, 100.0)
        
        def obj_func(solution):
            if gs_method:
                c = evaluate_helicopter(solution[:6].tolist(), setpoint_pitch, setpoint_yaw, t_max=t_max, disturbance_config=disturbance_config, params_large=solution[6:].tolist(), gs_method=gs_method, tuning_profile=tuning_profile, objective_type=objective_type, trajectory_type=trajectory_type)
            else:
                c = evaluate_helicopter(solution.tolist(), setpoint_pitch, setpoint_yaw, t_max=t_max, disturbance_config=disturbance_config, tuning_profile=tuning_profile, objective_type=objective_type, trajectory_type=trajectory_type)
            return c
            
        problem = {
            "obj_func": obj_func,
            "bounds": FloatVar(lb=bounds_min.tolist(), ub=bounds_max.tolist()),
            "minmax": "min",
            "verbose": False
        }
        
        results_at_checkpoints = {}
        last_iter = 0
        
        import time
        start_time = time.time()
        
        model = OriginalGWO(epoch=max_iters, pop_size=pop_size)
        try:
            best_agent = model.solve(problem, mode="thread", n_workers=-1)
        except Exception:
            best_agent = model.solve(problem)
            
        total_time = time.time() - start_time
            
        best_pos = best_agent.solution
        best_fit = best_agent.target.fitness
        
        history = [float(fit) for fit in model.history.list_global_best_fit]
        
        # Estimate or extract time history
        if hasattr(model.history, 'list_epoch_time') and len(model.history.list_epoch_time) == len(history):
            time_hist = []
            cum = 0.0
            for et in model.history.list_epoch_time:
                cum += et
                time_hist.append(cum)
        else:
            time_per_epoch = total_time / max_iters if max_iters > 0 else 0
            time_hist = [float(time_per_epoch * (i + 1)) for i in range(len(history))]
            
        for target_iter in iters_list:
            if target_iter <= len(history):
                target_cost = history[target_iter - 1]
                results_at_checkpoints[target_iter] = {
                    "best_cost": target_cost,
                    "best_params": best_pos.tolist(),
                    "cost_history": history[:target_iter],
                    "time_history": time_hist[:target_iter]
                }
            else:
                results_at_checkpoints[target_iter] = {
                    "best_cost": float(best_fit),
                    "best_params": best_pos.tolist(),
                    "cost_history": history,
                    "time_history": time_hist
                }
                
        if progress_callback:
            progress_callback(100)
            
        return results_at_checkpoints
