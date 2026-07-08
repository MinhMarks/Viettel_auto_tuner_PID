import numpy as np
import control

def compute_lqr_pid_baseline():
    """
    Computes a baseline PID tuning using Linear Quadratic Regulator (LQR)
    by linearizing the 2-DOF helicopter equations around theta=0.
    """
    # Physical parameters
    J_p_base = 0.0384
    J_y_base = 0.0432
    
    m = 1.0750
    l_cm = 0.0071
    m_lcm2 = m * (l_cm**2)
    
    J_p = J_p_base + m_lcm2
    J_y = J_y_base + m_lcm2
    
    K_pp = 0.204
    K_yy = 0.072
    K_py = 0.0068
    K_yp = 0.0219
    B_p = 0.8
    B_y = 0.318

    # Linearized A matrix (4x4) for states: [theta, theta_dot, psi, psi_dot]
    # Note: around theta=0, d/dtheta(cos(theta)) = -sin(0) = 0.
    A = np.array([
        [0, 1, 0, 0],
        [0, -B_p/J_p, 0, 0],
        [0, 0, 0, 1],
        [0, 0, 0, -B_y/J_y]
    ])

    # Linearized B matrix (4x2) for inputs: [V_p, V_y]
    B = np.array([
        [0, 0],
        [K_pp/J_p, K_yp/J_p],
        [0, 0],
        [K_py/J_y, K_yy/J_y]
    ])

    # C matrix for outputs we want to integrate: [theta, psi]
    C = np.array([
        [1, 0, 0, 0],
        [0, 0, 1, 0]
    ])

    # Augment A and B with integral states [int_theta, int_psi]
    A_aug = np.zeros((6, 6))
    A_aug[0:4, 0:4] = A
    A_aug[4:6, 0:4] = C

    B_aug = np.zeros((6, 2))
    B_aug[0:4, 0:2] = B

    # Q and R weighting matrices for LQR
    Q = np.diag([200, 10, 200, 10, 500, 500])
    R = np.diag([1, 1])

    # Solve continuous-time algebraic Riccati equation
    K, _, _ = control.lqr(A_aug, B_aug, Q, R)
    
    # We extract the diagonal equivalents for decentralized PID
    Kp_p = K[0, 0]
    Kd_p = K[0, 1]
    Ki_p = K[0, 4]

    Kp_y = K[1, 2]
    Kd_y = K[1, 3]
    Ki_y = K[1, 5]

    return [float(Kp_p), float(Ki_p), float(Kd_p), float(Kp_y), float(Ki_y), float(Kd_y)]

def compute_mimo_lqr_baseline():
    """
    Computes the full MIMO LQR gain matrix (12 parameters) for the 2-DOF helicopter.
    Returns a flattened list of 12 gains: [k11, k12, k13, k14, k15, k16, k21, k22, k23, k24, k25, k26].
    """
    # Physical parameters
    J_p_base = 0.0384
    J_y_base = 0.0432
    
    m = 1.0750
    l_cm = 0.0071
    m_lcm2 = m * (l_cm**2)
    
    J_p = J_p_base + m_lcm2
    J_y = J_y_base + m_lcm2
    
    K_pp = 0.204
    K_yy = 0.072
    K_py = 0.0068
    K_yp = 0.0219
    B_p = 0.8
    B_y = 0.318

    A = np.array([
        [0, 1, 0, 0],
        [0, -B_p/J_p, 0, 0],
        [0, 0, 0, 1],
        [0, 0, 0, -B_y/J_y]
    ])

    B = np.array([
        [0, 0],
        [K_pp/J_p, K_yp/J_p],
        [0, 0],
        [K_py/J_y, K_yy/J_y]
    ])

    C = np.array([
        [1, 0, 0, 0],
        [0, 0, 1, 0]
    ])

    A_aug = np.zeros((6, 6))
    A_aug[0:4, 0:4] = A
    A_aug[4:6, 0:4] = C

    B_aug = np.zeros((6, 2))
    B_aug[0:4, 0:2] = B

    Q = np.diag([200, 10, 200, 10, 500, 500])
    R = np.diag([1, 1])

    K, _, _ = control.lqr(A_aug, B_aug, Q, R)
    
    return [float(k) for k in K.flatten()]

if __name__ == "__main__":
    baseline = compute_lqr_pid_baseline()
    print("Analytical Baseline PID (LQR-derived):")
    print(f"Pitch: Kp={baseline[0]:.4f}, Ki={baseline[1]:.4f}, Kd={baseline[2]:.4f}")
    print(f"Yaw: Kp={baseline[3]:.4f}, Ki={baseline[4]:.4f}, Kd={baseline[5]:.4f}")
