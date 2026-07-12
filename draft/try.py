import numpy as np
from mealpy.swarm_based.GWO import OriginalGWO
from mealpy import FloatVar

def obj_func(solution):
    return sum(solution**2)

bounds_min = np.zeros(2)
bounds_max = np.ones(2)

problem = {
    "obj_func": obj_func,
    "bounds": FloatVar(lb=bounds_min.tolist(), ub=bounds_max.tolist()),
    "minmax": "min",
    "verbose": True
}

model = OriginalGWO(epoch=10, pop_size=5)
best_pos, best_fit = model.solve(problem)
print(best_fit)