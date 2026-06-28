import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import numpy as np
from scipy.io import wavfile
import os
import threading
import pygame
import time

# --- CẤU HÌNH GIAO DIỆN HIỆN ĐẠI ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

PRESETS = {
    "Sóng Delta (2 Hz) - Ngủ sâu, phục hồi": 2.0,
    "Sóng Theta (6 Hz) - Thiền định, tiềm thức": 6.0,
    "Sóng Alpha (10 Hz) - Giảm stress, bình tĩnh": 10.0,
    "Sóng Beta (20 Hz) - Tập trung cao độ": 20.0,
    "Sóng Gamma (40 Hz) - Hiệu suất đỉnh cao": 40.0
}

class BrainwaveStudioPro(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Bi's Brainwave Studio Pro v3.0")
        self.geometry("480x620")
        self.resizable(False, False)
        
        # Khởi tạo hệ thống âm thanh Pygame
        pygame.mixer.init()
        
        # Biến trạng thái
        self.current_file = None
        self.is_playing = False
        self.is_paused = False

        # Tiêu đề
        self.title_label = ctk.CTkLabel(self, text="🧠 BI'S BRAINWAVE STUDIO", font=ctk.CTkFont(size=22, weight="bold"))
        self.title_label.pack(pady=(20, 15))

        # Khung chứa các cài đặt
        self.frame = ctk.CTkFrame(self)
        self.frame.pack(pady=10, padx=20, fill="both", expand=True)

        # 1. Preset
        ctk.CTkLabel(self.frame, text="1. Chọn mục tiêu sóng não:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20, pady=(15, 5))
        self.combo_preset = ctk.CTkOptionMenu(self.frame, values=list(PRESETS.keys()), width=380)
        self.combo_preset.set("Sóng Alpha (10 Hz) - Giảm stress, bình tĩnh")
        self.combo_preset.pack(padx=20, pady=(0, 15))

        # 2. Chế độ
        ctk.CTkLabel(self.frame, text="2. Chọn phương pháp phát:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20, pady=(0, 5))
        self.mode_var = ctk.StringVar(value="binaural")
        self.radio_binaural = ctk.CTkRadioButton(self.frame, text="Binaural (Bắt buộc đeo tai nghe)", variable=self.mode_var, value="binaural")
        self.radio_binaural.pack(anchor="w", padx=20, pady=5)
        self.radio_monaural = ctk.CTkRadioButton(self.frame, text="Monaural (Có thể nghe loa ngoài)", variable=self.mode_var, value="monaural")
        self.radio_monaural.pack(anchor="w", padx=20, pady=(0, 15))

        # 3. Tần số nền
        ctk.CTkLabel(self.frame, text="3. Tần số âm nền (Base Hz):", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20, pady=(0, 5))
        self.entry_base = ctk.CTkEntry(self.frame, width=150)
        self.entry_base.insert(0, "432")
        self.entry_base.pack(anchor="w", padx=20, pady=(0, 15))

        # 4. Thời lượng
        ctk.CTkLabel(self.frame, text="4. Thời lượng (Phút):", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20, pady=(0, 5))
        self.entry_duration = ctk.CTkEntry(self.frame, width=150)
        self.entry_duration.insert(0, "15")
        self.entry_duration.pack(anchor="w", padx=20, pady=(0, 20))

        # Nhãn trạng thái
        self.status_label = ctk.CTkLabel(self, text="Sẵn sàng.", text_color="gray", font=ctk.CTkFont(size=13))
        self.status_label.pack(pady=(5, 10))

        # Khu vực nút bấm (Dùng Grid để chia layout đẹp hơn)
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(pady=(0, 20))

        self.btn_generate = ctk.CTkButton(self.btn_frame, text="▶ TẠO VÀ PHÁT NGAY", font=ctk.CTkFont(weight="bold"), height=45, width=420, command=self.start_generation_thread)
        self.btn_generate.grid(row=0, column=0, columnspan=2, pady=(0, 10))

        self.btn_pause = ctk.CTkButton(self.btn_frame, text="⏸ TẠM DỪNG", font=ctk.CTkFont(weight="bold"), fg_color="#f39c12", hover_color="#d68910", height=40, width=205, state="disabled", command=self.toggle_pause)
        self.btn_pause.grid(row=1, column=0, padx=(0, 5))

        self.btn_stop = ctk.CTkButton(self.btn_frame, text="⏹ DỪNG & XÓA FILE", font=ctk.CTkFont(weight="bold"), fg_color="#c0392b", hover_color="#e74c3c", height=40, width=205, state="disabled", command=self.stop_and_delete)
        self.btn_stop.grid(row=1, column=1, padx=(5, 0))

    def start_generation_thread(self):
        # Dọn dẹp file cũ nếu có trước khi tạo file mới
        self.stop_and_delete()
        
        self.btn_generate.configure(state="disabled", text="⏳ ĐANG TÍNH TOÁN...")
        self.status_label.configure(text="Đang xử lý sóng âm...", text_color="#f1c40f")
        threading.Thread(target=self.generate_and_play, daemon=True).start()

    def generate_and_play(self):
        try:
            preset_name = self.combo_preset.get()
            target_hz = PRESETS[preset_name]
            base_hz = float(self.entry_base.get())
            duration_mins = float(self.entry_duration.get())
            mode = self.mode_var.get()
            
            sample_rate = 44100
            duration_secs = int(duration_mins * 60)
            t = np.linspace(0, duration_secs, sample_rate * duration_secs, endpoint=False)
            
            f_left = base_hz
            f_right = base_hz + target_hz
            
            wave_left = np.sin(2 * np.pi * f_left * t)
            wave_right = np.sin(2 * np.pi * f_right * t)
            
            if mode == "binaural":
                audio_stereo = np.vstack((wave_left, wave_right)).T
                prefix = "Binaural"
            else:
                mixed_wave = (wave_left + wave_right) / 2
                audio_stereo = np.vstack((mixed_wave, mixed_wave)).T
                prefix = "Monaural"
                
            audio_stereo = (audio_stereo * 32767).astype(np.int16)
            wave_type = preset_name.split(" ")[1]
            self.current_file = f"{prefix}_{wave_type}_{int(target_hz)}Hz.wav"
            
            wavfile.write(self.current_file, sample_rate, audio_stereo)
            
            # Tải file vào hệ thống Pygame và phát
            pygame.mixer.music.load(self.current_file)
            pygame.mixer.music.play()
            
            self.is_playing = True
            self.is_paused = False
            
            # Cập nhật UI
            self.status_label.configure(text=f"🎶 Đang phát: {self.current_file}", text_color="#2ecc71")
            self.btn_pause.configure(state="normal", text="⏸ TẠM DỪNG")
            self.btn_stop.configure(state="normal")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {e}")
            self.status_label.configure(text="Sẵn sàng.", text_color="gray")
        finally:
            self.btn_generate.configure(state="normal", text="▶ TẠO VÀ PHÁT NGAY")

    def toggle_pause(self):
        if not self.is_playing: return
        
        if self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
            self.btn_pause.configure(text="⏸ TẠM DỪNG")
            self.status_label.configure(text=f"🎶 Đang phát: {self.current_file}", text_color="#2ecc71")
        else:
            pygame.mixer.music.pause()
            self.is_paused = True
            self.btn_pause.configure(text="▶ PHÁT TIẾP")
            self.status_label.configure(text="⏸ Đã tạm dừng.", text_color="#f39c12")

    def stop_and_delete(self):
        if self.current_file and os.path.exists(self.current_file):
            # Lệnh stop âm thanh
            pygame.mixer.music.stop()
            
            # GIẢI PHÓNG BỘ NHỚ: Ép thư viện nhả quyền kiểm soát file
            try:
                pygame.mixer.music.unload() 
            except AttributeError:
                pass
            
            # Cố gắng xóa file vĩnh viễn khỏi ổ cứng
            try:
                os.remove(self.current_file)
                self.status_label.configure(text="⏹ Đã dừng. File âm thanh đã bị XÓA vĩnh viễn.", text_color="gray")
            except PermissionError:
                # Nếu Windows vẫn cố chấp khóa file, ta khởi động lại luôn cả cụm âm thanh để cưỡng ép nhả file
                pygame.mixer.quit()
                os.remove(self.current_file)
                pygame.mixer.init()
                self.status_label.configure(text="⏹ Đã dừng. File âm thanh đã bị XÓA vĩnh viễn.", text_color="gray")
            
        self.is_playing = False
        self.is_paused = False
        self.current_file = None
        
        # Khóa nút lại
        self.btn_pause.configure(state="disabled", text="⏸ TẠM DỪNG")
        self.btn_stop.configure(state="disabled")

# Xử lý dọn dẹp file rác nếu người dùng bấm dấu X tắt ngang ứng dụng
def on_closing():
    app.stop_and_delete()
    app.destroy()

if __name__ == "__main__":
    app = BrainwaveStudioPro()
    app.protocol("WM_DELETE_WINDOW", on_closing)
    app.mainloop()