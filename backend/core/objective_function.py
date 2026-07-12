import numpy as np
from core.helicopter_2dof_env import Helicopter2DOF
from core.pid_controller import DecentralizedPID
from core.objective_functions.registry import registry

def evaluate_helicopter(params, setpoint_pitch, setpoint_yaw, t_max=10.0, dt=0.002, disturbance_config=None, trajectory_type='step', params_large=None, gs_method='step', controller_type='classic', tuning_profile='aggressive', objective_type='default_objective'):
    """
    Simulate the 2-DOF Helicopter with given PID params and compute the cost
    using the specified objective function structure from the registry.
    """
    env = Helicopter2DOF(disturbance_config=disturbance_config)
    controller = DecentralizedPID(params, setpoint_pitch, setpoint_yaw, controller_type=controller_type, params_large=params_large, gs_method=gs_method)
    
    obj_func = registry.get_objective(objective_type)
    return obj_func.evaluate(env, controller, t_max, dt, trajectory_type, setpoint_pitch, setpoint_yaw, tuning_profile)

def evaluate_schaffer_f6(params):
    """
    Schaffer F6 benchmark function.
    Args:
        params (list): [x, y] coordinates
    Returns:
        float: Function value
    """
    x, y = params[0], params[1]
    r2 = x**2 + y**2
    numerator = np.sin(np.sqrt(r2))**2 - 0.5
    denominator = (1 + 0.001 * r2)**2
    return 0.5 + numerator / denominator
