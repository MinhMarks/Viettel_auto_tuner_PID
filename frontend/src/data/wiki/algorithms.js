export const algorithms = {
    title: 'Các Thuật toán Tối ưu',
    content: `
# Các Thuật toán Tối ưu (Optimization Algorithms)

Trong dự án này, hệ thống hỗ trợ 5 thuật toán tối ưu hóa siêu tham số (Hyperparameter Optimization) khác nhau để tự động tìm ra bộ thông số PID tốt nhất. Mỗi thuật toán có một cơ chế tìm kiếm và đặc điểm hội tụ riêng, phù hợp với các tình huống và độ phức tạp khác nhau của hàm mục tiêu (Objective Function).

Dưới đây là nguyên lý hoạt động chi tiết của từng thuật toán.

---

## 1. GA (Genetic Algorithm)
**Thuật toán Di truyền** lấy cảm hứng từ quá trình tiến hóa và chọn lọc tự nhiên của Darwin.

- **Nguyên lý hoạt động:**
  1. **Khởi tạo:** Tạo ra một quần thể (population) gồm nhiều cá thể ngẫu nhiên. Mỗi cá thể đại diện cho một bộ tham số PID.
  2. **Đánh giá (Evaluation):** Tính toán độ fitness (Cost function) cho từng cá thể.
  3. **Chọn lọc (Selection):** Giữ lại các cá thể tốt nhất (Cost thấp nhất) để làm thế hệ cha mẹ.
  4. **Lai ghép (Crossover):** Kết hợp "nhiễm sắc thể" (các tham số $K_p, K_i, K_d$) của cha mẹ để tạo ra con cái mang đặc tính của cả hai.
  5. **Đột biến (Mutation):** Thay đổi ngẫu nhiên một tỷ lệ nhỏ tham số của con cái để duy trì sự đa dạng sinh học và tránh kẹt ở cực tiểu địa phương.
  6. Lặp lại quá trình này qua nhiều thế hệ (iterations) cho đến khi quần thể hội tụ về nghiệm tối ưu.

- **Đặc điểm:** Tốc độ hội tụ tương đối chậm, nhưng có khả năng tìm kiếm toàn cục rất tốt, khó bị kẹt vào cực tiểu địa phương nhờ cơ chế đột biến.

---

## 2. PSO (Particle Swarm Optimization)
**Tối ưu hóa Bầy đàn** mô phỏng hành vi kiếm mồi của các bầy chim hoặc đàn cá.

- **Nguyên lý hoạt động:**
  - Khởi tạo một bầy (swarm) gồm nhiều hạt (particles). Mỗi hạt là một bộ tham số PID.
  - Trong mỗi vòng lặp, mỗi hạt di chuyển trong không gian tìm kiếm dựa trên 3 yếu tố:
    1. **Quán tính (Inertia):** Hướng di chuyển cũ của chính nó.
    2. **Kinh nghiệm cá nhân (Cognitive):** Vị trí tốt nhất mà chính nó từng tìm thấy (Personal Best).
    3. **Kinh nghiệm xã hội (Social):** Vị trí tốt nhất mà toàn bộ bầy từng tìm thấy (Global Best).
  - Vận tốc di chuyển của hạt $i$ ở bước $t+1$ được tính bằng:
    $$ V_{i}^{t+1} = w V_{i}^{t} + c_1 r_1 (P_{best} - X_{i}^{t}) + c_2 r_2 (G_{best} - X_{i}^{t}) $$
  - Quá trình lặp lại liên tục kéo theo cả bầy dần bay về phía vị trí "thức ăn" ngon nhất (Nghiệm tối ưu).

- **Đặc điểm:** Hội tụ cực nhanh và có khả năng khai thác (exploitation) vùng không gian cục bộ cực kỳ mạnh. Tuy nhiên, dễ bị hội tụ sớm (premature convergence) nếu rơi vào cực tiểu địa phương.

---

## 3. TPE (Tree-structured Parzen Estimator)
TPE là một thuật toán tối ưu hóa theo mô hình Bayes (Bayesian Optimization), được sử dụng mặc định trong thư viện Optuna.

- **Nguyên lý hoạt động:**
  - Thay vì duy trì một quần thể, TPE xây dựng một mô hình xác suất học máy để dự đoán phân phối của vùng tham số sinh ra Cost thấp.
  - Sau mỗi phép thử, TPE chia các điểm dữ liệu lịch sử thành 2 nhóm:
    1. Nhóm điểm có kết quả TỐT (Good).
    2. Nhóm điểm có kết quả XẤU (Bad).
  - TPE sẽ cố gắng chọn điểm tiếp theo (bộ PID tiếp theo) sao cho nó có xác suất thuộc nhóm TỐT cao nhất và xác suất thuộc nhóm XẤU thấp nhất.
  - Do cơ chế này, TPE vừa học (khai thác) vừa thử nghiệm ngẫu nhiên (khám phá).

- **Đặc điểm:** Rất hiệu quả khi số lượng tham số ít, không cần đánh giá quá nhiều vòng lặp. TPE tối ưu từng điểm một (sequential) nên tiết kiệm chi phí tính toán hàm mục tiêu, nhưng có thể chậm hơn nếu số chiều bài toán (dimensions) lớn.

---

## 4. CMA-ES (Covariance Matrix Adaptation Evolution Strategy)
**CMA-ES** là một thuật toán tiến hóa liên tục, cực kỳ nổi tiếng và được coi là tiêu chuẩn vàng (state-of-the-art) cho các bài toán tối ưu hóa hàm hộp đen phi tuyến tính, không thể tính đạo hàm.

- **Nguyên lý hoạt động:**
  - Dựa trên một phân phối chuẩn đa chiều (Multivariate Normal Distribution).
  - Khởi tạo bằng cách lấy mẫu các nghiệm xung quanh một điểm trung bình (Mean).
  - Sau khi đánh giá các nghiệm, thuật toán sẽ thực hiện 2 việc chính:
    1. Dời điểm trung bình về phía các nghiệm tốt nhất.
    2. **Thích nghi ma trận hiệp phương sai (Covariance Matrix Adaptation):** Tự động điều chỉnh hình dáng và hướng của đám mây phân phối mẫu để bám theo đường viền (contours) của hàm mục tiêu.

- **Đặc điểm:** Vô đối trong các không gian biến dạng, đồi núi gồ ghề (ill-conditioned problems). Khả năng tìm kiếm toàn cục và vượt cực tiểu địa phương xuất sắc. Tuy nhiên, khá phức tạp và cần nhiều vòng lặp để làm nóng ma trận hiệp phương sai.

---

## 5. GWO (Grey Wolf Optimizer)
**Thuật toán Chó Sói Xám** là một thuật toán metaheuristic lấy cảm hứng từ cấu trúc phân cấp lãnh đạo và chiến thuật săn mồi của đàn sói xám trong tự nhiên.

- **Nguyên lý hoạt động:**
  - Quần thể sói được chia làm 4 cấp bậc:
    1. **Alpha ($\alpha$):** Con sói đầu đàn (Nghiệm tốt nhất hiện tại).
    2. **Beta ($\beta$):** Con sói phó đàn (Nghiệm tốt thứ 2).
    3. **Delta ($\delta$):** Con sói cấp 3 (Nghiệm tốt thứ 3).
    4. **Omega ($\omega$):** Các con sói còn lại (Các nghiệm yếu hơn).
  - Trong quá trình săn mồi (tối ưu hóa), $\alpha, \beta, \delta$ sẽ ước lượng vị trí của con mồi (điểm tối ưu). 
  - Các con sói $\omega$ sẽ tự động điều chỉnh vị trí của chúng theo hướng chỉ đạo của $\alpha, \beta, \delta$. Vòng vây ngày càng thu hẹp cho đến khi tóm được mồi.

- **Đặc điểm:** Cân bằng hoàn hảo giữa khả năng khám phá không gian rộng (exploration) và bám đuổi nghiệm tốt (exploitation) nhờ cơ chế phân cấp lãnh đạo rõ ràng. Thường có khả năng tránh cực tiểu địa phương và ít tham số cần tinh chỉnh.
`
};
