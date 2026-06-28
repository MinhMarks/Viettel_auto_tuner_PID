export const modeling = {
    title: 'Mô hình Toán học',
    content: `
# Phương Pháp Lập Mô Hình Động Học (Kinematics & Dynamics)

Để mô phỏng hệ thống trong \`helicopter_2dof_env.py\`, chúng ta cần xây dựng hệ phương trình vi phân mô tả chuyển động. Trong Cơ học Giải tích (Analytical Mechanics), có 6 phương pháp phổ biến để tiếp cận bài toán này. 

Hệ thống của chúng ta hiện đang được mô hình hoá dựa trên **Newton-Euler** (vì tính trực quan về lực và mô-men). Dưới đây là sự so sánh các lăng kính toán học:

### 1.1 Newton-Euler
- Phân tích trực tiếp các lực (lực nâng motor, trọng lực) và mô-men tác dụng lên trọng tâm của trực thăng. 
- **Đặc điểm:** Rất trực quan ($\\sum F = ma, \\sum \\tau = I \\alpha$), dễ hình dung ma sát, nhưng phải giải quyết các lực liên kết (constraint forces) rất phức tạp nếu hệ có nhiều khớp nối.

### 1.2 Euler-Lagrange
- Dựa trên năng lượng của hệ: Lagrangian $L = T - V$ (Động năng trừ Thế năng). Giải phương trình:
  $$ \\frac{d}{dt} \\left( \\frac{\\partial L}{\\partial \\dot{q}_i} \\right) - \\frac{\\partial L}{\\partial q_i} = Q_i $$
- **Đặc điểm:** Tự động loại bỏ các lực liên kết nội tại, tính toán có tính hệ thống cao cho robot nhiều bậc tự do. Đây là phương pháp phổ biến nhất trong Robotics học thuật.

### 1.3 Hamiltonian Mechanics
- Chuyển đổi từ không gian $(q, \\dot{q})$ sang không gian pha $(q, p)$ với động lượng tổng quát $p$. Hamiltonian $H = T + V$ đại diện cho tổng năng lượng.
- **Đặc điểm:** Hệ phương trình vi phân cấp 1 đối xứng tuyệt đẹp ($\\dot{q} = \\frac{\\partial H}{\\partial p}, \\dot{p} = -\\frac{\\partial H}{\\partial q}$). Rất hữu ích cho các lý thuyết điều khiển bảo toàn năng lượng (Passivity-based control).

### 1.4 Kane's Equations
- Sử dụng vận tốc tổng quát (partial velocities). 
- **Đặc điểm:** Hiệu quả tính toán bậc nhất (tiết kiệm số phép nhân/cộng). Được ứng dụng nhiều trong các phần mềm mô phỏng vật lý vũ trụ hoặc động lực học phức tạp vì nó tối ưu cho máy tính.

### 1.5 Gauss's Principle of Least Constraint
- Tuân theo nguyên lý: Gia tốc thực tế của hệ thống là gia tốc cực tiểu hoá một hàm "ràng buộc" (Constraint function) so với gia tốc khi hệ tự do rơi.
- **Đặc điểm:** Ít phổ biến trong kỹ thuật điều khiển nhưng cực kỳ mạnh mẽ khi mô phỏng các robot có ràng buộc phi holonomic (non-holonomic constraints).

### 1.6 Black-box Data-Driven Modeling
- Không sử dụng các định luật vật lý (First principles). Xây dựng mô hình bằng cách thu thập dữ liệu Input-Output (Điện áp vào - Góc ra) và dùng Machine Learning (RNN, LSTM, SINDy) để nhận dạng hệ thống (System Identification).
- **Đặc điểm:** Bù đắp được các yếu tố vật lý khó mô hình (ma sát phi tuyến phức tạp, độ rơ cơ khí), nhưng không có ý nghĩa vật lý tường minh (Physical insight).
`
};
