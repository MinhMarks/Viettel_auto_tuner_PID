import numpy as np
from fuzzy_logic import FuzzyPID

class PIDController:
    """
    A simple Discrete PID Controller implementation with anti-windup.
    """
    def __init__(self, kp, ki, kd, setpoint=0.0, output_limits=(None, None)):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint
        self.output_limits = output_limits
        
        self._integral = 0.0
        self._prev_error = 0.0

    def reset(self):
        """Reset the internal states (integral and previous error)"""
        self._integral = 0.0
        self._prev_error = 0.0
        
    def compute(self, current_value, dt, dynamic_setpoint=None):
        """
        Calculate the PID output.
        Args:
            current_value (float): The current measured value of the system.
            dt (float): Time step size.
            dynamic_setpoint (float): Optional varying setpoint for trajectory tracking.
        Returns:
            float: Control output.
        """
        if dynamic_setpoint is not None:
            self.setpoint = dynamic_setpoint
            
        error = self.setpoint - current_value
        
        # Proportional
        P = self.kp * error
        
        # Integral
        self._integral += error * dt
        I = self.ki * self._integral
        
        # Derivative
        derivative = (error - self._prev_error) / dt if dt > 0 else 0.0
        D = self.kd * derivative
        
        self._prev_error = error
        
        output = P + I + D
        
        # Output Clamping & Anti-windup
        min_out, max_out = self.output_limits
        if min_out is not None and output < min_out:
            output = min_out
            self._integral -= error * dt  # Anti-windup
        elif max_out is not None and output > max_out:
            output = max_out
            self._integral -= error * dt  # Anti-windup
            
        return output

class DecentralizedPID:
    """
    Contains two PID controllers for the 2-DOF Helicopter:
    One for Pitch, one for Yaw.
    """
    def __init__(self, params, setpoint_pitch=0.0, setpoint_yaw=0.0, v_limits=(-24.0, 24.0), controller_type='classic', params_large=None, gs_method='step'):
        """
        params: list or array of 6 elements: [Kp_p, Ki_p, Kd_p, Kp_y, Ki_y, Kd_y]
        params_large: optional large-angle params for gain scheduling
        gs_method: 'step', 'linear', 'sigmoid'
        controller_type: 'classic', 'model_based', or 'fuzzy'
        """
        self.controller_type = controller_type
        self.params_large = params_large
        self.gs_method = gs_method
        
        # Original params for Fuzzy reset
        self.base_params = params.copy() if hasattr(params, 'copy') else list(params)
        
        if self.controller_type == 'fuzzy':
            # Initialize Fuzzy Controllers for Pitch and Yaw
            # The scaling factors depend on the base gains. 
            # We allow the fuzzy controller to adjust Kp up to +/- 50% of the base Kp.
            self.fuzzy_p = FuzzyPID(kp_scale=abs(params[0])*0.5 if params[0] != 0 else 10.0, 
                                    kd_scale=abs(params[2])*0.5 if params[2] != 0 else 5.0)
            self.fuzzy_y = FuzzyPID(kp_scale=abs(params[3])*0.5 if params[3] != 0 else 10.0, 
                                    kd_scale=abs(params[5])*0.5 if params[5] != 0 else 5.0)
        self.pid_pitch = PIDController(
            kp=params[0], ki=params[1], kd=params[2],
            setpoint=setpoint_pitch, output_limits=v_limits
        )
        self.pid_yaw = PIDController(
            kp=params[3], ki=params[4], kd=params[5],
            setpoint=setpoint_yaw, output_limits=v_limits
        )

    def compute(self, current_pitch, current_yaw, dt, setpoint_pitch=None, setpoint_yaw=None):
        sp_p = setpoint_pitch if setpoint_pitch is not None else self.pid_pitch.setpoint
        sp_y = setpoint_yaw if setpoint_yaw is not None else self.pid_yaw.setpoint
        
        # 1. Advanced Gain Scheduling (if params_large is provided)
        if self.params_large is not None:
            theta = max(abs(sp_p), abs(sp_y))
            
            if self.gs_method == 'step':
                alpha = 1.0 if theta > 0.5 else 0.0
            elif self.gs_method == 'linear':
                alpha = np.clip((theta - 0.26) / (0.78 - 0.26), 0.0, 1.0)
            elif self.gs_method == 'sigmoid':
                k = 15.0
                alpha = 1.0 / (1.0 + np.exp(-k * (theta - 0.52)))
            else:
                alpha = 0.0
                
            blended_params = [(1 - alpha) * p1 + alpha * p2 for p1, p2 in zip(self.base_params, self.params_large)]
            self.pid_pitch.kp = blended_params[0]
            self.pid_pitch.ki = blended_params[1]
            self.pid_pitch.kd = blended_params[2]
            self.pid_yaw.kp = blended_params[3]
            self.pid_yaw.ki = blended_params[4]
            self.pid_yaw.kd = blended_params[5]
            
        # 2. Fuzzy Logic Adaptive Tuning (Delta updates on top of base/scheduled gains)
        if self.controller_type == 'fuzzy':
            e_p = sp_p - current_pitch
            ec_p = (e_p - self.pid_pitch._prev_error) / dt if dt > 0 else 0
            dkp_p, dkd_p = self.fuzzy_p.compute_delta(e_p, ec_p)
            
            e_y = sp_y - current_yaw
            ec_y = (e_y - self.pid_yaw._prev_error) / dt if dt > 0 else 0
            dkp_y, dkd_y = self.fuzzy_y.compute_delta(e_y, ec_y)
            
            base_kp_p = blended_params[0] if self.params_large else self.base_params[0]
            base_kd_p = blended_params[2] if self.params_large else self.base_params[2]
            base_kp_y = blended_params[3] if self.params_large else self.base_params[3]
            base_kd_y = blended_params[5] if self.params_large else self.base_params[5]
            
            self.pid_pitch.kp = base_kp_p + dkp_p
            self.pid_pitch.kd = base_kd_p + dkd_p
            self.pid_yaw.kp = base_kp_y + dkp_y
            self.pid_yaw.kd = base_kd_y + dkd_y
            
        v_pitch = self.pid_pitch.compute(current_pitch, dt, sp_p)
        v_yaw = self.pid_yaw.compute(current_yaw, dt, sp_y)
        
        if self.controller_type == 'model_based':
            # Model-based compensation for gravity
            # v_pitch = v_pitch + (K_g / K_pp) * cos(theta)
            # K_g = 0.326, K_pp = 0.204 -> K_g / K_pp = 1.598
            v_pitch += 1.598 * np.cos(current_pitch)
            
        # Ensure limits are respected after compensation
        v_pitch = np.clip(v_pitch, self.pid_pitch.output_limits[0], self.pid_pitch.output_limits[1])
        v_yaw = np.clip(v_yaw, self.pid_yaw.output_limits[0], self.pid_yaw.output_limits[1])
        
        return v_pitch, v_yaw

    def reset(self):
        self.pid_pitch.reset()
        self.pid_yaw.reset()
