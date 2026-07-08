import os
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from core.helicopter_2dof_env import Helicopter2DOF
from core.pid_controller import DecentralizedPID

def local_simulate(params, sp_pitch, sp_yaw, t_max, dist_cfg, params_large, gs_method):
    env = Helicopter2DOF(disturbance_config=dist_cfg)
    controller = DecentralizedPID(params[:6], sp_pitch, sp_yaw, params_large=params_large, gs_method=gs_method)
    
    state = [0.0, 0.0, 0.0, 0.0]
    time_step = 0.01
    steps = int(t_max / time_step)
    
    t_arr, p_arr, y_arr = [], [], []
    current_time = 0.0
    
    for _ in range(steps):
        t_arr.append(current_time)
        p_arr.append(state[0])
        y_arr.append(state[2])
        
        u = controller.compute(state[0], state[2], time_step)
        state = env.simulate_step(state, u[0], u[1], time_step)
        current_time += time_step
        
    return np.array(t_arr), np.array(p_arr), np.array(y_arr)

def generate_and_save_paper_plots(results_dict, setpoint_pitch, setpoint_yaw, t_max, dist_cfg, gs_method):
    plt.rcParams.update({
        'font.family': 'serif',
        'font.serif': ['Times New Roman', 'DejaVu Serif'],
        'font.size': 12,
        'axes.labelsize': 14,
        'axes.titlesize': 14,
        'legend.fontsize': 11,
        'xtick.labelsize': 11,
        'ytick.labelsize': 11,
    })
    
    colors = {
        'GA': '#3b82f6',
        'PSO': '#10b981',
        'TPE': '#ec4899',
        'CMA-ES': '#8b5cf6',
        'GWO': '#f59e0b'
    }
    
    fig, axs = plt.subplots(3, 1, figsize=(8, 12))
    
    t_target = [0, t_max]
    axs[0].plot(t_target, [setpoint_pitch, setpoint_pitch], 'k--', label='Target Pitch')
    axs[1].plot(t_target, [setpoint_yaw, setpoint_yaw], 'k--', label='Target Yaw')
    
    for algo, res in results_dict.items():
        if "best_overall" in res and res["best_overall"]:
            best = res["best_overall"]
            # Plot Convergence
            hist = best.get("cost_history", [])
            if hist:
                # Bỏ qua vài iteration đầu có cost quá cao để đồ thị đỡ bị méo scale
                start_idx = 0 if len(hist) < 5 else 3
                iters = np.arange(start_idx + 1, len(hist) + 1)
                axs[2].plot(iters, hist[start_idx:], label=algo, color=colors.get(algo, 'k'), linewidth=2)
                
            # Plot Time Response
            best_params = best["best_params"]
            params_large = best_params[6:] if len(best_params) > 6 else None
            t, p, y = local_simulate(best_params[:6], setpoint_pitch, setpoint_yaw, t_max, dist_cfg, params_large, gs_method)
            
            axs[0].plot(t, p, label=algo, color=colors.get(algo, 'k'), linewidth=1.5)
            axs[1].plot(t, y, label=algo, color=colors.get(algo, 'k'), linewidth=1.5)
            
    axs[0].set_title('Pitch Angle Response')
    axs[0].set_ylabel('Pitch (rad)')
    axs[0].legend(loc='best')
    axs[0].grid(True, linestyle=':', alpha=0.7)
    
    axs[1].set_title('Yaw Angle Response')
    axs[1].set_ylabel('Yaw (rad)')
    axs[1].set_xlabel('Time (s)')
    axs[1].legend(loc='best')
    axs[1].grid(True, linestyle=':', alpha=0.7)
    
    axs[2].set_title('Convergence Curve')
    axs[2].set_ylabel('Objective Cost')
    axs[2].set_xlabel('Iterations')
    axs[2].set_yscale('log')
    axs[2].legend(loc='best')
    axs[2].grid(True, linestyle=':', alpha=0.7)
    
    plt.tight_layout()
    
    # Save to local directory
    plot_dir = os.path.join(os.path.dirname(__file__), 'plots')
    os.makedirs(plot_dir, exist_ok=True)
    
    # Lấy timestamp gọn đẹp
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = os.path.join(plot_dir, f"paper_plot_{timestamp}.png")
    pdf_filename = os.path.join(plot_dir, f"paper_plot_{timestamp}.pdf")
    
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.savefig(pdf_filename, dpi=300, bbox_inches='tight') # Xuất thêm PDF cho Vector format xịn xò
    plt.close()
    
    print(f"Saved paper plots to {plot_dir}")
    return filename
