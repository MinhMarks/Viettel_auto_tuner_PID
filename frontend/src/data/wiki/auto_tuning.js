export const autoTuning = {
    title: 'Thuật toán Auto-Tuning',
    content: `
# Dò Tìm Tham Số PID (Auto-Tuning)

Để có được bộ 6 tham số PID $(K_{p}, K_{i}, K_{d})$ cho trục Pitch và Yaw, chúng ta cung cấp các phương pháp sau:

### 1. Genetic Algorithm (GA - Thuật toán Di Truyền)
- Mô phỏng quá trình tiến hóa tự nhiên (Chọn lọc, Lai ghép, Đột biến).
- Quần thể các bộ PID được đánh giá qua hàm mục tiêu. Các bộ PID tốt "giao phối" với nhau tạo ra thế hệ sau. Rất giỏi tìm kiếm toàn cục (Global Search) tránh kẹt vào cực tiểu địa phương.

### 2. Particle Swarm Optimization (PSO - Bầy Đàn)
- Mô phỏng bầy chim bay tìm thức ăn. Mỗi bầy (particle) là một bộ PID bay trong không gian 6 chiều. Mỗi hạt sẽ nhớ vị trí tốt nhất của bản thân nó, và vị trí tốt nhất của cả bầy để tự điều chỉnh hướng bay.
- PSO thường hội tụ nhanh hơn GA đối với bài toán điều khiển liên tục.

### 3. Bayesian Optimization (BO - Tối ưu Bayes)
- Sử dụng mô hình thống kê (Gaussian Process) để ước lượng hàm chi phí (hàm đen). 
- Dựa trên giá trị trung bình và phương sai ước lượng, BO quyết định thông minh điểm tiếp theo cần thử (cân bằng giữa Khám phá - Exploration và Khai thác - Exploitation). Cực kỳ tiết kiệm số lần mô phỏng so với GA/PSO.
`
};
