import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Fix path to import core modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from backend.core.helicopter_2dof_env import Helicopter2DOF
from backend.core.controllers import DecentralizedPID, MIMOLQRController

def generate_rejection_plot(config_file_or_dict, output_dir):
    """
    Simulate algorithms against a dynamic disturbance sequence and plot the rejection test.
    Complies with A* Academic Publication Standard.
    """
    if isinstance(config_file_or_dict, dict):
        config = config_file_or_dict
    else:
        import json
        with open(config_file_or_dict, 'r') as f:
            config = json.load(f)

    # Academic Style setup
    try:
        plt.rcParams['font.family'] = 'serif'
    except:
        pass
    
    sns.set_theme(style="white", palette="colorblind")
    
    t_max = config.get('t_max', 30.0)
    dt = 0.002
    steps = int(t_max / dt)
    time_arr = np.linspace(0, t_max, steps)
    
    sp_pitch = config.get('setpoint_pitch', 0.0)
    sp_yaw = config.get('setpoint_yaw', 0.0)
    
    dist_sequence = config.get('disturbance_sequence', [])
    base_dist = config.get('base_disturbance', {})
    
    algorithms = config.get('algorithms', {})
    
    results = {'time': time_arr}
    
    for alg_name, params in algorithms.items():
        env = Helicopter2DOF(disturbance_config=base_dist)
        
        if alg_name == 'MIMO_LQR':
            controller = MIMOLQRController(params, v_limits=(env.V_min, env.V_max))
        else:
            controller = DecentralizedPID(params, sp_pitch, sp_yaw, controller_type='classic')
        
        state = [0.0, 0.0, 0.0, 0.0]
        history_pitch = []
        history_yaw = []
        
        for i in range(steps):
            t = time_arr[i]
            
            # Apply dynamic disturbance
            active_dist = base_dist
            for seq in dist_sequence:
                if seq.get('start', 0) <= t <= seq.get('end', 0):
                    active_dist = seq.get('config', {})
                    break
            env.set_disturbances(active_dist)
            
            pitch, _, yaw, _ = state
            history_pitch.append(pitch * 180.0 / np.pi) # Convert to degrees for plotting
            history_yaw.append(yaw * 180.0 / np.pi)
            
            # Control calculation
            v_pitch, v_yaw = controller.compute(pitch, yaw, dt, sp_pitch, sp_yaw)
            if alg_name == 'MIMO_LQR':
                gravity_ff = env.K_g * np.cos(pitch) / env.K_pp
                v_pitch += gravity_ff
                v_pitch = np.clip(v_pitch, env.V_min, env.V_max)
                
            state = env.simulate_step(state, v_pitch, v_yaw, dt)
            
        results[f"{alg_name}_pitch"] = history_pitch
        results[f"{alg_name}_yaw"] = history_yaw

    # 1. Export Data to CSV
    df = pd.DataFrame(results)
    csv_path = os.path.join(output_dir, "disturbance_rejection_data.csv")
    df.to_csv(csv_path, index=False)
    
    # 2. Generate Plot
    fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    
    line_styles = ['-', '--', '-.', ':']
    
    # Pitch Plot
    ax1 = axes[0]
    ax1.axhline(sp_pitch * 180.0 / np.pi, color='black', linestyle='--', label='Setpoint', alpha=0.7)
    for idx, alg_name in enumerate(algorithms.keys()):
        ls = line_styles[idx % len(line_styles)]
        ax1.plot(time_arr, results[f"{alg_name}_pitch"], label=alg_name, linestyle=ls, linewidth=1.5)
        
    ax1.set_ylabel(r'$\theta$ [deg]', fontsize=14)
    
    # Yaw Plot
    ax2 = axes[1]
    ax2.axhline(sp_yaw * 180.0 / np.pi, color='black', linestyle='--', label='Setpoint', alpha=0.7)
    for idx, alg_name in enumerate(algorithms.keys()):
        ls = line_styles[idx % len(line_styles)]
        ax2.plot(time_arr, results[f"{alg_name}_yaw"], label=alg_name, linestyle=ls, linewidth=1.5)
        
    ax2.set_ylabel(r'$\psi$ [deg]', fontsize=14)
    ax2.set_xlabel('Time [s]', fontsize=14)
    
    # Formatting (Tufte Principle)
    for ax in axes:
        # Spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        # Grid
        ax.grid(True, axis='y', linestyle='--', alpha=0.6, zorder=0)
        ax.tick_params(axis='both', which='major', labelsize=12)
        
        # Highlight Disturbance Zones
        for seq in dist_sequence:
            t_start = seq.get('start', 0)
            t_end = seq.get('end', 0)
            ax.axvspan(t_start, t_end, color='gray', alpha=0.2, lw=0)
            
            # Optional annotation
            mid_t = (t_start + t_end) / 2
            # Annotate below the minimum value
            y_min = ax.get_ylim()[0]
            y_range = ax.get_ylim()[1] - ax.get_ylim()[0]
            ax.annotate('Disturbances', xy=(mid_t, y_min + 0.1 * y_range), xytext=(mid_t, y_min - 0.2 * y_range),
                        ha='center', va='top', arrowprops=dict(facecolor='black', arrowstyle='->'), fontsize=10)

    # Single Legend
    handles, labels = ax1.get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 1.05), ncol=len(labels), fontsize=12, frameon=False)
    
    plt.tight_layout()
    pdf_path = os.path.join(output_dir, "disturbance_rejection_plot.pdf")
    plt.savefig(pdf_path, format='pdf', bbox_inches='tight')
    plt.close()
    
    return {"csv_path": csv_path, "pdf_path": pdf_path}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, required=True, help="Path to JSON config")
    parser.add_argument("--out", type=str, default=".", help="Output directory")
    args = parser.parse_args()
    
    generate_rejection_plot(args.config, args.out)
    print(f"Exported to {args.out}")
