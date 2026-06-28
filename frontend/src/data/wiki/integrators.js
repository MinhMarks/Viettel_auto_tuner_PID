export const integrators = {
    title: 'Bộ giải vi phân (RK45)',
    content: `
# Giải Tích Phân Số (Numerical Integration)

Mô hình hệ thống trực thăng được định nghĩa bởi một phương trình trạng thái dạng vi phân:
$$ \\dot{x}(t) = f(x(t), u(t), t) $$

Để tính toán trạng thái tiếp theo $x(t + \\Delta t)$ trong môi trường giả lập (\`helicopter_2dof_env.py\`), ta không thể giải phương trình này bằng giải tích giải tích (Analytically) vì nó phi tuyến. Ta phải dùng phương pháp số.

### Phương pháp Runge-Kutta bậc 4/5 (RK45)
Dự án của chúng ta sử dụng thuật toán **RK45** (Dormand-Prince). 
- Khác với phương pháp Euler cơ bản (chỉ xấp xỉ đạo hàm bậc 1 $x_{k+1} = x_k + \\Delta t \\cdot f(x_k)$ gây sai số tích luỹ khổng lồ), RK4 dự đoán độ dốc tại 4 điểm trong khoảng $\\Delta t$ và lấy trung bình có trọng số.
- **Cơ chế Bước thời gian thích nghi (Adaptive Step Size):** RK45 vừa tính kết quả bằng công thức bậc 4, vừa tính bằng công thức bậc 5. Sự chênh lệch giữa hai kết quả được dùng làm "sai số ước lượng". Nếu sai số lớn (khi trạng thái thay đổi quá gắt), thuật toán tự động chia nhỏ $\\Delta t$ ra. Điều này đảm bảo mô phỏng trực thăng vừa chạy nhanh lúc ổn định, vừa không bị nổ (diverge) khi có dao động tần số cao.
`
};
