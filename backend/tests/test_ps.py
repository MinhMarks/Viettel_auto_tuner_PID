import pyswarms as ps
import numpy as np

def obj_func(swarm):
    costs = []
    for p in swarm:
        costs.append(np.sum(p**2))
    return np.array(costs)

optimizer = ps.single.GlobalBestPSO(n_particles=10, dimensions=2, options={'c1': 1.5, 'c2': 1.5, 'w': 0.7}, bounds=(np.zeros(2), np.ones(2)))

best_cost1, best_pos1 = optimizer.optimize(obj_func, iters=10)
print("After 10:", best_cost1, best_pos1)

best_cost2, best_pos2 = optimizer.optimize(obj_func, iters=10)
print("After 20:", best_cost2, best_pos2)
print("Total cost history length:", len(optimizer.cost_history))
