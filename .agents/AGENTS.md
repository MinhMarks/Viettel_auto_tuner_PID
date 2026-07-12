# Academic Paper Writing Rules

When tasked with writing, editing, or reviewing scientific papers, technical reports, or academic content, ALWAYS adhere strictly to the following Academic Writing Constraints:

## 1. Tone & Style
- Use formal, precise, objective, and authoritative academic language.
- Avoid journalistic language, marketing buzzwords (e.g., "game-changing", "revolutionary"), and casual transitions.

## 2. Density of Information
- Ensure a high density of knowledge. Every sentence must carry explicit logical or technical weight. Avoid fluff or redundant phrases.

## 3. Argumentation Strategy
- Use the **"three-step punch"** for literature critique:
  1. Acknowledge the state-of-the-art (SOTA).
  2. Pinpoint its critical limitations (e.g., computational overhead, vulnerability to noise).
  3. Pivot directly to how our proposed method resolves this gap.

## 4. Format & Structure
- **Topic Sentences (T-E-E-L Framework):** Every paragraph and section MUST begin with a clear, authoritative topic sentence that states the core subject. Subsequent sentences and sub-paragraphs must logically support, supplement, and develop that specific topic sentence.
- Do not use bullet points unless absolutely necessary. Present arguments in cohesive, well-structured paragraphs.
- Optimize sentence structures. Break down overly complex or fractured sentences into a smooth, balanced academic flow.

## 5. Technical Accuracy & Vocabulary
- Do not change the underlying technical meaning or mathematical concepts.
- Replace weak or non-academic verbs (e.g., "get", "make", "show", "bad", "good") with precise academic equivalents (e.g., "obtain", "formulate", "demonstrate", "susceptible", "superior").
- Eliminate wordiness (e.g., change "in order to" to "to", "due to the fact that" to "because").
- Correct any punctuation anomalies, particularly ensuring proper academic hedging (e.g., "may", "typically", "inherently").

- **Ask, Do Not Invent:** If user instructions, requirements, or inputs are ambiguous, incomplete, or not fully understood, ALWAYS ask the user for clarification. Do NOT hallucinate, guess, or invent ideas ("bịa ý") to fill in the gaps. Avoid adding redundant points that were not requested.

## 7. Technical Report vs. Research Paper Orientation
When writing a Technical Report (especially in an applied R&D setting like Viettel), pivot the focus from theoretical novelty to **practical problem solving and technology transfer**.
- **Retain Theory, Expand Practice:** Keep the theoretical foundations (like "Related Work" and "Novelty"), but heavily supplement them with extensive practical implementation details.
- **Emphasize Pipeline & Architecture:** Provide exhaustive details on the system architecture, data flow, GUI implementations, and software stacks (e.g., FastAPI, React, specific Python libraries) so that another engineer can perfectly reproduce the work.
- **Emphasize Physical Constraints:** Ground the optimization in physical realities (e.g., $\pm 24\text{V}$ voltage saturation, sensor noise, wind disturbance, payload changes).
- **Mandatory Failure Analysis:** Unlike academic papers that hide flaws, technical reports MUST detail edge cases, algorithm failures (e.g., PSO getting stuck in local optima, GA's heavy computational cost), and constraints to inform future deployment decisions.

## 8. User Guide & Technical Manual Constraints
When tasked with creating or updating User Guides or Technical Manuals, ALWAYS adhere strictly to the following rules:
- **Task-Oriented Structure:** Divide chapters based on user task goals (e.g., "Làm thế nào để cấu hình", "Làm thế nào để xem đồ thị").
- **3-Part Procedures:** Every procedure MUST include:
  1. **Điều kiện cần** (Prerequisites)
  2. **Các bước thực hiện** (Steps): Numbered (1, 2, 3) and always starting with action verbs.
  3. **Kết quả kỳ vọng** (Expected Results).
- **UI Element Formatting:** Bold all UI components like **[Nút bấm]**, **[Thẻ Menu]**. Place input values inside `code` blocks (e.g., `value`).
- **Image Placeholders:** Always create predefined placeholders for screenshots at crucial steps using the format: `[Chèn ảnh chụp màn hình...]` or explicitly define `<img src="...">` tags.
- **Troubleshooting Chapter:** Always write an 'Xử lý sự cố' (Troubleshooting) chapter covering classic errors (e.g., voltage saturation, simulator non-convergence, or UI crashes).
- **Tone & Style:** Objective, concise, imperative. Absolutely NO flowery or emotional language.

## 9. Frontend Routing & Navigation Constraints

When tasked with upgrading, adding, or refactoring client-side navigation in the Frontend of this project, ALWAYS adhere to the following rules.

### 9.1 General Principles
- **URL Must Reflect State:** Navigation MUST change the browser URL. Using React `useState` to show/hide components without updating the URL is PROHIBITED for top-level page navigation.
- **No Full-Page Reloads:** All page transitions MUST be handled client-side. Never use `<a href="...">` for internal navigation; use the framework's routing primitive (`<Link>` or `useNavigate` for React, `pushState` for Vanilla JS).
- **Browser History Support:** The Back/Forward buttons of the browser MUST work correctly and reflect the current URL state after any routing implementation.

### 9.2 React Projects — Standard: `react-router-dom` v6+

**Install:** `npm install react-router-dom`

**Router Configuration (`main.jsx` or `router.jsx`):**
- Use `createBrowserRouter` (not the deprecated `<BrowserRouter>` wrapper pattern).
- Define a root layout component (e.g., `Layout.jsx`) that contains the shared `<Navbar>` and an `<Outlet />` for child routes.
- Pass the router to `<RouterProvider router={router} />` in `main.jsx`.

**URL-to-Component Mapping Convention for this project:**

| URL Path | Component | Description |
|---|---|---|
| `/` | Redirect to `/experiments/ideal` | Default route |
| `/experiments/ideal` | `PageIdealTuning` | Experiment sub-tab 1 |
| `/experiments/robustness` | `PageRobustness` | Experiment sub-tab 2 |
| `/experiments/gainscheduling` | `PageGainScheduling` | Experiment sub-tab 3 |
| `/experiments/lqr` | `PageLQRComparison` | Experiment sub-tab 4 |
| `/simulation` | 3D Simulation Panel | Real-time HIL view |
| `/wiki` | `PageDocumentation` | Theory Wiki |
| `/history` | `PageHistory` | Session history |

**Navigation Rules:**
- Replace all `onClick={() => setMainTab(...)}` and `onClick={() => setExpTab(...)}` with `<Link to="/path">` or `useNavigate()`.
- The active tab highlight (CSS class `active`, `active-sub`) MUST be determined by `useMatch()` or `NavLink`'s built-in `isActive` prop, NOT by comparing a state variable.
- Shared/global state that must persist across routes (e.g., `tunedParams`, `manualParams`, `spPitch`) MUST be lifted to a React Context (`createContext`) or passed via a root layout component. Do NOT use URL query params for complex state objects.

**WebSocket Lifecycle:**
- The 3D Simulation WebSocket connection MUST connect `onMount` of the `/simulation` route component and disconnect `onUnmount` (i.e., use `useEffect` return cleanup within the route component itself).

### 9.3 Vanilla JS Projects — Standard: HTML5 History API

**Router Implementation:**
- Write a single `router.js` module exporting a `Router` class or factory function.
- The router MUST maintain an internal `routes` map: `{ path: string → renderFn: () => void }`.
- Use `window.history.pushState({ path }, '', path)` for programmatic navigation.
- Intercept ALL internal `<a>` clicks via event delegation on `document.body`: check `e.target.closest('a[data-link]')`, call `e.preventDefault()`, then `router.navigate(href)`.
- Bind `window.addEventListener('popstate', (e) => router.loadRoute(e.state?.path ?? '/'))` to handle browser Back/Forward.

**Route Registration Convention:**
```js
router.addRoute('/', renderHome);
router.addRoute('/api', renderApiTab);
```

**Initial Load:**
- On `DOMContentLoaded`, call `router.loadRoute(window.location.pathname)` so that a direct URL visit (e.g., `/api`) renders correctly without a 404.
# Data Visualization Rules (A* Academic Publication Standard)

You are an Expert Data Visualization Engineer specializing in A* Computer Science academic publications (e.g., NeurIPS, CVPR, ICML, IEEE/ACM Transactions). Your sole purpose is to generate Python code (Matplotlib/Seaborn) for charts, or LaTeX code for tables, that are strictly "Publication-Ready" out-of-the-box. 

You must strictly adhere to the following rules for every output:

### 1. GENERAL CHART AESTHETICS (The Tufte Principle)
- Maximize the Data-Ink Ratio: Remove all unnecessary visual clutter.
- Background: Strictly transparent or pure white. NEVER use the default grey background.
- Spines (Borders): Always remove the TOP and RIGHT spines (x.spines['top'].set_visible(False), etc.).
- Gridlines: If necessary, use only horizontal gridlines. They must be light grey (#E0E0E0), dashed (--), and set behind the data (zorder=0).
- Export Format: Always save figures as .pdf or .svg with box_inches='tight', NEVER as .png or .jpg.

### 2. COLORS AND ACCESSIBILITY (Black & White Print Safe)
- Color Palette: ALWAYS use colorblind-friendly palettes (e.g., Seaborn's colorblind, muted, or Tableau 10).
- Differentiate by Shape/Line, not just Color: Reviewers often print papers in grayscale. 
  - For Line Charts: Every line MUST have a distinct line style (-, --, -., :) AND a distinct marker (o, s, ^, D, x).
  - For Bar Charts: Use distinct hatch patterns (/, \, x, .) if colors are similar in grayscale.

### 3. TYPOGRAPHY (LaTeX Compatibility)
- Font Family: Use serif fonts (Times New Roman or standard LaTeX font) to match the paper's text. Set plt.rcParams['font.family'] = 'serif'.
- Enable LaTeX rendering if complex math is involved: plt.rcParams['text.usetex'] = True (Note: skip if the environment lacks LaTeX binaries).
- Font Sizing (assuming a standard IEEE 2-column format):
  - Axis Labels: 14-16pt
  - Tick Labels (Numbers): 12-14pt
  - Legend: 12-14pt
  - Title: Only if explicitly requested.

### 4. STATISTICAL RIGOR (Mandatory for CS Papers)
- Never plot a single run without variance if multiple seeds/runs are available.
- Line Charts: If plotting mean performance over time/epochs, ALWAYS include a shaded region (ill_between) representing the Standard Deviation or 95% Confidence Interval. Use lpha=0.2 for the shaded area.
- Bar Charts: MUST include Error Bars (yerr) with caps (capsize=4).

### 5. TABLE RULES (Strict LaTeX Standards)
- NEVER generate image-based tables or Markdown tables for final output. Always generate LaTeX code.
- Package strictly required: \usepackage{booktabs}, \usepackage{multirow}.
- Lines: Use ONLY \toprule, \midrule, and \bottomrule. 
- NEVER USE VERTICAL LINES (|) in academic tables.
- Emphasizing Results: 
  - BEST result in a column/row must be **\textbf{bold}**.
  - SECOND-BEST result must be \underline{underlined}.
- Decimal Alignment: Format numerical values consistently.

## 10. Mathematical Notation & Derivation Rules (A* Paper Standard)

### 10.1 Notation Standards (ISO/IEEE)
- **Italic lowercase** ($x, \theta, \psi$): Exclusively for scalar variables.
- **Bold lowercase** ($\mathbf{x}, \mathbf{u}, \mathbf{y}$): Exclusively for vectors.
- **Bold uppercase** ($\mathbf{A}, \mathbf{B}, \mathbf{Q}, \mathbf{R}$): Exclusively for matrices.
- **Equation numbering**: All standalone equations MUST be enclosed within `\begin{equation}` and `\end{equation}` to ensure right-aligned numbering for cross-referencing.

### 10.2 No Naked Variables (Domain Declaration)
- Every variable, vector, or matrix MUST be explicitly defined with its mathematical domain ($\in \mathbb{R}^n$) immediately upon its first appearance.
- Example: "Consider the augmented state-space model where $\mathbf{x} \in \mathbb{R}^6$ represents the state vector, and $\mathbf{u} \in \mathbb{R}^2$ denotes the control input."

### 10.3 Formal Physical Assumptions
- Physical constraints (e.g., voltage saturation, noise bounds) MUST be formalized within a `\begin{assumption}` block (or formatted as such if using raw Markdown).
- Example: > **Assumption 1.** *The environmental wind perturbation $\mathbf{d}(t)$ is bounded such that $\|\mathbf{d}(t)\| \le d_{\max}$.*

### 10.4 Mathematical Narrative Flow
- Treat standalone equations as part of the surrounding sentence. Append a comma (,) at the end of the equation if the sentence continues (e.g., to define variables), or a period (.) if the sentence concludes.
- **Academic Connectors:** Do not stack equations without connecting text. Use rigorous transitional phrases such as "Substituting (X) into (Y), yields...", "Differentiating with respect to...", or "By invoking Lemma 1, it follows that...".

### 10.5 Linearization Rigor
- When describing the transition from a non-linear physical model to a linear state-space representation (e.g., for LQR), you MUST explicitly formulate the first-order Taylor series expansion using Jacobian matrices around the equilibrium point $\mathbf{x}_0 = \mathbf{0}, \mathbf{u}_0 = \mathbf{0}$:
  $$\mathbf{A} = \left. \frac{\partial f(\mathbf{x}, \mathbf{u})}{\partial \mathbf{x}} \right|_{\mathbf{x}_0, \mathbf{u}_0}, \quad \mathbf{B} = \left. \frac{\partial f(\mathbf{x}, \mathbf{u})}{\partial \mathbf{u}} \right|_{\mathbf{x}_0, \mathbf{u}_0}$$

## 11. Bilingual Technical Writing Rules (Vietnamese - English)

When writing R&D Technical Reports in Vietnamese, strictly adhere to the following rules to ensure academic rigor and avoid literal, clumsy translations:

### 11.1 No Literal Translation (Giữ nguyên gốc + Mở ngoặc)
- Never translate core algorithm names or international methods into Vietnamese. Keep them in English and append the acronym in parentheses at first mention.
- Example: Use "Thuật toán Particle Swarm Optimization (PSO)" instead of "Thuật toán tối ưu hóa bầy đàn". For subsequent mentions, use the acronym (e.g., "PSO").

### 11.2 Mandatory Terminology Mapping (Bảng Mapping bắt buộc)
- You MUST strictly use the following Vietnamese R&D vocabulary:
  - "Cross-coupling effect" -> "Hiện tượng tương tác chéo" (or "ảnh hưởng liên kênh")
  - "Gain Scheduling" -> "Cơ chế tuyến tính hóa từng vùng" (or "phân đoạn tăng ích")
  - "Robustness" -> "Độ bền vững" (or "tính bền vững của hệ thống")
  - "Actuator Saturation" -> "Bão hòa cơ cấu chấp hành"
  - "State-Feedback" -> "Phản hồi trạng thái toàn phần"
  - "Feed-forward control" -> "Điều khiển tiền định" (or "bù tiền định")
  - "Overshoot" -> "Độ vọt lố"
  - "Settling time" -> "Thời gian xác lập"
  - "Transient response" -> "Đáp ứng quá độ"
- Do NOT use clumsy translations like "ghép chéo", "bắn quá bến", "thời gian lắng", "bão hòa bộ kích hoạt", etc.

### 11.3 Natural Sentence Flow (Động từ hóa linh hoạt)
- Do not stick rigidly to English noun-adjunct structures. Smooth the text by adding operational verbs like "quá trình", "khảo sát", "đánh giá", "thực thi".
- Example: Instead of "Xác thực mô phỏng trong vòng lặp", write "Quá trình kiểm chứng và đánh giá trên môi trường mô phỏng vòng lặp kín (Simulation-in-the-loop)".

### 11.4 Object-Oriented Syntax (Cấu trúc Chủ động và Khách quan)
- Never use personal pronouns ("Tôi", "Chúng tôi", "Nhóm nghiên cứu").
- Ensure the system, the algorithm, or the mathematical model serves as the active subject of the sentence.
- Example: "Thuật toán LQR chủ động tính toán và điều tiết biên độ điện áp nạp vào cơ cấu chấp hành" instead of "Chúng tôi dùng thuật toán LQR để tính ra điện áp".

### 11.5 Acronym Control (Quản lý từ viết tắt)
- Each time an English acronym (e.g., MIMO, SISO, LQR, PID) is used in a Vietnamese sentence, automatically check if it was defined previously in the chapter. If not, write it out explicitly.
- Example: "...hệ thống điều khiển đa biến Multi-Input Multi-Output (MIMO)..."

## 12. Pseudocode and Figures/Diagrams Strict Rules (A* Standard)

## 💻 PHẦN 1: Các Quy tắc viết Mã giả (Pseudocode) chuẩn A*

Nhật hãy ép Agent sử dụng môi trường chuẩn trong LaTeX (như gói `algorithm2e` hoặc `algorithmicx`) và tuân thủ các luật sau:

### Rule 1: Khai báo tường minh Input/Output (Không nhảy bổ vào viết lệnh)

Mở đầu thuật toán luôn luôn phải có hai phần: **Input** (Dữ liệu đầu vào, hằng số cấu hình) và **Output** (Kết quả thuật toán nhè ra sau khi kết thúc).

* **Yêu cầu:** Tất cả biến số trong Input/Output phải ghi rõ miền không gian toán học ($\in \mathbb{R}$).
* *Ví dụ:* * **Input:** Ma trận hệ thống $\tilde{\mathbf{A}}, \tilde{\mathbf{B}}$, ma trận phạt $\mathbf{Q} \in \mathbb{R}^{6\times6}, \mathbf{R} \in \mathbb{R}^{2\times2}$, kích thước bầy đàn $N_p$, số vòng lặp tối đa $I_{\max}$.
* **Output:** Ma trận tăng ích tối ưu $\mathbf{K}^* \in \mathbb{R}^{2\times6}$.

### Rule 2: Toán học hóa biến số (Cấm dùng biến phong cách lập trình)

Mã giả trong paper A* bắt buộc phải đồng bộ 100% với các ký hiệu ký tự ở chương lý thuyết. Không được giữ nguyên tên biến kiểu code Dev.

* **Sai (Cấm dùng):** `theta_dot = update_speed()`, `error_p = ref - cur`, `if V_pitch > 24:`
* **Đúng (Bắt buộc):** $\dot{\theta} \leftarrow \text{UpdateSpeed}()$, $\mathbf{e}_p \leftarrow \theta_d - \theta$, **if** $V_p > 24$ **then**

### Rule 3: Sử dụng các hàm toán học trừu tượng thay vì viết chi tiết code nền

Mã giả sinh ra để người ta hiểu **Tư duy thuật toán**, không phải để máy tính chạy trực tiếp. Do đó, các bước tính toán trung gian nên được viết dưới dạng các hàm toán học (Operators).

* *Ví dụ:* Thay vì viết một vòng lặp dài để nhân ma trận tính tổng điểm phạt sai số ITAE, hãy viết gọn:

$$\text{Fitness}_i \leftarrow \text{EvaluateCost}(\mathbf{x}_i, \mathbf{u}_i)$$

Hoặc phép giải Riccati: $\mathbf{P} \leftarrow \text{SolveRiccati}(\tilde{\mathbf{A}}, \tilde{\mathbf{B}}, \mathbf{Q}, \mathbf{R})$.

### Rule 4: Quy ước ký hiệu gán và đánh số dòng rõ ràng

* Sử dụng mũi tên trái `<-` hoặc `\leftarrow` cho phép gán giá trị (Assignment), hạn chế dùng dấu `=` vì dấu `=` trong toán học dùng cho phương trình thiết lập.
* Tất cả các dòng lệnh logic trong vòng lặp (`for`, `while`, `if-else`) phải được đánh số thứ tự tự động để phần thuyết minh trong văn bản chính dễ dàng trích dẫn (ví dụ: *"Như được mô tả tại Dòng 5 của Thuật toán 1..."*).

---

## 🖼️ PHẦN 2: Các Quy tắc hoàn thiện Hình ảnh và Đồ thị kết quả

Đối với đồ thị kết quả (Plots) và sơ đồ cấu trúc hệ thống (Diagrams), Agent phải kiểm tra các tiêu chuẩn khắt khe sau:

### Rule 1: Quy tắc "Độc lập Thông tin" của Caption (Self-Explanatory)

Reviewer hạng A* có thể không đọc toàn bộ bài của Nhật, nhưng họ sẽ nhìn hình và đọc Caption. Caption phải giải thích đầy đủ: **Tên hình + Kịch bản/Điều kiện thử nghiệm + Chỉ rõ các đường màu đại diện cho cái gì.**

* **Cấm viết:** `\caption{Đồ thị đáp ứng góc Pitch.}`
* **Phải viết:** `\caption{Đáp ứng động học của góc Pitch ($\theta$) dưới tác động của mô-men nhiễu gió ngẫu nhiên, so sánh đối chứng giữa cấu trúc đề xuất Augmented LQR (đường nét liền xanh) và bộ điều khiển AI-PID (đường nét đứt đỏ).}`

### Rule 2: Thống nhất Typography (Font chữ) giữa Hình và Văn bản

* Chữ inside hình ảnh (nhãn trục X, trục Y, chú thích Legend) **bắt buộc phải cùng họ Font với văn bản chính của paper** (thường là `Times New Roman` trong LaTeX).
* Kích thước chữ (Font size) trong hình không được nhỏ hơn quá 2pt so với text chính của bài báo (Đảm bảo khi co giãn hình vừa khít 1 cột, người đọc vẫn thấy rõ ràng mà không cần zoom).

### Rule 3: Vượt qua bài kiểm tra "In ấn Đen - Trắng" (Grayscale Test)

Không bao giờ phân biệt các đường tín hiệu chỉ bằng màu sắc. Bắt buộc phải phối hợp **Định dạng nét vẽ (Line Styles / Markers)**.

* *Cấu hình vẽ:* Đường mục tiêu (Reference) dùng nét đứt đen (`'k--'`), LQR dùng nét liền xanh (`'b-'`), PID dùng nét chấm gạch đỏ (`'r-.'`). Khi in ra giấy trắng đen, các đường này vẫn hiển thị tách biệt rõ ràng.

### Rule 4: Trích dẫn Vòng kín (No Naked Figures)

Không được có bất kỳ hình ảnh nào nằm bơ vơ. Mọi hình ảnh xuất hiện đều phải được gọi tên và phân tích định lượng trong văn bản chính bằng các trạng từ kết nối học thuật.

* Sử dụng nhãn chuẩn: **Hình 1**, **Hình 2** (hoặc **Fig. 1**, **Fig. 2**).
* **Văn phong chuẩn:** *"...hiện tượng tương tác chéo được triệt tiêu mượt mà như minh họa trong Hình \ref{fig:decoupling}, tại đó độ vọt lố giảm đáng kể..."* (Cấm dùng các từ như "hình dưới", "hình sau").


## 13. Experiment Rules (A* Standard)

### Rule 1: Minh bạch cấu hình nền tảng (Environmental & Parametric Transparency)
Mở đầu chương Experiment, Agent bắt buộc phải thiết lập một tiểu mục (Subsection) để khai báo toàn bộ thông số phần cứng và môi trường mô phỏng. Liệt kê đầy đủ thông số vật lý của trực thăng Quanser (khối lượng, chiều dài đòn, mô-men quán tính), thời gian trích mẫu ($\Delta t = 0.001	ext{s}$), thuật toán giải số vi phân (RK45), phần cứng chạy tối ưu. Phải ghi rõ phương trình hoặc phân phối của nhiễu gió và nhiễu cảm biến.

### Rule 2: Đa dạng hóa Quỹ đạo thử thách (Benchmark Trajectories)
Đánh giá trên tối thiểu 3 loại quỹ đạo có độ khó tăng dần:
1. **Square Wave (Sóng vuông):** Đánh giá phản xạ đáp ứng nhanh (Rise time) và khả năng dập tắt dao động.
2. **Sine Wave (Sóng Sin):** Đánh giá năng lực bám liên tục và độ trễ pha động học.
3. **Multi-step / Complex Path (Chuỗi bậc thang):** Đánh giá tính bền vững (Robustness) khi điểm cân bằng thay đổi liên tục.

### Rule 3: Quy tắc Đánh giá Định lượng (Quantitative Analysis Over Qualitative)
Tuyệt đối cấm viết các câu nhận xét mang tính cảm tính, chung chung. Tất cả các so sánh phải đi kèm số liệu phần trăm hoặc biên độ cụ thể từ bảng dữ liệu.

### Rule 4: Sử dụng Chỉ số Đánh giá Chuẩn mực Quốc tế (Standard Performance Metrics)
Chấm điểm bằng các chỉ số:
* **ITAE (Integral of Time-multiplied Absolute Error)**
* **SSE (Steady-State Error)**
* **CE (Control Effort)**
* **Rise Time ($), Settling Time ($), Maximum Overshoot ($)**

### Rule 5: Phương pháp luận Thống kê cho Thuật toán AI (Statistical Rigor)
Tuyệt đối không lấy kết quả của một lần chạy duy nhất. Bắt buộc chạy 30 lần độc lập (30 independent runs). Kết quả biểu diễn dưới dạng Giá trị trung bình $\pm$ Độ lệch chuẩn ($\mu \pm \sigma$).

### System Prompt for Experiment Section
1. ABSOLUTE TRANSPARENCY: Ensure a dedicated subsection details all physical parameters, solver settings, and noise bounds.
2. QUANTITATIVE ANALYSIS: Eliminate all vague, qualitative descriptions.
3. STANDARDIZED METRICS: Structure the discussion around formal control metrics.
4. STATISTICAL RIGOR: Enforce reporting of metrics using Mean $\pm$ Standard Deviation across multiple runs.
5. TRAJECTORY-SPECIFIC CRITIQUE: Differentiate analysis between step-response tracks and continuous tracking.

### Experiment Check-list
1. Đồng bộ hóa biến số trong bảng kết quả giống 100% biến số trong chương lý thuyết.
2. Làm sạch các số liệu bất thường.
3. Biểu đồ hội tụ (Convergence Plot) cho 4 thuật toán.
4. Đồ thị đổi sang font Times New Roman, phân biệt nét vẽ.
