export const intro = {
    title: 'Đề bài & Tổng quan',
    content: `
# Bài Toán Điều Khiển Trực Thăng 2 Bậc Tự Do (2-DOF Helicopter)

Hệ thống trực thăng 2 bậc tự do (Quanser 2-DOF Helicopter) là một mô hình chuẩn trong kỹ thuật điều khiển. Bản chất hệ thống là phi tuyến tính, ghép kênh mạnh (strongly coupled) và thiếu cơ cấu chấp hành (underactuated) ở một số khía cạnh.

**Mục tiêu của dự án:**
1. Số hoá và mô phỏng chính xác động học của trực thăng.
2. Thiết kế bộ điều khiển PID phân tán (Decentralized PID) bám quỹ đạo góc Pitch (Trục dọc) và góc Yaw (Trục ngang).
3. Triển khai các thuật toán tối ưu (Meta-heuristic & Bayesian) để tự động dò tìm tham số (Auto-Tuning).
4. Áp dụng kỹ thuật Gain Scheduling (Classic, Model-based, Fuzzy) để giải quyết tính phi tuyến khi hoạt động ở góc nghiêng lớn.
`
};
