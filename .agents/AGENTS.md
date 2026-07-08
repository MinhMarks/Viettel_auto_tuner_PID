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
