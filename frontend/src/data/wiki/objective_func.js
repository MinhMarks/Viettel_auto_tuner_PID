export const objectiveFunc = {
    title: 'Hàm Mục Tiêu Đa Cấu Phần',
    content: `
# Khảo cứu SOTA & Thiết kế Hàm Mục Tiêu (Objective Function)

Trong quá trình ứng dụng Trí tuệ Nhân tạo (AI/Meta-heuristics) để tối ưu hóa bộ điều khiển cho các hệ thống Hàng không Vũ trụ (Aerospace) hoặc Robot, việc thiết kế một **Hàm mục tiêu (Fitness Function)** chuẩn xác là cực kỳ quan trọng. AI không tối ưu "mù" bằng toán học, mà nó học cách thỏa mãn các tiêu chuẩn kỹ thuật có cân nhắc đến giới hạn cơ khí thực tế.

Dưới đây là cơ sở lý thuyết SOTA (State-of-the-Art) đằng sau kiến trúc hàm mục tiêu mà hệ thống Quanser 2-DOF Helicopter của chúng ta đang sử dụng. Kiến trúc này được tổng hợp từ 3 nhóm nghiên cứu cốt lõi:

## 1. Thành phần Chất lượng Bám (Performance - $J_1$)
Ban đầu, các Auto-tuner thường chỉ dùng hàm **ITAE (Integral of Time-weighted Absolute Error)**: $J = \\int t \\cdot |e(t)| dt$.
Tuy nhiên, các nghiên cứu về hệ bám quỹ đạo động học phi tuyến chỉ ra rằng ITAE truyền thống gặp nhược điểm khi bám quỹ đạo động phức tạp liên tục, như Multi-step hay Sine wave [1]. Để ép trực thăng bám sát mục tiêu, chúng ta giữ nguyên nền tảng ITAE làm cấu phần $J_1$ để tối ưu hóa độ ổn định dài hạn (Steady-state dynamic tracking) và triệt tiêu sai số tĩnh.

## 2. Thành phần Bảo vệ Phần cứng (Actuator Protection - $J_2$)
> **Bài toán:** Nếu chỉ dùng ITAE, AI sẽ đẩy thông số PID ($K_p, K_d$) lên rất cao. Điều này khiến động cơ sinh ra các xung điện áp (Voltage) cực đoan (chatter liên tục), vượt giới hạn vật lý, gây hao mòn cơ khí và tốn năng lượng.

Giải pháp tối ưu đa mục tiêu được đề xuất để giải quyết tình trạng này bằng cách tích hợp **Control Effort & Smoothness** (Năng lượng & Độ mịn cơ khí) [2, 3].
Cấu phần $J_2$ của chúng ta ra đời để phạt năng lượng ($\\int V^2 dt$) và phạt sự giật cục của điện áp ($\\int \\Delta V^2 dt$). Nhờ đó, động cơ chạy êm hơn, không phát ra tiếng rít và tiết kiệm pin.

## 3. Thành phần Ràng buộc Vật lý (Constraint Handling - $J_3$)
> **Bài toán:** Khi trực thăng bám sóng vuông (Square Wave), hiện tượng Bão hòa Tích phân (Integrator Windup) xảy ra do điện áp bị giới hạn ở mức $\\pm 24\\text{V}$ bởi trạm nguồn VoltPaq.

Để đối phó với giới hạn phần cứng cứng ngắc, một giải pháp hiệu quả là bổ sung hàm phạt động (Dynamic Penalty Function) [4]. Bất cứ khi nào bộ PID (do AI sinh ra) đòi xuất một mức điện áp vượt ngưỡng $24\\text{V}$, điểm Fitness sẽ bị cộng thêm một lượng phạt khổng lồ thông qua cấu phần $J_3$, ép thuật toán AI phải quay đầu tìm kiếm trong "vùng tham số an toàn".


---

### Chuẩn Hóa Không Kích Thước (Normalization) — Giải Pháp Bắt Buộc
Lý do lớn nhất khiến việc chọn $\\alpha, \\beta$ bằng tay trở nên bất khả thi là vì các thành phần $J_1, J_2, J_3$ bị lệch pha hoàn toàn về mặt đơn vị vật lý và biên độ số.
- Sai số góc $e$ tính bằng Radian (chỉ quanh quẩn từ $0 \\to 0.5$).
- Điện áp $V^2$ tính bằng Vôn bình phương (có thể lên tới $24^2 = 576$).

Nếu đặt $\\alpha = 1$, thành phần năng lượng $J_2$ sẽ to gấp hàng ngàn lần sai số $J_1$, khiến các bầy chim PSO/GA chỉ lo "tiết kiệm điện" mà bỏ mặc máy bay rơi tự do.

**Cách giải quyết:** Chúng ta chia mỗi thành phần $J_i$ cho giá trị lớn nhất có thể chấp nhận được của chính nó ($J_{i,\\max}$). Lúc này, mọi $J_i$ đều biến thành một con số không đơn vị, chạy ngoan ngoãn trong khoảng từ $0 \\to 1$.
$$ \\bar{J}_1 = \\frac{J_1}{J_{1,\\max}}, \\quad \\bar{J}_2 = \\frac{J_2}{J_{2,\\max}}, \\quad \\bar{J}_3 = \\frac{J_3}{J_{3,\\max}} $$

Khi đã chuẩn hóa về cùng một "sân chơi" từ $0 \\to 1$, các hệ số $\\alpha, \\beta$ lúc này không còn phải gánh nhiệm vụ quy đổi đơn vị nữa. Thuật toán hoàn toàn có thể đặt $\\alpha = 1, \\beta = 1$ (coi các mục tiêu quan trọng ngang nhau) mà không sợ hệ thống bị lệch lạc.

---
<div id="tuning-profiles-section"></div>

### Ý Nghĩa Của 4 Tuning Profiles (Trọng số tùy chỉnh)

Bằng cách điều chỉnh tỷ lệ giữa $\alpha$ (năng lượng) và $\beta$ (bão hòa), chúng ta có thể hướng AI học ra các bộ PID có "tính cách" khác nhau. Dưới đây là 4 cấu hình đã được cung cấp trong **Ideal Tuning**:

1. **Balanced (Cân bằng):** $w_{itae} = 1, w_{energy} = 1, w_{smoothness} = 1, w_{saturation} = 1$
   - Cân bằng hoàn hảo giữa thời gian đáp ứng và mức tiêu thụ điện năng. Lý tưởng cho các ứng dụng theo dõi mục tiêu bình thường.
2. **Aggressive Tracking (Bám gắt):** $w_{itae} = 5, w_{energy} = 0.1, w_{smoothness} = 0.1, w_{saturation} = 1$
   - Dồn toàn bộ sự tập trung vào $J_1$ (ITAE) để giảm sai số về 0 nhanh nhất có thể.
   - Chấp nhận tốn điện và động cơ bị giật cục. Thích hợp cho môi trường quân sự cần phản ứng tức thời.
3. **Eco & Smooth (Êm ái & Tiết kiệm):** $w_{itae} = 1, w_{energy} = 5, w_{smoothness} = 10, w_{saturation} = 1$
   - Đặt phạt rất nặng lên $J_2$ (Đặc biệt là Smoothness). 
   - Động cơ sẽ chạy vô cùng mượt mà, không tiếng rít, pin dùng được lâu, nhưng bù lại thời gian hội tụ mục tiêu (Settling time) sẽ bị chậm đi đáng kể. Phù hợp làm camera drone.
4. **Strict Safety (An toàn tuyệt đối):** $w_{itae} = 1, w_{energy} = 1, w_{smoothness} = 1, w_{saturation} = 50$
   - Hình phạt khổng lồ lên $J_3$ (Saturation). 
   - Bộ điều khiển tuyệt đối không bao giờ được phép xuất ra dòng điện vượt quá $24V$ dù chỉ 1 milisecond, nhằm tránh cháy nổ trạm nguồn VoltPaq.

---
### Kiến Trúc Hàm Tổng Hợp Của Hệ Thống

Kết hợp các lý thuyết trên, hàm mục tiêu thực tế chạy trong backend (\`objective_function.py\`) của dự án được định nghĩa như sau:

$$ Fitness = J_1 + \\alpha \\cdot J_2 + \\beta \\cdot J_3 $$

Trong đó:
- **$J_1$ (Performance):** $\\int t \\cdot (|e_{pitch}| + |e_{yaw}|) dt$
- **$J_2$ (Actuator Protection):** $w_{energy} \\int (V_p^2 + V_y^2) dt + w_{smoothness} \\int (\\Delta V_p^2 + \\Delta V_y^2) dt$
- **$J_3$ (Saturation Penalty):** $w_{saturation} \\int \\max(0, |V| - 24) dt$
---

### Tài Liệu Tham Khảo (References)
[1] *Modified ITAE Objective Function for Dynamic Trajectory Tracking of Non-linear Servo Systems*  
[2] *A Novel Multi-Objective Fitness Function for PSO-Based PID Tuning of Non-linear Systems*  
[3] *Multi-Objective Optimization of PID Controller Parameters for a 2-DOF Helicopter Using Controlled Elitist Genetic Algorithm*  
[4] *Constraint Handling in Metaheuristic Optimization for UAV Controllers: A Saturation Penalty Approach*
`
};
