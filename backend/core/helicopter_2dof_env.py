import numpy as np
from scipy.integrate import solve_ivp

class Helicopter2DOF:
    """
    2-DOF Helicopter Environment for Simulation.
    Simulates Pitch (theta) and Yaw (psi) dynamics including cross-coupling.
    """
    def __init__(self, disturbance_config=None):
        # Physical parameters (Approximate Quanser 2-DOF Helicopter params)
        self.J_p_base = 0.0384   # Moment of inertia about pitch axis (kg*m^2)
        self.J_y_base = 0.0432   # Moment of inertia about yaw axis (kg*m^2)
        
        self.K_pp = 0.204   # Thrust torque constant from pitch motor to pitch axis (N*m/V)
        self.K_yy = 0.072   # Thrust torque constant from yaw motor to yaw axis (N*m/V)
        
        self.K_py = 0.0068  # Cross-torque constant from pitch motor to yaw axis (N*m/V)
        self.K_yp = 0.0219  # Cross-torque constant from yaw motor to pitch axis (N*m/V)
        
        self.B_p = 0.8      # Viscous damping about pitch axis (N*m*s/rad)
        self.B_y = 0.318    # Viscous damping about yaw axis (N*m*s/rad)
        
        self.K_g = 0.326    # Gravity torque constant (N*m)
    
        # Voltage limits
        self.V_max = 24.0
        self.V_min = -24.0

        # Disturbances
        self.disturbance_config = disturbance_config or {}
        self.wind_torque_p = self.disturbance_config.get("wind_torque_p", 0.0)
        self.wind_torque_y = self.disturbance_config.get("wind_torque_y", 0.0)
        self.sensor_noise_std = self.disturbance_config.get("sensor_noise_std", 0.0)
        
        # mass_payload alters the moment of inertia
        # Assuming payload mass increases J proportionally
        payload_ratio = self.disturbance_config.get("mass_payload", 0.0)
        self.J_p = self.J_p_base * (1.0 + payload_ratio)
        self.J_y = self.J_y_base * (1.0 + payload_ratio)

    def dynamics(self, t, state, V_p, V_y):
        """
        Differential equations of the 2-DOF Helicopter.
        state = [theta, theta_dot, psi, psi_dot]
        """
        theta, theta_dot, psi, psi_dot = state
        
        # Clip voltages to physical limits
        if V_p > self.V_max: V_p = self.V_max
        elif V_p < self.V_min: V_p = self.V_min
        
        if V_y > self.V_max: V_y = self.V_max
        elif V_y < self.V_min: V_y = self.V_min

        # Non-linear equations of motion
        # Pitch dynamics: J_p * theta_ddot = -B_p*theta_dot - K_g*cos(theta) + K_pp*V_p + K_yp*V_y + wind_torque_p
        import math
        theta_ddot = (-self.B_p * theta_dot - self.K_g * math.cos(theta) + self.K_pp * V_p + self.K_yp * V_y + self.wind_torque_p) / self.J_p
        
        # Yaw dynamics: J_y * psi_ddot = -B_y*psi_dot + K_py*V_p + K_yy*V_y + wind_torque_y
        psi_ddot = (-self.B_y * psi_dot + self.K_py * V_p + self.K_yy * V_y + self.wind_torque_y) / self.J_y

        return [theta_dot, theta_ddot, psi_dot, psi_ddot]

    def simulate_step(self, current_state, V_p, V_y, dt):
        """
        Simulate the system for a time step dt given constant control inputs V_p and V_y using RK4.
        """
        s0, s1, s2, s3 = current_state
        
        k1_0, k1_1, k1_2, k1_3 = self.dynamics(0, current_state, V_p, V_y)
        
        dt_2 = 0.5 * dt
        k2_0, k2_1, k2_2, k2_3 = self.dynamics(0, [s0 + dt_2*k1_0, s1 + dt_2*k1_1, s2 + dt_2*k1_2, s3 + dt_2*k1_3], V_p, V_y)
        
        k3_0, k3_1, k3_2, k3_3 = self.dynamics(0, [s0 + dt_2*k2_0, s1 + dt_2*k2_1, s2 + dt_2*k2_2, s3 + dt_2*k2_3], V_p, V_y)
        
        k4_0, k4_1, k4_2, k4_3 = self.dynamics(0, [s0 + dt*k3_0, s1 + dt*k3_1, s2 + dt*k3_2, s3 + dt*k3_3], V_p, V_y)
        
        dt_6 = dt / 6.0
        next_state = [
            s0 + dt_6 * (k1_0 + 2*k2_0 + 2*k3_0 + k4_0),
            s1 + dt_6 * (k1_1 + 2*k2_1 + 2*k3_1 + k4_1),
            s2 + dt_6 * (k1_2 + 2*k2_2 + 2*k3_2 + k4_2),
            s3 + dt_6 * (k1_3 + 2*k2_3 + 2*k3_3 + k4_3)
        ]
        
        # Add sensor noise if configured
        if self.sensor_noise_std > 0.0:
            import random
            next_state[0] += random.gauss(0.0, self.sensor_noise_std)
            next_state[1] += random.gauss(0.0, self.sensor_noise_std)
            next_state[2] += random.gauss(0.0, self.sensor_noise_std)
            next_state[3] += random.gauss(0.0, self.sensor_noise_std)
            
        return next_state

# Example usage
if __name__ == "__main__":
    env = Helicopter2DOF()
    state = [0.0, 0.0, 0.0, 0.0] # Initial state: horizontal, at rest
    dt = 0.01
    
    # Apply constant voltages
    V_pitch = 5.0
    V_yaw = 2.0
    
    # Simulate for 100 steps (1 second)
    history = []
    for _ in range(100):
        state = env.simulate_step(state, V_pitch, V_yaw, dt)
        history.append(state)
        
    history = np.array(history)
    print(f"Final Pitch: {history[-1, 0]:.4f} rad, Final Yaw: {history[-1, 2]:.4f} rad")
