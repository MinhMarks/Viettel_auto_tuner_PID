import numpy as np
from pymoo.core.problem import Problem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
import matplotlib.pyplot as plt

import sys
import os
# Thêm thư mục backend (thư mục cha của thư mục scripts) vào sys.path để import được package 'core'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.helicopter_2dof_env import Helicopter2DOF
from core.pid_controller import DecentralizedPID

# =================================================================
# CẤU HÌNH CÁC TIÊU CHÍ TỐI ƯU
# Bạn có thể chọn 2 hoặc 3 tiêu chí từ danh sách các tiêu chí hỗ trợ sau:
# 1. "ITAE": Sai số bám quỹ đạo toàn cục (Integral of Time-weighted Absolute Error)
# 2. "Energy": Tổng tiêu hao năng lượng của 2 động cơ (Control Effort / Energy)
# 3. "Overshoot": Độ vọt lố lớn nhất trung bình của Pitch và Yaw
# 4. "SSE": Sai số xác lập (Steady State Error) trung bình tại thời điểm cuối
# 5. "Pitch_SSE": Sai số xác lập (Steady State Error) riêng của trục Pitch
# 6. "Yaw_SSE": Sai số xác lập (Steady State Error) riêng của trục Yaw
# =================================================================
SELECTED_OBJECTIVES = ["Pitch_SSE", "Yaw_SSE"] # ["ITAE", "Energy", "Overshoot"] # Thử xóa "Overshoot" để vẽ 2D

class HelicopterMultiObjectiveProblem(Problem):
    def __init__(self):
        # 6 variables (Kp_p, Ki_p, Kd_p, Kp_y, Ki_y, Kd_y)
        # Tự động thay đổi n_obj dựa vào số lượng tiêu chí được chọn
        super().__init__(n_var=6,
                         n_obj=len(SELECTED_OBJECTIVES),
                         n_constr=0,
                         xl=np.array([0.0]*6),
                         xu=np.array([100.0]*6))
        
        self.t_max = 5.0 # Shorter time for demo
        self.dt = 0.002  # Using the new 500Hz sampling rate
        self.setpoint_pitch = 0.436
        self.setpoint_yaw = 0.520
        self.J1_MAX = 300.0
        self.J2_E_MAX = 11520.0
        
        # Cấu hình nhiễu (Disturbances) theo yêu cầu
        self.disturbance_config = {
            "wind_torque_p": 0.01,
            "wind_torque_y": 0.01,
            "sensor_noise_std": 0.005,
            "mass_payload": 0.01
        }
        
    def _evaluate(self, x, out, *args, **kwargs):
        # x is an array of shape (pop_size, n_var)
        pop_size = x.shape[0]
        
        # Ma trận kết quả (số tiêu chí x số cá thể)
        f_matrix = np.zeros((len(SELECTED_OBJECTIVES), pop_size))
        
        for i in range(pop_size):
            params = x[i]
            env = Helicopter2DOF(disturbance_config=self.disturbance_config)
            controller = DecentralizedPID(params, self.setpoint_pitch, self.setpoint_yaw)
            
            steps = int(self.t_max / self.dt)
            state = [0.0, 0.0, 0.0, 0.0]
            
            itae = 0.0
            energy = 0.0
            max_pitch = 0.0
            max_yaw = 0.0
            
            for step_idx in range(steps):
                t = step_idx * self.dt
                pitch, _, yaw, _ = state
                
                error_pitch = abs(self.setpoint_pitch - pitch)
                error_yaw = abs(self.setpoint_yaw - yaw)
                
                itae += t * (error_pitch + error_yaw) * self.dt
                
                if abs(pitch) > max_pitch: max_pitch = abs(pitch)
                if abs(yaw) > max_yaw: max_yaw = abs(yaw)
                
                if abs(pitch) > np.pi or abs(yaw) > np.pi:
                    itae += 10000.0 # Heavy Penalty for crashing/spinning
                    energy += 10000.0
                    max_pitch = 10.0 # Penalty overshoot
                    max_yaw = 10.0
                    break
                    
                v_pitch_raw, v_yaw_raw = controller.compute(pitch, yaw, self.dt, self.setpoint_pitch, self.setpoint_yaw)
                v_pitch = np.clip(v_pitch_raw, env.V_min, env.V_max)
                v_yaw = np.clip(v_yaw_raw, env.V_min, env.V_max)
                
                energy += (v_pitch**2 + v_yaw**2) * self.dt
                
                state = env.simulate_step(state, v_pitch, v_yaw, self.dt)
                
            # Tính toán Overshoot trung bình của Pitch và Yaw
            overshoot_pitch = max(0, max_pitch - self.setpoint_pitch) / self.setpoint_pitch
            overshoot_yaw = max(0, max_yaw - self.setpoint_yaw) / self.setpoint_yaw
            
            # Tính Sai số xác lập (SSE) tại bước cuối cùng
            sse_pitch = abs(self.setpoint_pitch - state[0])
            sse_yaw = abs(self.setpoint_yaw - state[2])
            
            # Gom tất cả kết quả vào dictionary
            metrics = {
                "ITAE": itae / self.J1_MAX,
                "Energy": energy / self.J2_E_MAX,
                "Overshoot": (overshoot_pitch + overshoot_yaw) / 2.0,
                "SSE": (sse_pitch + sse_yaw) / 2.0,
                "Pitch_SSE": sse_pitch,
                "Yaw_SSE": sse_yaw
            }
            
            # Chỉ lấy các tiêu chí được chọn
            for j, obj_name in enumerate(SELECTED_OBJECTIVES):
                f_matrix[j][i] = metrics[obj_name]
            
        out["F"] = np.column_stack(f_matrix)

def run_nsga2_demo():
    print("Starting NSGA-II Demo for 2-DOF Helicopter PID Tuning...")
    problem = HelicopterMultiObjectiveProblem()
    
    # Population of 20
    algorithm = NSGA2(pop_size=50)
    
    # 20 generations for a quick demo
    res = minimize(problem,
                   algorithm,
                   ('n_gen', 50),
                   seed=1,
                   verbose=True)
                   
    print(f"Optimization finished. Found {len(res.F)} non-dominated solutions on the Pareto front.")
    
    n_obj = len(SELECTED_OBJECTIVES)
    
    # In chi tiết các nghiệm
    print("\n--- CHI TIẾT CÁC NGHIỆM TRÊN PARETO FRONT ---")
    for idx, f_vals in enumerate(res.F):
        metrics_str = " | ".join([f"{SELECTED_OBJECTIVES[j]}: {f_vals[j]:.4f}" for j in range(n_obj)])
        print(f"Nghiệm {idx + 1}: {metrics_str}")
    print("--------------------------------------------\n")
    
    if n_obj == 2:
        # Plotting the Pareto Front (2D)
        plt.figure(figsize=(8, 6))
        plt.scatter(res.F[:, 0], res.F[:, 1], s=40, facecolors='none', edgecolors='blue')
        plt.title(f"Pareto Front: {SELECTED_OBJECTIVES[0]} vs {SELECTED_OBJECTIVES[1]} (NSGA-II)")
        plt.xlabel(f"Normalized {SELECTED_OBJECTIVES[0]}")
        plt.ylabel(f"Normalized {SELECTED_OBJECTIVES[1]}")
        plt.grid(True)
        plt.savefig("nsga2_pareto_front_2d.png", dpi=300)
        print("Saved Pareto front plot to nsga2_pareto_front_2d.png")
        
    elif n_obj == 3:
        # Plotting the Pareto Front (3D)
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(res.F[:, 0], res.F[:, 1], res.F[:, 2], s=40, facecolors='none', edgecolors='blue')
        ax.set_title(f"Pareto Front: {SELECTED_OBJECTIVES[0]} vs {SELECTED_OBJECTIVES[1]} vs {SELECTED_OBJECTIVES[2]} (NSGA-II)")
        ax.set_xlabel(f"Normalized {SELECTED_OBJECTIVES[0]}")
        ax.set_ylabel(f"Normalized {SELECTED_OBJECTIVES[1]}")
        ax.set_zlabel(f"Normalized {SELECTED_OBJECTIVES[2]}")
        plt.grid(True)
        plt.savefig("nsga2_pareto_front_3d.png", dpi=300)
        print("Saved Pareto front plot to nsga2_pareto_front_3d.png")
    else:
        print(f"Cannot plot for {n_obj} objectives. Only 2D and 3D are supported.")

if __name__ == "__main__":
    run_nsga2_demo()
