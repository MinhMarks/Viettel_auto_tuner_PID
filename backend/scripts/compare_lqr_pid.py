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
        controller = DecentralizedPID(params, setpoint_pitch=0.0, setpoint_yaw=0.0, v_limits=(env.V_min, env.V_max))

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

def plot_comparison(lqr_data, pid_data, scenario_name, output_path, sp_label_y="0.0 rad (cố định)"):
    """
    Vẽ biểu đồ 2x2 so sánh LQR và PID cho Pitch và Yaw.
    """
    t = lqr_data["time"]

    fig = plt.figure(figsize=(16, 10))
    fig.patch.set_facecolor('#0d1117')
    gs_layout = gridspec.GridSpec(2, 2, hspace=0.45, wspace=0.3)
    ax_pp = fig.add_subplot(gs_layout[0, 0])
    ax_py = fig.add_subplot(gs_layout[0, 1])
    ax_yp = fig.add_subplot(gs_layout[1, 0])
    ax_yy = fig.add_subplot(gs_layout[1, 1])

    colors = {
        "lqr_line": "#60a5fa",     # Blue
        "pid_line": "#f87171",     # Red
        "sp": "#a3e635",           # Lime
        "grid": "#1f2937",
        "text": "#e5e7eb",
        "bg": "#111827"
    }

    def style_ax(ax, title, xlabel, ylabel):
        ax.set_facecolor(colors["bg"])
        ax.set_title(title, color=colors["text"], fontsize=12, fontweight='bold', pad=10)
        ax.set_xlabel(xlabel, color=colors["text"], fontsize=10)
        ax.set_ylabel(ylabel, color=colors["text"], fontsize=10)
        ax.tick_params(colors=colors["text"])
        ax.spines['bottom'].set_color('#374151')
        ax.spines['top'].set_color('#374151')
        ax.spines['left'].set_color('#374151')
        ax.spines['right'].set_color('#374151')
        ax.grid(True, color=colors["grid"], linewidth=0.5, alpha=0.8)

    # --- Subplot 1: Pitch response ---
    style_ax(ax_pp, "Phản hồi Trục Pitch", "Thời gian (s)", "Góc Pitch (rad)")
    ax_pp.plot(t, lqr_data["sp_pitch"], '--', color=colors["sp"], linewidth=1.5, label='Setpoint')
    ax_pp.plot(t, lqr_data["pitch"], color=colors["lqr_line"], linewidth=2.0, label='LQR (MIMO)')
    ax_pp.plot(t, pid_data["pitch"], color=colors["pid_line"], linewidth=2.0, label='Decentralized PID', alpha=0.9)
    ax_pp.legend(facecolor='#1f2937', edgecolor='#374151', labelcolor=colors["text"], fontsize=9)

    # --- Subplot 2: Yaw response (cross-coupling effect) ---
    style_ax(ax_py, "⚡ Phản hồi Trục Yaw (Nhiễu Chéo)", "Thời gian (s)", "Góc Yaw (rad)")
    ax_py.axhline(0, color=colors["sp"], linewidth=1.5, linestyle='--', label=f'Setpoint Yaw = {sp_label_y}')
    ax_py.plot(t, lqr_data["yaw"], color=colors["lqr_line"], linewidth=2.0, label='LQR (MIMO)')
    ax_py.plot(t, pid_data["yaw"], color=colors["pid_line"], linewidth=2.0, label='Decentralized PID', alpha=0.9)
    ax_py.legend(facecolor='#1f2937', edgecolor='#374151', labelcolor=colors["text"], fontsize=9)

    # --- Subplot 3: Control voltage Pitch ---
    style_ax(ax_yp, "Điện áp điều khiển Pitch (V)", "Thời gian (s)", "Điện áp V_p (V)")
    ax_yp.plot(t, lqr_data["v_pitch"], color=colors["lqr_line"], linewidth=1.5, label='LQR')
    ax_yp.plot(t, pid_data["v_pitch"], color=colors["pid_line"], linewidth=1.5, label='PID', alpha=0.9)
    ax_yp.axhline(24, color='#fbbf24', linestyle=':', linewidth=1, label='±24V Saturation')
    ax_yp.axhline(-24, color='#fbbf24', linestyle=':', linewidth=1)
    ax_yp.legend(facecolor='#1f2937', edgecolor='#374151', labelcolor=colors["text"], fontsize=9)

    # --- Subplot 4: Control voltage Yaw ---
    style_ax(ax_yy, "Điện áp điều khiển Yaw (V)", "Thời gian (s)", "Điện áp V_y (V)")
    ax_yy.plot(t, lqr_data["v_yaw"], color=colors["lqr_line"], linewidth=1.5, label='LQR')
    ax_yy.plot(t, pid_data["v_yaw"], color=colors["pid_line"], linewidth=1.5, label='PID', alpha=0.9)
    ax_yy.axhline(24, color='#fbbf24', linestyle=':', linewidth=1, label='±24V Saturation')
    ax_yy.axhline(-24, color='#fbbf24', linestyle=':', linewidth=1)
    ax_yy.legend(facecolor='#1f2937', edgecolor='#374151', labelcolor=colors["text"], fontsize=9)

    # --- Tính toán và in các chỉ số đánh giá ---
    yaw_arr_lqr = np.array(lqr_data["yaw"])
    yaw_arr_pid = np.array(pid_data["yaw"])
    sp_y_arr = np.array(lqr_data["sp_yaw"])

    lqr_yaw_rmse = np.sqrt(np.mean((yaw_arr_lqr - sp_y_arr) ** 2))
    pid_yaw_rmse = np.sqrt(np.mean((yaw_arr_pid - sp_y_arr) ** 2))
    lqr_yaw_max = np.max(np.abs(yaw_arr_lqr - sp_y_arr))
    pid_yaw_max = np.max(np.abs(yaw_arr_pid - sp_y_arr))

    summary = (
        f"Kịch bản: {scenario_name}\n"
        f"LQR → Yaw RMSE: {lqr_yaw_rmse:.5f} rad | Max Cross-Error: {lqr_yaw_max:.5f} rad\n"
        f"PID → Yaw RMSE: {pid_yaw_rmse:.5f} rad | Max Cross-Error: {pid_yaw_max:.5f} rad\n"
        f"Cải thiện LQR so với PID: {((pid_yaw_rmse - lqr_yaw_rmse)/pid_yaw_rmse*100):.1f}% (RMSE)"
    )

    fig.suptitle(
        f"So sánh LQR (MIMO) vs Decentralized PID\nKịch bản: {scenario_name}",
        color='#a78bfa', fontsize=14, fontweight='bold', y=1.01
    )

    fig.text(0.5, -0.02, summary, ha='center', va='top',
             color='#9ca3af', fontsize=9, fontfamily='monospace',
             bbox=dict(facecolor='#1f2937', edgecolor='#374151', boxstyle='round,pad=0.5'))

    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()
    print(f"  ✓ Đã lưu biểu đồ: {output_path}")
    print(f"\n  {summary}")
    return {
        "lqr_yaw_rmse": float(lqr_yaw_rmse), "pid_yaw_rmse": float(pid_yaw_rmse),
        "lqr_yaw_max_cross_error": float(lqr_yaw_max), "pid_yaw_max_cross_error": float(pid_yaw_max),
        "improvement_percent": float((pid_yaw_rmse - lqr_yaw_rmse) / pid_yaw_rmse * 100) if pid_yaw_rmse > 0 else 0
    }


# ============================================================
#  PHẦN 4: ENTRY POINT
# ============================================================

def run_comparison(
    disturbance_config=None,
    t_max=10.0,
    dt=0.002,
    sp_pitch_step=0.3,
    sp_yaw_fixed=0.0,
    sine_amplitude=0.4,
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
    print("[1/4] Đang tính toán ma trận LQR K...")
    params = compute_mimo_lqr_baseline()
    lqr_data_ctrl = {"params": params}

    print("[2/4] Đang tải thông số Decentralized PID (LQR-Baseline)...")
    pid_params = compute_lqr_pid_baseline()
    pid_data_ctrl = {"params": pid_params}

    results = {}

    # ---- Kịch bản 1: Asymmetric Step ----
    print("\n[3/4] Chạy Kịch bản 1: Asymmetric Step Test...")
    sp_pitch_step_fn = lambda t: sp_pitch_step
    sp_yaw_zero_fn = lambda t: sp_yaw_fixed

    lqr_s1 = run_simulation('lqr', lqr_data_ctrl, disturbance_config, t_max, dt, sp_pitch_step_fn, sp_yaw_zero_fn)
    pid_s1 = run_simulation('pid', pid_data_ctrl, disturbance_config, t_max, dt, sp_pitch_step_fn, sp_yaw_zero_fn)

    out_s1 = os.path.join(output_dir, "scenario1_asymmetric_step.png")
    metrics_s1 = plot_comparison(lqr_s1, pid_s1,
                                  f"Kịch bản 1 – Asymmetric Step (Pitch→{sp_pitch_step:.2f}rad, Yaw→{sp_yaw_fixed:.2f}rad)",
                                  out_s1, sp_label_y=f"{sp_yaw_fixed:.1f} rad")

    # ---- Kịch bản 3: Sine Trajectory Tracking ----
    print("\n[4/4] Chạy Kịch bản 3: Sine Trajectory Tracking...")
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


if __name__ == "__main__":
    run_comparison()
