export const gainScheduling = {
    title: 'Dynamic Tracking & Gain Scheduling',
    content: `
# Bám Quỹ Đạo Động (Dynamic Trajectory Tracking)

Trong điều khiển bám, khi biên độ (Setpoint) thay đổi lớn, tính phi tuyến của trực thăng (hàm $\\sin(\\theta)$ của trọng lực, cross-coupling) bộc lộ rõ. Một bộ PID duy nhất (tuyến tính) không thể đảm bảo chất lượng ở mọi góc nghiêng.

## Các Phương Pháp SOTA (State-of-the-Art)
Trong nghiên cứu hiện đại, bài toán này được giải quyết bằng các kỹ thuật tiên tiến:
1. **DRL-PID (Deep Reinforcement Learning-based Adaptive PID):** Dùng mạng RL (PPO/SAC) để điều chỉnh $K_p, K_i, K_d$ liên tục theo thời gian thực (real-time). 
2. **RBF Neural Network Adaptive PID:** Mạng nơ-ron hàm xuyên tâm (RBF) online xấp xỉ các thành phần phi tuyến chưa biết của hệ thống và bù trừ trực tiếp vào luật điều khiển PID.
3. **ASMPID (Adaptive Sliding Mode PID Control):** Ghép mảng PID vào mặt trượt (Sliding Surface) để tận dụng độ bền vững của SMC nhưng giữ được sự trơn tru của PID.
4. **Hybrid Meta-heuristic Optimized Fuzzy PID:** Dùng thuật toán đàn kết hợp mờ, giống với hướng tiếp cận Fuzzy của chúng ta, nhưng thuật toán mờ bị điều chỉnh liên tục.

## Lựa chọn của dự án
Dự án của chúng ta trang bị một cơ chế so sánh 4 chế độ **Gain Scheduling** (Lập lịch khuếch đại) để giải quyết vấn đề góc lớn:

1. **None (Single PID):** Dùng 1 bộ PID xuyên suốt. Sẽ bộc lộ sự chậm chạp hoặc rung lắc khi gặp góc lớn.
2. **Classic Gain Scheduling:** Sử dụng 2 bộ PID. Một bộ cho góc nhỏ, một bộ cho góc lớn. Trọng số chuyển đổi (Blend Alpha) được thực hiện bằng hàm Bậc thang (Step), Tuyến tính (Linear), hoặc Sigmoid.
3. **Model-Based Compensation:** Dùng 1 bộ PID cơ bản, cộng thêm một tín hiệu bù Feed-Forward dựa trên mô hình toán học (Bù trọng lực $\\hat{m} g l \\sin(\\theta_{ref})$). Giúp triệt tiêu trực tiếp tính phi tuyến đã biết.
4. **Fuzzy Adaptive PID:** Đưa sai số $e$ và đạo hàm $\\Delta e$ qua hệ Logic Mờ (Fuzzy Inference System). Các luật IF-THEN sẽ trực tiếp scale (nới lỏng hoặc siết chặt) các thông số PID một cách uyển chuyển theo trạng thái quỹ đạo.
`
};
