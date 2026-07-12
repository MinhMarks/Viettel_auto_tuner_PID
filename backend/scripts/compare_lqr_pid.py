"""
compare_lqr_pid.py
------------------
Script so sanh hieu qua chong nhieu cheo (cross-coupling robustness) giua:
  1. True MIMO LQR Controller
  2. Decentralized PID (LQR-Baseline params)

Kich ban 1: Asymmetric Step Test (Pitch=0.5 rad, Yaw=0.0 rad)
Kich ban 3: Sine Trajectory Tracking (Pitch=sin(t), Yaw=0.0)

Chay script nay tu thu muc backend:
  python scripts/compare_lqr_pid.py
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import sys
import os

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# --- Setup path ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.append(BACKEND_DIR)

from core.helicopter_2dof_env import Helicopter2DOF
from core.analytical_baseline import compute_lqr_pid_baseline, compute_mimo_lqr_baseline
from core.pid_controller import DecentralizedPID, MIMOLQRController

# ============================================================
#  HÀM MÔ PHỎNG TỔNG QUÁT
# ============================================================

def run_simulation(controller_type, controller_data, disturbance_config,
                   t_max, dt, sp_pitch_fn, sp_yaw_fn):
    """
    Chạy mô phỏng với các setpoint động (dạng hàm).
    Trả về dict chứa chuỗi thời gian pitch, yaw, setpoint.
    """
    env = Helicopter2DOF(disturbance_config=disturbance_config)
    state = [0.0, 0.0, 0.0, 0.0]
    steps = int(t_max / dt)

    hist_t, hist_pitch, hist_yaw = [], [], []
    hist_sp_p, hist_sp_y = [], []
    hist_vp, hist_vy = [], []

    if controller_type == 'lqr':
        params = controller_data['params']
        controller = MIMOLQRController(params, v_limits=(env.V_min, env.V_max))
    else:  # pid
        params = controller_data['params']
        controller = DecentralizedPID(
            params, 
            setpoint_pitch=0.0, 
            setpoint_yaw=0.0, 
            v_limits=(env.V_min, env.V_max),
            controller_type='model_based',
            gs_method='sigmoid'
        )

    for i in range(steps):
        t = i * dt
        sp_p = sp_pitch_fn(t)
        sp_y = sp_yaw_fn(t)

        pitch, _, yaw, _ = state
        hist_t.append(t)
        hist_pitch.append(pitch)
        hist_yaw.append(yaw)
        hist_sp_p.append(sp_p)
        hist_sp_y.append(sp_y)

        # compute(self, current_pitch, current_yaw, dt, setpoint_pitch=None, setpoint_yaw=None)
        v_p, v_y = controller.compute(pitch, yaw, dt, setpoint_pitch=sp_p, setpoint_yaw=sp_y)

        # LQR MIMO Controller needs gravity compensation as in original compare script
        if controller_type == 'lqr':
            gravity_ff = env.K_g * np.cos(pitch) / env.K_pp
            v_p += gravity_ff
            v_p = np.clip(v_p, env.V_min, env.V_max)

        hist_vp.append(v_p)
        hist_vy.append(v_y)
        state = env.simulate_step(state, v_p, v_y, dt)

    return {
        "time": hist_t, "pitch": hist_pitch, "yaw": hist_yaw,
        "sp_pitch": hist_sp_p, "sp_yaw": hist_sp_y,
        "v_pitch": hist_vp, "v_yaw": hist_vy
    }


# ============================================================
#  PHẦN 3: VẼ BIỂU ĐỒ SO SÁNH
# ============================================================

def plot_comparison(lqr_data, pid_data, scenario_name, output_path, sp_label_y="0.0 rad"):
    """
    Vẽ biểu đồ 2x2 so sánh LQR và PID cho Pitch và Yaw theo tiêu chuẩn học thuật A*.
    """
    t = lqr_data["time"]

    # Thiết lập typography chuẩn LaTeX
    plt.rcParams['font.family'] = 'serif'
    
    # ----------------------------------------------------
    # FIG 1: STATE RESPONSE (Pitch & Yaw)
    # ----------------------------------------------------
    fig_state = plt.figure(figsize=(10, 4))
    fig_state.patch.set_facecolor('white') # Strict white background
    gs_state = gridspec.GridSpec(1, 2, wspace=0.3)
    ax_pp = fig_state.add_subplot(gs_state[0, 0])
    ax_py = fig_state.add_subplot(gs_state[0, 1])

    # Colorblind friendly colors + distinct line styles and markers
    color_lqr = '#1f77b4'  # blue
    style_lqr = '-'
    marker_lqr = 'o'
    
    color_pid = '#d62728'  # red
    style_pid = '-.'
    marker_pid = 's'
    
    color_ref = 'k'        # black
    style_ref = '--'

    # Giảm mật độ marker
    me = max(1, len(t) // 10)

    def style_ax(ax, xlabel, ylabel):
        ax.set_facecolor('white')
        ax.set_xlabel(xlabel, fontsize=14)
        ax.set_ylabel(ylabel, fontsize=14)
        ax.tick_params(axis='both', which='major', labelsize=12)
        
        # Bỏ top, right spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Grid ngang, nhạt, nằm sau data
        ax.grid(axis='y', color='#E0E0E0', linestyle='--', linewidth=1, zorder=0)
        ax.set_axisbelow(True)

    # --- Subplot 1: Pitch response ---
    style_ax(ax_pp, "Time (s)", "Pitch Angle (rad)")
    ax_pp.plot(t, lqr_data["sp_pitch"], linestyle=style_ref, color=color_ref, linewidth=1.5, label='Reference', zorder=1)
    ax_pp.plot(t, lqr_data["pitch"], linestyle=style_lqr, marker=marker_lqr, markevery=me, color=color_lqr, linewidth=2.0, label='MIMO LQR', zorder=2)
    ax_pp.plot(t, pid_data["pitch"], linestyle=style_pid, marker=marker_pid, markevery=me, color=color_pid, linewidth=2.0, label='AI-PID (GWO)', zorder=3)
    ax_pp.legend(fontsize=12, frameon=False, loc='best')

    # --- Subplot 2: Yaw response (cross-coupling effect) ---
    style_ax(ax_py, "Time (s)", "Yaw Angle (rad)")
    ax_py.axhline(0, color=color_ref, linewidth=1.5, linestyle=style_ref, label=f'Reference (Yaw={sp_label_y})', zorder=1)
    ax_py.plot(t, lqr_data["yaw"], linestyle=style_lqr, marker=marker_lqr, markevery=me, color=color_lqr, linewidth=2.0, label='MIMO LQR', zorder=2)
    ax_py.plot(t, pid_data["yaw"], linestyle=style_pid, marker=marker_pid, markevery=me, color=color_pid, linewidth=2.0, label='AI-PID (GWO)', zorder=3)
    ax_py.legend(fontsize=12, frameon=False, loc='best')

    output_path_state_pdf = output_path.replace('.png', '_state.pdf')
    fig_state.savefig(output_path_state_pdf, format='pdf', bbox_inches='tight')
    plt.close(fig_state)

    # ----------------------------------------------------
    # FIG 2: CONTROL INPUT (V_pitch & V_yaw)
    # ----------------------------------------------------
    fig_ctrl = plt.figure(figsize=(10, 4))
    fig_ctrl.patch.set_facecolor('white') # Strict white background
    gs_ctrl = gridspec.GridSpec(1, 2, wspace=0.3)
    ax_yp = fig_ctrl.add_subplot(gs_ctrl[0, 0])
    ax_yy = fig_ctrl.add_subplot(gs_ctrl[0, 1])

    # --- Subplot 3: Control voltage Pitch ---
    style_ax(ax_yp, "Time (s)", "Control Input $V_p$ (V)")
    ax_yp.plot(t, pid_data["v_pitch"], linestyle='-', color=color_pid, linewidth=0.8, alpha=0.6, label='AI-PID (GWO)', zorder=2)
    ax_yp.plot(t, lqr_data["v_pitch"], linestyle=style_lqr, color=color_lqr, linewidth=1.5, label='MIMO LQR', zorder=3)
    ax_yp.axhline(24, color='gray', linestyle=':', linewidth=1.5, label='Saturation $\pm$24V', zorder=1)
    ax_yp.axhline(-24, color='gray', linestyle=':', linewidth=1.5, zorder=1)
    ax_yp.legend(fontsize=12, frameon=False, loc='best')

    # --- Subplot 4: Control voltage Yaw ---
    style_ax(ax_yy, "Time (s)", "Control Input $V_y$ (V)")
    ax_yy.plot(t, pid_data["v_yaw"], linestyle='-', color=color_pid, linewidth=0.8, alpha=0.6, label='AI-PID (GWO)', zorder=2)
    ax_yy.plot(t, lqr_data["v_yaw"], linestyle=style_lqr, color=color_lqr, linewidth=1.5, label='MIMO LQR', zorder=3)
    ax_yy.axhline(24, color='gray', linestyle=':', linewidth=1.5, label='Saturation $\pm$24V', zorder=1)
    ax_yy.axhline(-24, color='gray', linestyle=':', linewidth=1.5, zorder=1)
    ax_yy.legend(fontsize=12, frameon=False, loc='best')

    output_path_ctrl_pdf = output_path.replace('.png', '_control.pdf')
    fig_ctrl.savefig(output_path_ctrl_pdf, format='pdf', bbox_inches='tight')
    plt.close(fig_ctrl)

    # --- Tính toán và in các chỉ số đánh giá ---
    pitch_arr_lqr = np.array(lqr_data["pitch"])
    pitch_arr_pid = np.array(pid_data["pitch"])
    sp_p_arr = np.array(lqr_data["sp_pitch"])
    lqr_pitch_rmse = np.sqrt(np.mean((pitch_arr_lqr - sp_p_arr) ** 2))
    pid_pitch_rmse = np.sqrt(np.mean((pitch_arr_pid - sp_p_arr) ** 2))
    lqr_pitch_max = np.max(np.abs(pitch_arr_lqr - sp_p_arr))
    pid_pitch_max = np.max(np.abs(pitch_arr_pid - sp_p_arr))

    yaw_arr_lqr = np.array(lqr_data["yaw"])
    yaw_arr_pid = np.array(pid_data["yaw"])
    sp_y_arr = np.array(lqr_data["sp_yaw"])
    lqr_yaw_rmse = np.sqrt(np.mean((yaw_arr_lqr - sp_y_arr) ** 2))
    pid_yaw_rmse = np.sqrt(np.mean((yaw_arr_pid - sp_y_arr) ** 2))
    lqr_yaw_max = np.max(np.abs(yaw_arr_lqr - sp_y_arr))
    pid_yaw_max = np.max(np.abs(yaw_arr_pid - sp_y_arr))
    
    print(f"  ✓ Đã lưu biểu đồ: {output_path_state_pdf} và {output_path_ctrl_pdf}")
    print(f"      (Lưu ý Caption tiếng Việt cho bài báo: Tùy chỉnh theo báo cáo thực tế)")
    
    return {
        "lqr_pitch_rmse": float(lqr_pitch_rmse), "pid_pitch_rmse": float(pid_pitch_rmse),
        "lqr_pitch_max_error": float(lqr_pitch_max), "pid_pitch_max_error": float(pid_pitch_max),
        "lqr_yaw_rmse": float(lqr_yaw_rmse), "pid_yaw_rmse": float(pid_yaw_rmse),
        "lqr_yaw_max_cross_error": float(lqr_yaw_max), "pid_yaw_max_cross_error": float(pid_yaw_max)
    }


# ============================================================
#  PHẦN 4: ENTRY POINT
# ============================================================

def run_comparison(
    disturbance_config=None,
    t_max=10.0,
    dt=0.002,
    sp_pitch_step=  0.8727 ,
    sp_yaw_fixed=0.0,
    sine_amplitude= 0.8727 ,
    sine_freq=0.25,
    output_dir=None
):
    """
    Hàm chính: chạy cả 2 kịch bản và trả về kết quả.
    Có thể gọi từ FastAPI endpoint.
    """
    if disturbance_config is None:
        disturbance_config = {
            "wind_torque_p": 0.01, "wind_torque_y": 0.01,
            "sensor_noise_std": 0.005, "mass_payload": 0.01
        }
    if output_dir is None:
        output_dir = SCRIPT_DIR

    print("\n=== BẮT ĐẦU SO SÁNH LQR vs DECENTRALIZED PID ===\n")

    # Xây dựng bộ điều khiển
    print("[1/5] Đang tính toán ma trận LQR K...")
    params = compute_mimo_lqr_baseline()
    lqr_data_ctrl = {"params": params}

    print("[2/5] Đang tải thông số AI-PID (GWO Optimized)...")
    # GWO best params from user input
    pid_params = [98.3466207, 48.8761348, 23.9687184, 58.0128565, 6.81405923, 100]

    pid_data_ctrl = {"params": pid_params}

    results = {}

    # ---- Kịch bản 1: Asymmetric Step ----
    print("\n[3/5] Chạy Kịch bản 1: Asymmetric Step Test...")
    sp_pitch_step_fn = lambda t: sp_pitch_step
    sp_yaw_zero_fn = lambda t: sp_yaw_fixed

    lqr_s1 = run_simulation('lqr', lqr_data_ctrl, disturbance_config, t_max, dt, sp_pitch_step_fn, sp_yaw_zero_fn)
    pid_s1 = run_simulation('pid', pid_data_ctrl, disturbance_config, t_max, dt, sp_pitch_step_fn, sp_yaw_zero_fn)

    out_s1 = os.path.join(output_dir, "scenario1_asymmetric_step.png")
    metrics_s1 = plot_comparison(lqr_s1, pid_s1,
                                  f"Kịch bản 1 – Asymmetric Step (Pitch→{sp_pitch_step:.2f}rad, Yaw→{sp_yaw_fixed:.2f}rad)",
                                  out_s1, sp_label_y=f"{sp_yaw_fixed:.1f} rad")

    # ---- Kịch bản 2: Multi-step Trajectory Tracking ----
    print("\n[4/5] Chạy Kịch bản 2: Multi-step Trajectory Tracking...")
    def sp_multi_step_fn(t):
        if t < t_max * 0.33:
            return sp_pitch_step
        elif t < t_max * 0.66:
            return -sp_pitch_step
        else:
            return 0.0

    lqr_s2 = run_simulation('lqr', lqr_data_ctrl, disturbance_config, t_max, dt, sp_multi_step_fn, sp_yaw_zero_fn)
    pid_s2 = run_simulation('pid', pid_data_ctrl, disturbance_config, t_max, dt, sp_multi_step_fn, sp_yaw_zero_fn)

    out_s2 = os.path.join(output_dir, "scenario2_multi_step.png")
    metrics_s2 = plot_comparison(lqr_s2, pid_s2,
                                  f"Kịch bản 2 – Multi-step Tracking (Pitch: $\pm${sp_pitch_step:.2f}rad, Yaw→{sp_yaw_fixed:.2f}rad)",
                                  out_s2, sp_label_y=f"{sp_yaw_fixed:.1f} rad")

    # ---- Kịch bản 3: Sine Trajectory Tracking ----
    print("\n[5/5] Chạy Kịch bản 3: Sine Trajectory Tracking...")
    sp_sine_fn = lambda t: sine_amplitude * np.sin(2 * np.pi * sine_freq * t)
    sp_yaw_zero_fn2 = lambda t: sp_yaw_fixed

    lqr_s3 = run_simulation('lqr', lqr_data_ctrl, disturbance_config, t_max, dt, sp_sine_fn, sp_yaw_zero_fn2)
    pid_s3 = run_simulation('pid', pid_data_ctrl, disturbance_config, t_max, dt, sp_sine_fn, sp_yaw_zero_fn2)

    out_s3 = os.path.join(output_dir, "scenario3_sine_tracking.png")
    metrics_s3 = plot_comparison(lqr_s3, pid_s3,
                                  f"Kịch bản 3 – Sine Tracking (Pitch={sine_amplitude}×sin(2π×{sine_freq}×t), Yaw→{sp_yaw_fixed:.2f}rad)",
                                  out_s3, sp_label_y=f"{sp_yaw_fixed:.1f} rad (cố định)")

    results = {
        "scenario1": {
            "label": "Asymmetric Step Test",
            "output_image": out_s1,
            "lqr_time": lqr_s1["time"],
            "lqr_pitch": lqr_s1["pitch"],
            "lqr_yaw": lqr_s1["yaw"],
            "lqr_sp_pitch": lqr_s1["sp_pitch"],
            "lqr_sp_yaw": lqr_s1["sp_yaw"],
            "pid_time": pid_s1["time"],
            "pid_pitch": pid_s1["pitch"],
            "pid_yaw": pid_s1["yaw"],
            "pid_sp_pitch": pid_s1["sp_pitch"],
            "pid_sp_yaw": pid_s1["sp_yaw"],
            "metrics": metrics_s1,
        },
        "scenario2": {
            "label": "Multi-step Trajectory Tracking",
            "output_image": out_s2,
            "lqr_time": lqr_s2["time"],
            "lqr_pitch": lqr_s2["pitch"],
            "lqr_yaw": lqr_s2["yaw"],
            "lqr_sp_pitch": lqr_s2["sp_pitch"],
            "lqr_sp_yaw": lqr_s2["sp_yaw"],
            "pid_time": pid_s2["time"],
            "pid_pitch": pid_s2["pitch"],
            "pid_yaw": pid_s2["yaw"],
            "pid_sp_pitch": pid_s2["sp_pitch"],
            "pid_sp_yaw": pid_s2["sp_yaw"],
            "metrics": metrics_s2,
        },
        "scenario3": {
            "label": "Sine Trajectory Tracking",
            "output_image": out_s3,
            "lqr_time": lqr_s3["time"],
            "lqr_pitch": lqr_s3["pitch"],
            "lqr_yaw": lqr_s3["yaw"],
            "lqr_sp_pitch": lqr_s3["sp_pitch"],
            "lqr_sp_yaw": lqr_s3["sp_yaw"],
            "pid_time": pid_s3["time"],
            "pid_pitch": pid_s3["pitch"],
            "pid_yaw": pid_s3["yaw"],
            "pid_sp_pitch": pid_s3["sp_pitch"],
            "pid_sp_yaw": pid_s3["sp_yaw"],
            "metrics": metrics_s3,
        }
    }

    print("\n=== HOÀN THÀNH ===")
    return results


def generate_latex_table(results):
    print("\n\\begin{table}[h]")
    print("\\centering")
    print("\\caption{Comparison of Controller Performance Metrics}")
    print("\\label{tab:performance_metrics}")
    print("\\begin{tabular}{@{}llcccc@{}}")
    print("\\toprule")
    print("\\multirow{2}{*}{Scenario} & \\multirow{2}{*}{Metric} & \\multicolumn{2}{c}{Pitch ($\\theta$)} & \\multicolumn{2}{c}{Yaw ($\\psi$)} \\\\ \\cmidrule(l){3-4} \\cmidrule(l){5-6}")
    print(" & & LQR & AI-PID & LQR & AI-PID \\\\ \\midrule")
    
    for s_key in ["scenario1", "scenario2", "scenario3"]:
        m = results[s_key]["metrics"]
        label = results[s_key]["label"]
        print(f"\\multirow{{2}}{{*}}{{{label}}} & RMSE (rad) & {m['lqr_pitch_rmse']:.4f} & {m['pid_pitch_rmse']:.4f} & {m['lqr_yaw_rmse']:.4f} & {m['pid_yaw_rmse']:.4f} \\\\")
        print(f" & Max Error (rad) & {m['lqr_pitch_max_error']:.4f} & {m['pid_pitch_max_error']:.4f} & {m['lqr_yaw_max_cross_error']:.4f} & {m['pid_yaw_max_cross_error']:.4f} \\\\")
        if s_key in ["scenario1", "scenario2"]:
            print("\\midrule")
            
    print("\\bottomrule")
    print("\\end{tabular}")
    print("\\end{table}\n")

def generate_csv_table(results, filename=None):
    if filename is None:
        filename = os.path.join(SCRIPT_DIR, "comparison_metrics.csv")
    import csv
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Scenario", "Metric", "LQR_Pitch", "AI-PID_Pitch", "LQR_Yaw", "AI-PID_Yaw"])
        for s_key in ["scenario1", "scenario2", "scenario3"]:
            m = results[s_key]["metrics"]
            label = results[s_key]["label"]
            writer.writerow([label, "RMSE (rad)", m['lqr_pitch_rmse'], m['pid_pitch_rmse'], m['lqr_yaw_rmse'], m['pid_yaw_rmse']])
            writer.writerow([label, "Max Error (rad)", m['lqr_pitch_max_error'], m['pid_pitch_max_error'], m['lqr_yaw_max_cross_error'], m['pid_yaw_max_cross_error']])
    print(f"\n  ✓ Đã lưu bảng số liệu CSV: {filename}")

if __name__ == "__main__":
    results = run_comparison()
    generate_latex_table(results)
    generate_csv_table(results)
