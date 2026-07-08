from app.main import compare_algorithms, CompareRequest
import asyncio

req = CompareRequest(
    setpoint_pitch=10.0,
    setpoint_yaw=10.0,
    iters_dict={"GA": [2], "PSO": [2], "TPE": [2], "CMA-ES": [2], "GWO": [2]},
    trajectory_type='step',
    t_max=10.0,
    disturbance_config={},
    gs_method=None,
    controller_type='classic',
    tuning_profile='balanced',
    objective_type='default_objective'
)

res = compare_algorithms(req)
print(res.keys())
