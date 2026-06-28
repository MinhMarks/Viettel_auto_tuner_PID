export const limitations = {
    title: 'Hạn chế của Hệ thống',
    content: `
# Các Hạn Chế Hiện Tại của Hệ Thống

Dù đã tích hợp các công nghệ tiên tiến, cả mô hình mô phỏng lẫn hệ thống thực tế vẫn vấp phải những rào cản vật lý và toán học cốt lõi.

### A. Ma sát tĩnh (Coulomb Friction) là kẻ phá hoại
Hệ thống bị ảnh hưởng rất nặng bởi ma sát Coulomb ($F_{c}$). Khi trực thăng bay gần tới góc mục tiêu, sai số $e$ giảm dần dẫn đến tín hiệu điều khiển từ bộ PID sụt giảm về sát $0$. Khi lực motor quá yếu, nó không gồng nổi qua lực ma sát tĩnh Coulomb nữa.
$\\rightarrow$ **Hệ quả:** Máy bay bị kẹt cứng ngay trước khi chạm tới mục tiêu (tạo ra Steady State Error không thể xoá bỏ bằng Khâu I thông thường mà không gây Windup).

### B. Sự bất đối xứng của cánh quạt đuôi (Yaw Asymmetry)
Trục Yaw có đáp ứng động học bất đối xứng. Lưỡi quạt nhựa thực tế chỉ được tối ưu hóa khí động học để thổi gió mạnh về một hướng (lực đẩy lùi). 
$\\rightarrow$ **Hệ quả:** Khi lệnh quay trái, nó phản hồi rất nhanh; nhưng khi lệnh bắt quay sang phải (motor phải quay ngược, hút gió), hiệu suất nâng bị tụt giảm nghiêm trọng. Mô hình tuyến tính đối xứng sẽ thất bại nặng nề tại đây.

### C. Ràng buộc toán học của Cực bất ổn định (Unstable Pole)
Khi định danh hệ thống (System Identification) thực tế, hệ thống vòng hở có thể chứa một cực (pole) nằm bên nửa phải mặt phẳng phức.
$\\rightarrow$ **Hệ quả:** Toán học giải tích đã chứng minh (Bode Integral Theorem): Chừng nào hệ thống còn tồn tại cực bất ổn định này, thì dù dùng bất kỳ kỹ thuật điều khiển nào (PID, LQR, hay AI), hệ thống bắt buộc **PHẢI CÓ vọt lố (Overshoot)**. Cố gắng dập vọt lố sẽ làm thời gian xác lập cực kỳ chậm và ngược lại. 

### D. Tích luỹ sai số (Integral Windup)
Trong quá trình bám quỹ đạo động, khâu Tích phân (I) của PID liên tục cộng dồn sai số. Nếu động cơ đạt tới điểm bão hoà (Saturation - ví dụ 24V max), khâu I vẫn tiếp tục phình to. Khi vượt qua điểm setpoint, khâu I khổng lồ sẽ bắt động cơ chạy xả lùi rất lâu, gây ra hiện tượng mất kiểm soát (Windup). 

### E. Đặc dụng Model (Sim2Real Gap)
Mô hình \`helicopter_2dof_env\` hiện tại đang dựa trên các tham số danh định của NSX Quanser (như khối lượng $m$, khoảng cách trọng tâm $l_p$). Trong thực tế, nhiệt độ cuộn dây motor, độ rơ cơ học của trục quay, và sự xói mòn khí động học gây ra một khoảng trống lớn giữa mô phỏng và thực tế (Sim-to-Real Gap).
`
};
