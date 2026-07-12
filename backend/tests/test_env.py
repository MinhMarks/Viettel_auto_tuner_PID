import numpy as np
import matplotlib.pyplot as plt
from core.helicopter_2dof_env import Helicopter2DOF
from core.pid_controller import DecentralizedPID

def test_simulation():
    env = Helicopter2DOF()
    
    # Example PID params: [Kp_p, Ki_p, Kd_p, Kp_y, Ki_y, Kd_y]
    params = [30.0, 15.0, 10.0, 40.0, 10.0, 15.0]
    setpoint_pitch = np.deg2rad(15)  # target pitch: 15 degrees
    setpoint_yaw = np.deg2rad(30)    # target yaw: 30 degrees
    
    controller = DecentralizedPID(params, setpoint_pitch, setpoint_yaw)
    
    dt = 0.002
    t_max = 10.0
    steps = int(t_max / dt)
    
    state = [0.0, 0.0, 0.0, 0.0]
    
    history_t = []
    history_pitch = []
    history_yaw = []
    
    for i in range(steps):
        t = i * dt
        pitch, pitch_rate, yaw, yaw_rate = state
        
        history_t.append(t)
        history_pitch.append(np.rad2deg(pitch))
        history_yaw.append(np.rad2deg(yaw))
        
        # Compute control
        v_pitch, v_yaw = controller.compute(pitch, yaw, dt)
        
        # Step env
        state = env.simulate_step(state, v_pitch, v_yaw, dt)
        
    plt.figure(figsize=(10, 5))
    plt.plot(history_t, history_pitch, label='Pitch (deg)')
    plt.plot(history_t, history_yaw, label='Yaw (deg)')
    plt.axhline(np.rad2deg(setpoint_pitch), color='blue', linestyle='--', label='SP Pitch')
    plt.axhline(np.rad2deg(setpoint_yaw), color='orange', linestyle='--', label='SP Yaw')
    plt.legend()
    plt.title('2-DOF Helicopter PID Control Test (Manual Tuning)')
    plt.xlabel('Time (s)')
    plt.ylabel('Angle (deg)')
    plt.grid(True)
    plt.savefig('test_plot.png')
    print("Test finished. Plot saved to test_plot.png")
    
if __name__ == '__main__':
    test_simulation()
