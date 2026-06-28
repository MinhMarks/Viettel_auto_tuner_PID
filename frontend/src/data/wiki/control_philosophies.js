export const controlPhilosophies = {
    title: 'Trường phái Điều khiển',
    content: `
# Các Trường Phái Điều Khiển & Lý do chọn PID

Trong điều khiển học hiện đại, có 3 trường phái chính để giải quyết bài toán phi tuyến như 2-DOF Helicopter. Mặc dù dự án này chọn **PID Phân tán (Decentralized PID)** làm cốt lõi vì tính đơn giản, dễ triển khai thực tế và độ tin cậy công nghiệp cao (chiếm >90% trong công nghiệp), việc đối chiếu với các trường phái khác là cần thiết để thấy được bức tranh toàn cảnh.

### 1. Điều khiển Tối ưu và Không gian trạng thái (State-Space & Optimal Control)
Đại diện tiêu biểu là **LQR (Linear Quadratic Regulator)** hoặc **MPC (Model Predictive Control)**.
- **Tiếp cận:** Tuyến tính hoá hệ thống quanh một điểm làm việc để đưa về hệ phương trình trạng thái $\\dot{x} = Ax + Bu$. LQR tìm ma trận phản hồi $K$ để cực tiểu hoá hàm chi phí toàn phương $J = \\int (x^T Q x + u^T R u) dt$.
- **So sánh với PID:** LQR xử lý rất tốt sự ghép kênh (coupling) giữa trục Pitch và Yaw (vì nó là bộ điều khiển MIMO). Tuy nhiên, LQR yêu cầu biết chính xác toàn bộ state vector (kể cả vận tốc góc) và rất nhạy cảm với sai số mô hình. PID phân tán rẻ hơn, dễ tune hơn ở hiện trường.

### 2. Điều khiển Thích nghi và Bền vững (Adaptive & Robust Control)
Đại diện là **SMC (Sliding Mode Control)**, **$H_\\infty$**, hoặc **MRAC (Model Reference Adaptive Control)**.
- **Tiếp cận:** Thiết kế bộ điều khiển chịu đựng được nhiễu loạn (Robust) hoặc tự thay đổi cấu trúc khi đối tượng thay đổi (Adaptive). SMC ép quỹ đạo hệ thống trượt trên một mặt phẳng mong muốn (Sliding Surface) bằng các tín hiệu điều khiển tần số cao (chattering).
- **So sánh với PID:** Bền vững hơn PID trước gió tạt hoặc thay đổi tải trọng. Tuy nhiên SMC gây hao mòn cơ khí nghiêm trọng do chattering, trong khi $H_\\infty$ đòi hỏi kiến thức toán học quá phức tạp để triển khai trên vi điều khiển cấp thấp.

### 3. Điều khiển Thông minh (AI / Intelligent Control)
Đại diện là **DRL (Deep Reinforcement Learning)** hoặc **Mạng Nơ-ron (Neural Networks)**.
- **Tiếp cận:** Xem hệ thống là hộp đen (Black-box). Tác tử (Agent) học chính sách điều khiển thông qua quá trình thử-sai với môi trường mô phỏng (RL) hoặc xấp xỉ hàm phi tuyến (NN).
- **So sánh với PID:** AI Control có thể giải quyết hoàn hảo tính phi tuyến mà không cần biết phương trình vật lý. Nhưng nó mang bản chất "hộp đen", thiếu chứng minh độ ổn định toán học (Lyapunov stability), khó gỡ lỗi và yêu cầu năng lực tính toán cực lớn.

> Trong dự án này, chúng ta sử dụng **PID** kết hợp với sự thông minh của **Thuật toán tối ưu hoá** và **Fuzzy Logic** để lai tạo sức mạnh giữa điều khiển kinh điển và trí tuệ nhân tạo, mang lại một bộ điều khiển vừa minh bạch, vừa linh hoạt.
`
};
