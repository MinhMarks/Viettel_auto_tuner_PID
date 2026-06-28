import numpy as np
import pyswarms as ps
import optuna
from objective_function import evaluate_helicopter, evaluate_schaffer_f6

class TuningOptimizers:
    @staticmethod
    def pso_helicopter(setpoint_pitch, setpoint_yaw, n_particles=20, iters_list=None, t_max=10.0, disturbance_config=None, gs_method=None, tuning_profile='balanced', progress_callback=None):
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
        def obj_func(swarm):
            costs = []
            for particle in swarm:
                if gs_method:
                    c = evaluate_helicopter(particle[:6].tolist(), setpoint_pitch, setpoint_yaw, t_max=t_max, disturbance_config=disturbance_config, params_large=particle[6:].tolist(), gs_method=gs_method, tuning_profile=tuning_profile)
                else:
                    c = evaluate_helicopter(particle.tolist(), setpoint_pitch, setpoint_yaw, t_max=t_max, disturbance_config=disturbance_config, tuning_profile=tuning_profile)
                costs.append(c)
                
            if progress_callback:
                iteration_counter[0] += 1
                progress_callback(iteration_counter[0] / max_iters * 100)
                
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
                "cost_history": [float(c) for c in optimizer.cost_history]
            }
            
        return results_at_checkpoints

    @staticmethod
    def bo_helicopter(setpoint_pitch, setpoint_yaw, iters_list=None, t_max=10.0, disturbance_config=None, gs_method=None, tuning_profile='balanced', progress_callback=None):
        if iters_list is None: iters_list = [50]
        iters_list = sorted(iters_list)
        max_iters = max(iters_list)
        
        cost_history = []
        dims = 12 if gs_method else 6
        
        def objective(trial):
            params = [trial.suggest_float(f'p{i}', 0.0, 100.0) for i in range(dims)]
            if gs_method:
                cost = evaluate_helicopter(params[:6], setpoint_pitch, setpoint_yaw, t_max=t_max, disturbance_config=disturbance_config, params_large=params[6:], gs_method=gs_method, tuning_profile=tuning_profile)
            else:
                cost = evaluate_helicopter(params, setpoint_pitch, setpoint_yaw, t_max=t_max, disturbance_config=disturbance_config, tuning_profile=tuning_profile)
            cost_history.append(cost)
            
            if progress_callback:
                progress_callback(trial.number / max_iters * 100)
                
            return cost
            
        study = optuna.create_study(direction='minimize')
        
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

    @staticmethod
    def ga_helicopter(setpoint_pitch, setpoint_yaw, pop_size=20, iters_list=None, t_max=10.0, disturbance_config=None, gs_method=None, tuning_profile='balanced', progress_callback=None):
        import numpy as np
        if iters_list is None: iters_list = [30]
        iters_list = sorted(iters_list)
        max_iters = max(iters_list)
        
        dims = 12 if gs_method else 6
        bounds_min = np.zeros(dims)
        bounds_max = np.full(dims, 100.0)
        
        population = np.random.uniform(bounds_min, bounds_max, (pop_size, dims))
        
        cost_history = []
        best_pos = None
        best_cost = float('inf')
        results_at_checkpoints = {}
        
        for generation in range(max_iters):
            if progress_callback:
                progress_callback(generation / max_iters * 100)
                
            costs = []
            for i in range(pop_size):
                if gs_method:
                    c = evaluate_helicopter(population[i, :6].tolist(), setpoint_pitch, setpoint_yaw, t_max=t_max, disturbance_config=disturbance_config, params_large=population[i, 6:].tolist(), gs_method=gs_method, tuning_profile=tuning_profile)
                else:
                    c = evaluate_helicopter(population[i].tolist(), setpoint_pitch, setpoint_yaw, t_max=t_max, disturbance_config=disturbance_config, tuning_profile=tuning_profile)
                costs.append(c)
            costs = np.array(costs)
            
            min_cost_idx = np.argmin(costs)
            if costs[min_cost_idx] < best_cost:
                best_cost = costs[min_cost_idx]
                best_pos = population[min_cost_idx].copy()
                
            cost_history.append(best_cost)
            
            if (generation + 1) in iters_list:
                results_at_checkpoints[generation + 1] = {
                    "best_cost": float(best_cost),
                    "best_params": best_pos.tolist(),
                    "cost_history": [float(c) for c in cost_history]
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
        
        # We need pos_history to animate the particles moving on the 3D surface
        # pos_history shape: (iters, n_particles, dimensions)
        pos_history_list = [pos.tolist() for pos in optimizer.pos_history]
        return best_cost, best_pos.tolist(), optimizer.cost_history, pos_history_list
