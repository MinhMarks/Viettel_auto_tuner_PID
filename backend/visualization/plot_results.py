import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import argparse
import sys
import csv

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Thêm đường dẫn tới thư mục backend để import các module core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.analytical_baseline import compute_lqr_pid_baseline, compute_mimo_lqr_baseline
from core.helicopter_2dof_env import Helicopter2DOF
from core.pid_controller import DecentralizedPID, MIMOLQRController
from core.metrics import calculate_metrics

# ==========================================
# CẤU HÌNH TRỰC QUAN HÓA (CONFIGURATION)
# ==========================================
# 1. Thư mục chứa dữ liệu thực nghiệm (VD: "experiment_logs/batch_20260703_064718")
TARGET_RUN_DIR = r"../experiment_logs/batch_20260708_222210"

# 2. Bộ lọc (Để danh sách rỗng [] nếu muốn tự động lấy TẤT CẢ các giá trị có trong file log)
FILTER_ALGORITHMS = ["PSO", "TPE", "CMA-ES", "GWO", "LQR Decentralized", "MIMO LQR"] # VD: ["PSO", "TPE"] hoặc để []
FILTER_OBJECTIVES = ["time_domain_objective"] # VD: ["time_domain_objective"] hoặc để []
# Gợi ý các Profile có sẵn theo từng Objective Function (trong trường hợp bạn muốn chọn riêng):
# - "default_objective": ["balanced", "aggressive", "eco", "safety"]
# - "time_domain_objective": ["balanced", "aggressive", "conservative"]
FILTER_PROFILES = ["aggressive"] # Để trống [] script sẽ tự phân tích và lấy đúng các profile có trong log
FILTER_CONTROLLER_TYPES = ["classic"] # VD: ["classic", "fuzzy"]
FILTER_GS_METHODS = ["step"] # VD: ["step", "None"]
FILTER_CONFIGURATIONS = ["Conf 2"] # VD: ["Conf 1", "Conf 5"]

# 3. Phương thức Gộp nhóm (Aggregation) khi có nhiều cấu hình chạy cùng 1 thuật toán
# Cách tính: Lấy "mean" (Trung bình hiệu năng) hoặc "max" (Trường hợp tồi tệ nhất)
AGGREGATION_METHOD = "max" # Chỉ chấp nhận "mean" hoặc "max"

# 4. Metric để so sánh (Cột trong file CSV)
# Ví dụ: "Pitch_ITAE", "Pitch_Overshoot", "Pitch_RiseTime", "Pitch_CE"
AGGREGATION_METRIC = "Pitch_ITAE"

# ==========================================
# HÀM XỬ LÝ CHÍNH
# ==========================================
def save_csv_safe(df, path):
    try:
        df.to_csv(path, index=False)
    except PermissionError:
        print(f"\n[CẢNH BÁO] Lỗi Permission Denied khi lưu file: {path}")
        print("-> File này có thể đang được mở trong Excel hoặc một phần mềm khác. Vui lòng đóng file đó lại!\n")

def save_latex_table_safe(df, path):
    try:
        df_format = df.copy()
        for col in df_format.columns:
            if pd.api.types.is_numeric_dtype(df_format[col]):
                df_format[col] = df_format[col].apply(lambda x: f"{x:.4f}" if pd.notnull(x) else "-")
        
        cols = "l" + "c" * (len(df.columns) - 1)
        tex = ["\\begin{table}[h]", "\\centering", f"\\begin{{tabular}}{{{cols}}}", "\\toprule"]
        tex.append(" & ".join([str(c).replace("_", "\\_") for c in df_format.columns]) + " \\\\")
        tex.append("\\midrule")
        for _, row in df_format.iterrows():
            tex.append(" & ".join([str(x) for x in row]) + " \\\\")
        tex.append("\\bottomrule")
        tex.append("\\end{tabular}")
        tex.append("\\end{table}")
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write("\n".join(tex))
    except Exception as e:
        print(f"[CẢNH BÁO] Lỗi khi lưu file LaTeX {path}: {e}")

def format_academic_plot(ax):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', linestyle='--', color='#E0E0E0', zorder=0)
    ax.set_axisbelow(True)

def simulate_lqr_for_metrics(sp_pitch, sp_yaw, t_max, dist_cfg, mode='decentralized'):
    env = Helicopter2DOF(disturbance_config=dist_cfg)
    
    if mode == 'mimo':
        params = compute_mimo_lqr_baseline()
        controller = MIMOLQRController(params, sp_pitch, sp_yaw, v_limits=(-24.0, 24.0))
    else:
        params = compute_lqr_pid_baseline()
        controller = DecentralizedPID(params, sp_pitch, sp_yaw, params_large=None, gs_method=None)
        
    state = [0.0, 0.0, 0.0, 0.0]
    time_step = 0.01
    steps = int(t_max / time_step)
    
    t_arr, p_arr, y_arr = [], [], []
    u_p_arr, u_y_arr = [], []
    current_time = 0.0
    
    for _ in range(steps):
        t_arr.append(current_time)
        p_arr.append(state[0])
        y_arr.append(state[2])
        
        u = controller.compute(state[0], state[2], time_step)
        u_p_arr.append(u[0])
        u_y_arr.append(u[1])
        
        state = env.simulate_step(state, u[0], u[1], time_step)
        current_time += time_step
        
    m_pitch = calculate_metrics(t_arr, p_arr, sp_pitch, u_p_arr)
    m_yaw = calculate_metrics(t_arr, y_arr, sp_yaw, u_y_arr)
    return m_pitch, m_yaw

def main():
    if not os.path.exists(TARGET_RUN_DIR):
        print(f"[LỖI] Không tìm thấy thư mục: {TARGET_RUN_DIR}")
        return
        
    print(f"--- Đang phân tích dữ liệu tại: {TARGET_RUN_DIR} ---")
    
    # --- A* ACADEMIC PUBLICATION STYLING ---
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['text.usetex'] = False # Default disabled to prevent crash if no LaTeX environment
    sns.set_palette("colorblind")
    sns.set_style("white") # Pure white background
    
    
    # ---------------------------------------------------------
    # PAIR 1: TỐC ĐỘ HỘI TỤ (CONVERGENCE)
    # ---------------------------------------------------------
    conv_path = os.path.join(TARGET_RUN_DIR, "convergence_history.csv")
    if os.path.exists(conv_path):
        df_conv = pd.read_csv(conv_path)
        # Lọc df_conv (chỉ lấy theo Objective và Profile giống như df_sum)
        if 'Objective_Type' in df_conv.columns and FILTER_OBJECTIVES:
            df_conv = df_conv[df_conv['Objective_Type'].isin(FILTER_OBJECTIVES)]
        if 'Tuning_Profile' in df_conv.columns and FILTER_PROFILES:
            df_conv = df_conv[df_conv['Tuning_Profile'].isin(FILTER_PROFILES)]
            
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Tạo bảng tóm tắt
        summary_rows = []
        
        if not df_conv.empty:
            cost_cols = [col for col in df_conv.columns if "_Cost" in col]
            if cost_cols:
                has_seed = 'Seed' in df_conv.columns
                id_vars = ['Iteration', 'Seed'] if has_seed else ['Iteration']
                
                df_melt = pd.melt(df_conv, id_vars=id_vars, value_vars=cost_cols, var_name='Algorithm', value_name='Cost')
                df_melt['Algorithm'] = df_melt['Algorithm'].str.replace("_Cost", "")
                
                if FILTER_ALGORITHMS:
                    df_melt = df_melt[df_melt['Algorithm'].isin(FILTER_ALGORITHMS)]
                
                markers = ['o', 's', '^', 'D', 'v', 'p', '*', 'X']
                
                # sns.lineplot automatically handles CI shading if multiple seeds exist
                sns.lineplot(data=df_melt, x='Iteration', y='Cost', hue='Algorithm', 
                             style='Algorithm', markers=markers[:df_melt['Algorithm'].nunique()], 
                             dashes=True, errorbar=('ci', 95) if has_seed else None, ax=ax, markersize=6)
                
                # Bảng tóm tắt (Mean cost)
                df_mean = df_melt.groupby('Algorithm')['Cost'].min().reset_index()
                df_mean.rename(columns={'Cost': 'Best Cost (Mean)'}, inplace=True)
                summary_rows = df_mean.to_dict('records')
                        
        ax.set_xlabel("Iteration", fontsize=14)
        ax.set_ylabel("Cost Function Value (Log Scale)", fontsize=14)
        ax.set_yscale('log')
        ax.tick_params(labelsize=12)
        if ax.get_legend():
            ax.legend(title="Algorithm", fontsize=12, title_fontsize=12)
            
        format_academic_plot(ax)
        plt.tight_layout()
        
        # Save Chart & Table
        plt.savefig(os.path.join(TARGET_RUN_DIR, "chart_convergence.pdf"), bbox_inches='tight', dpi=300)
        plt.close()
        
        if summary_rows:
            df_summary = pd.DataFrame(summary_rows)
            save_csv_safe(df_summary, os.path.join(TARGET_RUN_DIR, "table_convergence.csv"))
            save_latex_table_safe(df_summary, os.path.join(TARGET_RUN_DIR, "table_convergence.tex"))
        print("Đã xuất Pair 1: Convergence (Chart + Table)")
        
    # ---------------------------------------------------------
    # PAIR 1b: TỐC ĐỘ HỘI TỤ THEO THỜI GIAN (CONVERGENCE OVER TIME)
    # ---------------------------------------------------------
    if os.path.exists(conv_path):
        fig, ax = plt.subplots(figsize=(10, 6))
        summary_time_rows = []
        has_time_data = False
        
        if not df_conv.empty:
            time_cols = [col for col in df_conv.columns if "_Time" in col]
            cost_cols = [col for col in df_conv.columns if "_Cost" in col]
            if time_cols and cost_cols:
                has_time_data = True
                has_seed = 'Seed' in df_conv.columns
                id_vars = ['Iteration', 'Seed'] if has_seed else ['Iteration']
                
                df_time_melt = pd.melt(df_conv, id_vars=id_vars, value_vars=time_cols, var_name='Algorithm', value_name='Time')
                df_time_melt['Algorithm'] = df_time_melt['Algorithm'].str.replace("_Time", "")
                
                df_cost_melt = pd.melt(df_conv, id_vars=id_vars, value_vars=cost_cols, var_name='Algorithm_Cost', value_name='Cost')
                df_cost_melt['Algorithm'] = df_cost_melt['Algorithm_Cost'].str.replace("_Cost", "")
                
                df_merged = pd.merge(df_time_melt, df_cost_melt, on=id_vars + ['Algorithm'])
                
                if FILTER_ALGORITHMS:
                    df_merged = df_merged[df_merged['Algorithm'].isin(FILTER_ALGORITHMS)]
                
                markers = ['o', 's', '^', 'D', 'v', 'p', '*', 'X']
                
                sns.lineplot(data=df_merged, x='Time', y='Cost', hue='Algorithm', 
                             style='Algorithm', markers=markers[:df_merged['Algorithm'].nunique()], 
                             dashes=True, errorbar=('ci', 95) if has_seed else None, ax=ax, markersize=6)
                
                df_best = df_merged.groupby('Algorithm').agg({'Cost': 'min', 'Time': 'max'}).reset_index()
                df_best.rename(columns={'Cost': 'Best Cost', 'Time': 'Total Time (s)'}, inplace=True)
                summary_time_rows = df_best.to_dict('records')
                        
        if has_time_data:
            ax.set_xlabel("Execution Time (Seconds)", fontsize=14)
            ax.set_ylabel("Cost Function Value (Log Scale)", fontsize=14)
            ax.set_yscale('log')
            ax.tick_params(labelsize=12)
            if ax.get_legend():
                ax.legend(title="Algorithm", fontsize=12, title_fontsize=12)
                
            format_academic_plot(ax)
            plt.tight_layout()
            
            plt.savefig(os.path.join(TARGET_RUN_DIR, "chart_convergence_time.pdf"), bbox_inches='tight', dpi=300)
            plt.close()
            
            if summary_time_rows:
                df_summary_time = pd.DataFrame(summary_time_rows)
                save_csv_safe(df_summary_time, os.path.join(TARGET_RUN_DIR, "table_convergence_time.csv"))
                save_latex_table_safe(df_summary_time, os.path.join(TARGET_RUN_DIR, "table_convergence_time.tex"))
            print("Đã xuất Pair 1b: Convergence over Time (Chart + Table)")
        else:
            plt.close()
            print("Bỏ qua Pair 1b (Không có dữ liệu thời gian trong convergence_history.csv)")
            
    # ---------------------------------------------------------
    # PAIR 2: ĐỘ CỨNG VỮNG (ROBUSTNESS SWEEP)
    # ---------------------------------------------------------
    robust_path = os.path.join(TARGET_RUN_DIR, "robustness_test_results.csv")
    if os.path.exists(robust_path):
        df_rob = pd.read_csv(robust_path)
        
        # --- BỔ SUNG LQR BASELINE CHO ROBUSTNESS ---
        missing_baselines = []
        if "LQR Decentralized" not in df_rob['Algorithm'].values:
            missing_baselines.append("LQR Decentralized")
            
        if "LQR_Baseline" in df_rob['Algorithm'].values:
            df_rob.loc[df_rob['Algorithm'] == "LQR_Baseline", 'Algorithm'] = "LQR Decentralized"
            if "LQR Decentralized" in missing_baselines:
                missing_baselines.remove("LQR Decentralized")
                
        if "MIMO LQR" not in df_rob['Algorithm'].values:
            missing_baselines.append("MIMO LQR")
            
        if missing_baselines and not df_rob.empty:
            print(f"--- Đang mô phỏng {missing_baselines} cho Robustness Sweep ---")
            
            configs = df_rob[['Tuning_Objective', 'Tuning_Profile', 'Tuning_Disturbance', 'Test_Trajectory', 'Configuration', 'Disturbance_Wind_P', 'Disturbance_Wind_Y', 'Disturbance_Sensor_Noise', 'Disturbance_Payload']].drop_duplicates()
            
            lqr_rows = []
            for _, row in configs.iterrows():
                dist_cfg = {
                    'wind_torque_p': row.get('Disturbance_Wind_P', 0.0),
                    'wind_torque_y': row.get('Disturbance_Wind_Y', 0.0),
                    'sensor_noise_std': row.get('Disturbance_Sensor_Noise', 0.0),
                    'mass_payload': row.get('Disturbance_Payload', 1.0)
                }
                sp_pitch = 0.5236
                sp_yaw = 0.5236
                t_max = 10.0
                
                for baseline_name in missing_baselines:
                    mode = 'mimo' if baseline_name == "MIMO LQR" else 'decentralized'
                    m_pitch, m_yaw = simulate_lqr_for_metrics(sp_pitch, sp_yaw, t_max, dist_cfg, mode=mode)
                    
                    new_row = {col: row.get(col) for col in configs.columns}
                    new_row['Algorithm'] = baseline_name
                    new_row['Controller_Type'] = 'classic'
                    new_row['GS_Method'] = 'None'
                    new_row['Pitch_RiseTime'] = m_pitch.get('rise_time')
                    new_row['Pitch_SettlingTime'] = m_pitch.get('settling_time')
                    new_row['Pitch_Overshoot'] = m_pitch.get('overshoot')
                    new_row['Pitch_SSE'] = m_pitch.get('steady_state_error')
                    new_row['Pitch_CE'] = m_pitch.get('control_energy')
                    new_row['Pitch_ITAE'] = m_pitch.get('itae')
                    new_row['Yaw_RiseTime'] = m_yaw.get('rise_time')
                    new_row['Yaw_SettlingTime'] = m_yaw.get('settling_time')
                    new_row['Yaw_Overshoot'] = m_yaw.get('overshoot')
                    new_row['Yaw_SSE'] = m_yaw.get('steady_state_error')
                    new_row['Yaw_CE'] = m_yaw.get('control_energy')
                    new_row['Yaw_ITAE'] = m_yaw.get('itae')
                    
                    lqr_rows.append(new_row)
                
            if lqr_rows:
                df_lqr = pd.DataFrame(lqr_rows)
                df_rob = pd.concat([df_rob, df_lqr], ignore_index=True)
                save_csv_safe(df_rob, robust_path)
        # -------------------------------------------
        
        # Bộ lọc
        if FILTER_ALGORITHMS:
            df_rob = df_rob[df_rob['Algorithm'].isin(FILTER_ALGORITHMS)]
        if FILTER_OBJECTIVES and 'Tuning_Objective' in df_rob.columns:
            df_rob = df_rob[df_rob['Tuning_Objective'].isin(FILTER_OBJECTIVES)]
        if FILTER_PROFILES and 'Tuning_Profile' in df_rob.columns:
            df_rob = df_rob[df_rob['Tuning_Profile'].isin(FILTER_PROFILES)]
        if FILTER_CONTROLLER_TYPES and 'Controller_Type' in df_rob.columns:
            df_rob = df_rob[df_rob['Controller_Type'].isin(FILTER_CONTROLLER_TYPES)]
        
        if not df_rob.empty and AGGREGATION_METRIC in df_rob.columns:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            has_seed = 'Seed' in df_rob.columns
            markers = ['o', 's', '^', 'D', 'v', 'p', '*', 'X']
            
            sns.lineplot(data=df_rob, x="Configuration", y=AGGREGATION_METRIC, hue="Algorithm", 
                         style="Algorithm", markers=markers[:df_rob['Algorithm'].nunique()], 
                         dashes=True, errorbar=('ci', 95) if has_seed else None, ax=ax, markersize=8)
            
            ax.set_xlabel("Disturbance Level (Configurations)", fontsize=14)
            ax.set_ylabel(AGGREGATION_METRIC, fontsize=14)
            ax.tick_params(labelsize=12)
            plt.xticks(rotation=45)
            if ax.get_legend():
                ax.legend(title="Algorithm", fontsize=12, title_fontsize=12)
                
            format_academic_plot(ax)
            plt.tight_layout()
            
            # Save Chart
            plt.savefig(os.path.join(TARGET_RUN_DIR, "chart_robustness.pdf"), bbox_inches='tight', dpi=300)
            plt.close()
            
            # Lấy danh sách các cột Metric có trong dữ liệu (loại bỏ các cột chữ/không liên quan)
            metric_cols = [col for col in df_rob.columns if "Pitch_" in col or "Yaw_" in col]
            
            # Tạo bảng Pivot Table Delta (Conf cuối - Conf 1) cho TẤT CẢ metrics
            conf_list = sorted(df_rob['Configuration'].unique())
            if len(conf_list) >= 2:
                base_conf = conf_list[0]
                max_conf = conf_list[-1]
                
                # Groupby mean đề phòng có nhiều dòng cùng thuật toán ở cùng 1 conf (như nhiều profile)
                df_base = df_rob[df_rob['Configuration'] == base_conf].groupby('Algorithm')[metric_cols].mean()
                df_max = df_rob[df_rob['Configuration'] == max_conf].groupby('Algorithm')[metric_cols].mean()
                df_delta = df_max - df_base
                
                # Thêm hậu tố cho tên cột
                df_base_out = df_base.add_suffix(f'_Base({base_conf})')
                df_max_out = df_max.add_suffix(f'_Worst({max_conf})')
                df_delta_out = df_delta.add_suffix('_Delta')
                
                # Nối tất cả lại
                df_out = pd.concat([df_base_out, df_max_out, df_delta_out], axis=1).reset_index()
                save_csv_safe(df_out, os.path.join(TARGET_RUN_DIR, "table_robustness_delta.csv"))
                save_latex_table_safe(df_out, os.path.join(TARGET_RUN_DIR, "table_robustness_delta.tex"))
            
            # ---------------------------------------------------------
            # BỔ SUNG: XUẤT SUBSET BẢNG THEO FILTER (CHỈ LẤY VÀI CỘT YÊU CẦU)
            # ---------------------------------------------------------
            df_subset = df_rob.copy()
            if FILTER_GS_METHODS and 'GS_Method' in df_subset.columns:
                df_subset = df_subset[df_subset['GS_Method'].isin(FILTER_GS_METHODS)]
            if FILTER_CONFIGURATIONS and 'Configuration' in df_subset.columns:
                df_subset = df_subset[df_subset['Configuration'].isin(FILTER_CONFIGURATIONS)]
            
            # Các cột bạn yêu cầu trích xuất
            desired_columns = [
                'Algorithm', 'Configuration', 'Controller_Type', 'GS_Method',
                'Pitch_ITAE', 'Yaw_ITAE', 
                'Pitch_Overshoot', 'Yaw_Overshoot', 
                'Pitch_CE', 'Yaw_CE', 
                'Pitch_SettlingTime', 'Yaw_SettlingTime'
            ]
            
            # Chỉ lấy các cột có tồn tại trong dữ liệu thực tế
            actual_columns = [col for col in desired_columns if col in df_subset.columns]
            
            if not df_subset.empty and actual_columns:
                df_subset_out = df_subset[actual_columns]
                save_csv_safe(df_subset_out, os.path.join(TARGET_RUN_DIR, "table_robustness_filtered_subset.csv"))
                save_latex_table_safe(df_subset_out, os.path.join(TARGET_RUN_DIR, "table_robustness_filtered_subset.tex"))
                print("Đã xuất Pair 2: Bảng lọc tập con (table_robustness_filtered_subset.csv/.tex)")
            
            print("Đã xuất Pair 2: Robustness Sweep (Chart + Table)")
            
    # ---------------------------------------------------------
    # PAIR 3: TỔNG QUAN KIẾN TRÚC & ĐÁNH ĐỔI (OVERALL & TRADE-OFF)
    # ---------------------------------------------------------
    sum_path = os.path.join(TARGET_RUN_DIR, "experiment_summary.csv")
    if os.path.exists(sum_path):
        df_sum = pd.read_csv(sum_path)
        
        # --- BỔ SUNG LQR BASELINE CHO EXPERIMENT SUMMARY ---
        missing_baselines = []
        if "LQR Decentralized" not in df_sum['Algorithm'].values:
            missing_baselines.append("LQR Decentralized")
            
        if "LQR_Baseline" in df_sum['Algorithm'].values:
            df_sum.loc[df_sum['Algorithm'] == "LQR_Baseline", 'Algorithm'] = "LQR Decentralized"
            if "LQR Decentralized" in missing_baselines:
                missing_baselines.remove("LQR Decentralized")
                
        if "MIMO LQR" not in df_sum['Algorithm'].values:
            missing_baselines.append("MIMO LQR")
            
        if missing_baselines and not df_sum.empty:
            print(f"--- Đang mô phỏng {missing_baselines} cho mẻ thử nghiệm (df_sum) ---")
            
            # Grouping by unique environment configuration
            configs = df_sum[['Objective_Type', 'Tuning_Profile', 'Trajectory_Type', 'T_Max', 'Setpoint_Pitch', 'Setpoint_Yaw', 'Disturbance_Wind_P', 'Disturbance_Wind_Y', 'Disturbance_Sensor_Noise', 'Disturbance_Payload']].drop_duplicates()
            
            lqr_rows = []
            for _, row in configs.iterrows():
                dist_cfg = {
                    'wind_torque_p': row.get('Disturbance_Wind_P', 0.0),
                    'wind_torque_y': row.get('Disturbance_Wind_Y', 0.0),
                    'sensor_noise_std': row.get('Disturbance_Sensor_Noise', 0.0),
                    'mass_payload': row.get('Disturbance_Payload', 1.0)
                }
                sp_pitch = row.get('Setpoint_Pitch', 0.5236)
                sp_yaw = row.get('Setpoint_Yaw', 0.5236)
                t_max = row.get('T_Max', 10.0)
                
                for baseline_name in missing_baselines:
                    mode = 'mimo' if baseline_name == "MIMO LQR" else 'decentralized'
                    m_pitch, m_yaw = simulate_lqr_for_metrics(sp_pitch, sp_yaw, t_max, dist_cfg, mode=mode)
                    
                    new_row = {col: row.get(col) for col in configs.columns}
                    new_row['Algorithm'] = baseline_name
                    new_row['Controller_Type'] = 'classic'
                    new_row['GS_Method'] = 'None'
                    new_row['Pitch_RiseTime'] = m_pitch.get('rise_time')
                    new_row['Pitch_SettlingTime'] = m_pitch.get('settling_time')
                    new_row['Pitch_Overshoot'] = m_pitch.get('overshoot')
                    new_row['Pitch_SSE'] = m_pitch.get('steady_state_error')
                    new_row['Pitch_CE'] = m_pitch.get('control_energy')
                    new_row['Pitch_ITAE'] = m_pitch.get('itae')
                    new_row['Yaw_RiseTime'] = m_yaw.get('rise_time')
                    new_row['Yaw_SettlingTime'] = m_yaw.get('settling_time')
                    new_row['Yaw_Overshoot'] = m_yaw.get('overshoot')
                    new_row['Yaw_SSE'] = m_yaw.get('steady_state_error')
                    new_row['Yaw_CE'] = m_yaw.get('control_energy')
                    new_row['Yaw_ITAE'] = m_yaw.get('itae')
                    
                    lqr_rows.append(new_row)
            
            if lqr_rows:
                df_lqr = pd.DataFrame(lqr_rows)
                df_sum = pd.concat([df_sum, df_lqr], ignore_index=True)
                save_csv_safe(df_sum, sum_path)
        # ---------------------------------------------------
        
        # Áp dụng bộ lọc
        if FILTER_ALGORITHMS:
            df_sum = df_sum[df_sum['Algorithm'].isin(FILTER_ALGORITHMS)]
        if FILTER_OBJECTIVES:
            df_sum = df_sum[df_sum['Objective_Type'].isin(FILTER_OBJECTIVES)]
        if FILTER_PROFILES:
            df_sum = df_sum[df_sum['Tuning_Profile'].isin(FILTER_PROFILES)]
        if FILTER_CONTROLLER_TYPES and 'Controller_Type' in df_sum.columns:
            df_sum = df_sum[df_sum['Controller_Type'].isin(FILTER_CONTROLLER_TYPES)]
        
        if not df_sum.empty and AGGREGATION_METRIC in df_sum.columns:
            # 1. Bar Chart So Sánh Kiến Trúc theo Aggregation Method (Chỉ vẽ 1 biểu đồ)
            has_seed = 'Seed' in df_sum.columns
            df_agg_chart = df_sum.groupby(['Algorithm'])[AGGREGATION_METRIC].agg(['mean', 'max']).reset_index()
            target_col_chart = 'mean' if AGGREGATION_METHOD == 'mean' else 'max'
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Using sns.barplot. If has_seed, we can just pass df_sum to get error bars
            if has_seed:
                # With error bars (computed by seaborn directly on raw data)
                # target_col_chart here implies we want the mean or max over profiles, but with seeds, 
                # we should aggregate normally by seaborn (estimator='mean' or 'max')
                import numpy as np
                estimator = np.max if AGGREGATION_METHOD == 'max' else np.mean
                bp = sns.barplot(data=df_sum, x="Algorithm", y=AGGREGATION_METRIC, hue="Algorithm", 
                            estimator=estimator, errorbar=('ci', 95), capsize=0.1, ax=ax, dodge=False)
            else:
                bp = sns.barplot(data=df_agg_chart, x="Algorithm", y=target_col_chart, hue="Algorithm", dodge=False, ax=ax)
            
            # Apply distinctive hatches
            hatches = ['/', '\\', 'x', '.', '-', '+', 'O', '*']
            for i, patch in enumerate(ax.patches):
                # Cycle through hatches based on the index
                hatch = hatches[i % len(hatches)]
                patch.set_hatch(hatch)
                
            ax.set_ylabel(f'{AGGREGATION_METRIC} ({AGGREGATION_METHOD.upper()})', fontsize=14)
            ax.set_xlabel("Algorithm", fontsize=14)
            ax.tick_params(labelsize=12)
            
            format_academic_plot(ax)
            plt.tight_layout()
            plt.savefig(os.path.join(TARGET_RUN_DIR, "chart_architectures.pdf"), bbox_inches='tight', dpi=300)
            plt.close()
            
            # XUẤT TABLE CHO TẤT CẢ METRICS
            metric_cols_sum = [col for col in df_sum.columns if "Pitch_" in col or "Yaw_" in col]
            if metric_cols_sum:
                df_mean_all = df_sum.groupby('Algorithm')[metric_cols_sum].mean().add_suffix('_Mean')
                df_max_all = df_sum.groupby('Algorithm')[metric_cols_sum].max().add_suffix('_Max')
                df_table_out = pd.concat([df_mean_all, df_max_all], axis=1).reset_index()
                save_csv_safe(df_table_out, os.path.join(TARGET_RUN_DIR, "table_architectures_aggregation.csv"))
                save_latex_table_safe(df_table_out, os.path.join(TARGET_RUN_DIR, "table_architectures_aggregation.tex"))
            
            # 2. Scatter Plot Đánh Đổi (Trade-off) giữa Control Energy và Metric hiện tại
            # Chỉ vẽ nếu metric hiện tại không phải Control Energy
            if 'Pitch_CE' in df_sum.columns and AGGREGATION_METRIC != 'Pitch_CE':
                fig, ax = plt.subplots(figsize=(10, 6))
                
                markers = ['o', 's', '^', 'D', 'v', 'p', '*', 'X']
                sns.scatterplot(
                    data=df_sum, 
                    x='Pitch_CE', 
                    y=AGGREGATION_METRIC, 
                    hue='Algorithm', 
                    style='Tuning_Profile',
                    markers=markers[:df_sum['Tuning_Profile'].nunique()],
                    s=150, alpha=0.8, ax=ax
                )
                
                ax.set_xlabel("Control Energy (Pitch_CE)", fontsize=14)
                ax.set_ylabel(AGGREGATION_METRIC, fontsize=14)
                ax.tick_params(labelsize=12)
                if ax.get_legend():
                    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=12)
                    
                format_academic_plot(ax)
                plt.tight_layout()
                plt.savefig(os.path.join(TARGET_RUN_DIR, "chart_tradeoff.pdf"), bbox_inches='tight', dpi=300)
                plt.close()
                
            print("Đã xuất Pair 3: Architectures & Trade-off (Chart + Table)")
            
    print("--- HOÀN TẤT ---")

if __name__ == "__main__":
    main()
