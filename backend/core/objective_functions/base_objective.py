class ObjectiveFunction:
    """
    Base class for all objective functions in the pipeline.
    """
    def __init__(self, name, description):
        self.name = name
        self.description = description
        
    def evaluate(self, env, controller, t_max, dt, trajectory_type, setpoint_pitch, setpoint_yaw, tuning_profile):
        """
        Evaluate the helicopter simulation.
        Must return a single float cost value.
        """
        raise NotImplementedError("evaluate() must be implemented by subclass")
