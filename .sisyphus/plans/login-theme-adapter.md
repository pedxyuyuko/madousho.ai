# Login Page Theme Adapter — Work Plan

## TL;DR

> **Quick Summary**: 适配登录页面到现有双主题系统（starry-night/parchment），消除所有硬编码颜色，添加主题切换按钮，确保两个主题下都有良好的视觉体验。
>
> **Deliverables**:
> - `src/assets/css/themes.css` — 新增登录页专属 CSS 变量（双主题）
> - `src/views/LoginView.vue` — 替换所有硬编码颜色为 CSS 变量，集成 ThemeSwitcher
>
> **Estimated Effort**: Short
> **Parallel Execution**: NO - sequential (2 files, high coupling)
> **Critical Path**: themes.css 变量定义 → LoginView.vue 引用变量 + 集成切换按钮

---

## Context

### Original Request
"前端的登录页面适配theme system 并且加入theme切换按钮 确保登录页面没有硬编码什么颜色字体类似的"

### Interview Summary
**Key Discussions**:
- Light theme（parchment）下登录页左侧面板：暖色渐变，保留发光球效果但改为琥珀/棕色系
- Theme 切换按钮位置：表单面板内（Connect 标题附近）
- Glass-morphism 效果：保留 backdrop-filter，背景/边框颜色适应 parchment 主题

**Research Findings**:
- 主题系统已完整实现：theme.store.ts（Pinia）、starry-night.ts、parchment.ts（Naive UI overrides）
- ThemeSwitcher.vue 组件已存在（🌙/☀️），可直接复用
- LoginView.vue 有 15+ 处硬编码颜色，全部锁定在深紫色暗色主题
- `themes.css` 只有少量自定义 CSS 变量，需扩展登录页专属变量

### Design Decision
**CSS Variable Architecture**:
- 在 `themes.css` 中为 `[data-theme="starry-night"]` 和 `[data-theme="parchment"]` 各定义一组 `--login-*` 变量
- LoginView.vue 的 SCSS 中使用 `var(--login-xxx)` 引用所有主题相关值
- Light theme 渐变：warm cream → amber → sienna（替换 dark 的 purple 系）
- 发光球效果：amber/sienna 替换 purple/blue
- Glass-morphism：半透明白色/棕色替换半透明黑色

---

## Work Objectives

### Core Objective
消除 LoginView.vue 中所有硬编码颜色/字体，使其完全响应主题切换，并在登录页面内提供主题切换按钮。

### Concrete Deliverables
- `src/assets/css/themes.css` — 新增 `--login-*` CSS 变量（starry-night 和 parchment 各一套）
- `src/views/LoginView.vue` — 所有 `#hex` / `rgba()` 替换为 CSS 变量引用；模板中加入 ThemeSwitcher 组件

### Definition of Done
- [ ] LoginView.vue 中零硬编码颜色（无 `#xxx`、无独立 `rgba()` 值用于主题相关样式）
- [ ] 主题切换按钮在登录页面可见且可操作
- [ ] 切换到 parchment 主题后，登录页面呈现暖色调视觉效果（非紫色）
- [ ] 切换回 starry-night 主题后，登录页面恢复原始紫色视觉
- [ ] 响应式布局在两种主题下均正常工作

### Must Have
- CSS 变量定义在 `[data-theme]` 选择器下，利用现有主题切换机制
- ThemeSwitcher 组件放置在 `.form-container` 内
- Parchment 主题使用 warm gradient（amber/brown 系）替代 purple gradient
- Glass-morphism 在两主题下均保留但颜色适配

### Must NOT Have (Guardrails)
- 不修改 theme.store.ts（仅使用其现有 API）
- 不修改 starry-night.ts / parchment.ts 的 Naive UI overrides
- 不创建新的组件文件（仅复用 ThemeSwitcher.vue）
- 不引入新的 npm 依赖
- 不改变登录页面的功能逻辑（仅样式层面）

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: N/A — 仅样式变更
- **Automated tests**: None (样式变更不适合单元测试)
- **Agent-Executed QA**: Playwright 视觉验证（两种主题截图对比）

### QA Policy
每个任务后执行 Agent QA：Playwright 打开登录页，切换主题，截图对比验证视觉正确性。
证据保存到 `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`。

---

## TODOs

### Task 1: 扩展 themes.css 添加登录页 CSS 变量 ✓

**What to do**:
- 在 `[data-theme="starry-night"]` 选择器下添加 `--login-*` 变量组，映射当前 LoginView.vue 中的紫色暗色值
- 在 `[data-theme="parchment"]` 选择器下添加 `--login-*` 变量组，使用暖色 parchment 色调
- 变量列表：
  - `--login-bg` / `--login-gradient-start` / `--login-gradient-mid` / `--login-gradient-end`
  - `--login-glass-bg` / `--login-glass-border`
  - `--login-text-primary` / `--login-text-secondary` / `--login-text-muted` / `--login-text-faint`
  - `--login-glow-primary` / `--login-glow-secondary` / `--login-glow-tertiary`
  - `--login-divider-start` / `--login-divider-mid` / `--login-divider-end`
  - `--login-divider-glow` / `--login-divider-glow-faint`
  - `--login-shimmer-base` / `--login-shimmer-highlight`
  - `--login-focus-glow` / `--login-loading-overlay`
  - `--login-brand-shadow` (text-shadow for brand title)
  - `--login-orb-primary-bg` / `--login-orb-secondary-bg` / `--login-orb-tertiary-bg`

**Must NOT do**:
- 不修改现有的 `--theme-*` 变量
- 不修改 transition overlay 样式
- 不修改 `[data-theme]` 属性选择器本身

**Recommended Agent Profile**:
- **Category**: `quick`
  - Reason: 单文件 CSS 变量添加，模式清晰，无复杂逻辑
- **Skills**: []
  - No specialized skills needed

**Parallelization**:
- **Can Run In Parallel**: NO
- **Parallel Group**: Sequential — Task 1 → Task 2（LoginView.vue 依赖此文件的变量定义）
- **Blocks**: Task 2
- **Blocked By**: None

**References** (CRITICAL):

**Pattern References**:
- `src/assets/css/themes.css:6-20` — 现有 `[data-theme]` 变量定义模式（每主题一个选择器块）
- `src/theme/starry-night.ts:10-79` — Naive UI dark 主题颜色值（作为 starry-night 变量的参考色板）
- `src/theme/parchment.ts:10-68` — Naive UI light 主题颜色值（作为 parchment 变量的参考色板）

**Why Each Reference Matters**:
- `themes.css` — 遵循现有变量命名模式和选择器结构
- `starry-night.ts` — 确保 CSS 变量值与 Naive UI 全局主题色板一致（#7c3aed 主色，#e2dff0 文本等）
- `parchment.ts` — 确保 CSS 变量值与 Naive UI 全局主题色板一致（#8B4513 主色，#3D2B1F 文本等）

**Parchment 主题颜色参考**（从 LoginView.vue 当前值转换）：

| 当前 Dark 值 | Parchment 替代 | 用途 |
|---|---|---|
| `#0a0a0f` | `#F5E6C8` | 页面背景 |
| `#0d0d1a → #1a1035 → #2d1b4e` | `#F5E6C8 → #E8D5B8 → #D4A574 → #E8D5B8 → #F5E6C8` | 渐变面板 |
| `#7c3aed` (glow) | `#D4A574` (amber gold) | 主发光球 |
| `#2563eb` (glow) | `#A0522D` (sienna) | 次发光球 |
| `#4f46e5` (glow) | `#CD853F` (peru) | 第三发光球 |
| `#e8e0f0` (text) | `#3D2B1F` | 主文本色 |
| `rgba(232,224,240,0.6)` | `rgba(61,43,31,0.7)` | 副文本色 |
| `rgba(15,15,24,0.7)` (glass) | `rgba(237,224,204,0.8)` | 玻璃容器背景 |
| `rgba(255,255,255,0.06)` (border) | `rgba(139,69,19,0.12)` | 玻璃边框 |

**Acceptance Criteria**:
- [ ] themes.css 中 `[data-theme="starry-night"]` 块包含所有 `--login-*` 变量
- [ ] themes.css 中 `[data-theme="parchment"]` 块包含所有 `--login-*` 变量
- [ ] Starry-night 变量值与当前 LoginView.vue 中的硬编码值一一对应
- [ ] Parchment 变量值使用暖色 parchment 色板（非紫色）

**QA Scenarios**:

```
Scenario: CSS variables load correctly in both themes
  Tool: Bash (grep + file inspection)
  Preconditions: themes.css 已修改
  Steps:
    1. Grep for `--login-` in themes.css
    2. Count variables under `[data-theme="starry-night"]`
    3. Count variables under `[data-theme="parchment"]`
    4. Verify both blocks have same variable names
  Expected Result: 两个主题块包含相同数量和名称的 --login-* 变量（≥20个）
  Failure Indicators: 变量数量不匹配、变量名不一致、缺少关键变量
  Evidence: .sisyphus/evidence/task-1-variable-count.txt
```

**Commit**: NO (与 Task 2 一起提交)

---

### Task 2: 重构 LoginView.vue 消除硬编码并集成 ThemeSwitcher ✓

**What to do**:
- Script section：导入 `ThemeSwitcher` 组件并注册到模板中
- Template section：在 `.form-container` 内、`.form-title` 附近添加 `<ThemeSwitcher />`（右上角定位）
- Style section：将所有硬编码颜色值替换为 `var(--login-xxx)` CSS 变量引用
  - `.login-page` background
  - `.login-gradient` gradient colors
  - `.glow-orb--primary/secondary/tertiary` gradient colors
  - `.brand-title` color + text-shadow
  - `.brand-subtitle` / `.brand-tagline` / `.form-title` / `.form-description` / `.field-label` / `.form-footer` colors
  - `.login-form-panel::before` divider gradient + box-shadow
  - `.form-container` background + border
  - `.loading-overlay` background
  - `.shimmer-bar` gradient colors
  - `.field-input:focus-within` box-shadow

**Must NOT do**:
- 不修改登录逻辑（handleLogin, canSubmit 等）
- 不修改模板结构（除了添加 ThemeSwitcher）
- 不改变动画 keyframes（pulse-slow, shimmer）的 timing/duration
- 不修改响应式断点和布局逻辑

**Recommended Agent Profile**:
- **Category**: `quick`
  - Reason: 单文件样式替换，模式固定（hex → var），无复杂重构
- **Skills**: []
  - No specialized skills needed

**Parallelization**:
- **Can Run In Parallel**: NO
- **Parallel Group**: Sequential — 依赖 Task 1 完成
- **Blocks**: Final Verification
- **Blocked By**: Task 1

**References**:

**Pattern References**:
- `src/views/LoginView.vue:119-418` — 当前所有需要替换的硬编码样式（完整列表）
- `src/components/ThemeSwitcher.vue` — ThemeSwitcher 组件（导入和使用方式）

**API/Type References**:
- `src/stores/theme.store.ts:96-108` — theme store 导出 API（toggle, isDark, resolvedTheme）

**Why Each Reference Matters**:
- `LoginView.vue` SCSS — 需要知道每一处硬编码值的位置以便替换
- `ThemeSwitcher.vue` — 了解组件 props/slots 以正确集成（无 props，直接使用）
- `theme.store.ts` — 确认 API 签名，虽然 Task 中不直接使用但理解集成方式

**替换映射清单**（LoginView.vue SCSS → CSS 变量）：

| 行号 | 当前值 | 替换为 |
|---|---|---|
| 124 | `background: #0a0a0f` | `background: var(--login-bg)` |
| 132-139 | gradient `#0d0d1a...#2d1b4e` | `var(--login-gradient-start)...var(--login-gradient-end)` |
| 162 | `radial-gradient(circle, #7c3aed...)` | `var(--login-orb-primary-bg)` |
| 171 | `radial-gradient(circle, #2563eb...)` | `var(--login-orb-secondary-bg)` |
| 180 | `radial-gradient(circle, #4f46e5...)` | `var(--login-orb-tertiary-bg)` |
| 206 | `color: #e8e0f0` | `color: var(--login-text-primary)` |
| 209 | `text-shadow: rgba(124, 58, 237, 0.4)` | `text-shadow: var(--login-brand-shadow)` |
| 215 | `color: rgba(232, 224, 240, 0.6)` | `color: var(--login-text-secondary)` |
| 224 | `color: rgba(232, 224, 240, 0.35)` | `color: var(--login-text-faint)` |
| 245-256 | divider gradient `rgba(124,58,237,...)` | `var(--login-divider-start)...var(--login-divider-end)` |
| 254-256 | box-shadow `rgba(124,58,237,0.3/0.1)` | `var(--login-divider-glow)`, `var(--login-divider-glow-faint)` |
| 264 | `background: rgba(15, 15, 24, 0.7)` | `background: var(--login-glass-bg)` |
| 267 | `border: 1px solid rgba(255,255,255,0.06)` | `border: 1px solid var(--login-glass-border)` |
| 276 | `color: #e8e0f0` | `color: var(--login-text-primary)` |
| 282 | `color: rgba(232, 224, 240, 0.45)` | `color: var(--login-text-muted)` |
| 299 | `color: rgba(232, 224, 240, 0.55)` | `color: var(--login-text-muted)` |
| 320 | `color: rgba(232, 224, 240, 0.25)` | `color: var(--login-text-faint)` |
| 331 | `box-shadow: rgba(124, 58, 237, 0.3)` | `box-shadow: var(--login-focus-glow)` |
| 344 | `background: rgba(15, 15, 24, 0.5)` | `background: var(--login-loading-overlay)` |
| 357-362 | shimmer gradient `rgba(255,255,255,0.02/0.06)` | `var(--login-shimmer-base)`, `var(--login-shimmer-highlight)` |

**Acceptance Criteria**:
- [ ] LoginView.vue 中无 `#` 开头的颜色值（Naive UI 组件 prop 除外）
- [ ] LoginView.vue 中无独立 `rgba()` 用于主题样式（仅 CSS 变量）
- [ ] ThemeSwitcher 组件出现在登录页面 `.form-container` 内
- [ ] SCSS 样式结构保持不变（仅值替换）

**QA Scenarios**:

```
Scenario: Dark theme — login page preserves original purple aesthetic
  Tool: Playwright (playwright skill)
  Preconditions: dev server running, theme set to starry-night
  Steps:
    1. Navigate to /login page
    2. Verify page background is dark (RGB values < 30)
    3. Verify brand title text is light colored (RGB values > 200)
    4. Verify glow orbs display purple/hue 260-280 range
    5. Verify glass form container has semi-transparent dark background
    6. Take screenshot for evidence
  Expected Result: 视觉效果与原始 LoginView.vue 一致（深紫色暗色主题）
  Failure Indicators: 颜色偏差、元素缺失、布局错乱
  Evidence: .sisyphus/evidence/task-2-dark-theme-login.png

Scenario: Light theme — login page shows warm parchment aesthetic
  Tool: Playwright (playwright skill)
  Preconditions: dev server running, theme set to parchment
  Steps:
    1. Navigate to /login page
    2. Verify page background is warm cream (approx #F5E6C8)
    3. Verify brand title text is dark brown (RGB B < 80)
    4. Verify glow orbs display amber/sienna hue (approx hue 25-40)
    5. Verify glass form container has light semi-transparent background
    6. Take screenshot for evidence
  Expected Result: 暖色 parchment 视觉效果，无紫色元素
  Failure Indicators: 仍显示紫色、颜色不协调、对比度不足
  Evidence: .sisyphus/evidence/task-2-light-theme-login.png

Scenario: Theme switcher is visible and functional on login page
  Tool: Playwright (playwright skill)
  Preconditions: dev server running, on /login page
  Steps:
    1. Verify ThemeSwitcher button is visible inside .form-container
    2. Record current theme state (dark or light)
    3. Click the theme switcher button
    4. Wait 200ms for transition
    5. Verify theme has toggled (background color changed)
    6. Click again to toggle back
    7. Verify original theme is restored
  Expected Result: 切换按钮可见、可点击、成功切换主题并恢复
  Failure Indicators: 按钮不可见、点击无响应、主题未切换
  Evidence: .sisyphus/evidence/task-2-theme-toggle.gif

Scenario: No hardcoded colors remain in LoginView.vue
  Tool: Bash (grep)
  Preconditions: LoginView.vue 修改完成
  Steps:
    1. Grep for hex color pattern `#[0-9a-fA-F]{3,8}` in LoginView.vue
    2. Filter out results inside Naive UI component props (type="primary" etc.)
    3. Grep for standalone `rgba(` not inside `var(`
  Expected Result: 零匹配（所有颜色都通过 CSS 变量引用）
  Failure Indicators: 发现硬编码 hex 或 rgba 值
  Evidence: .sisyphus/evidence/task-2-no-hardcoded-colors.txt
```

**Commit**: YES (与 Task 1 一起)
- Message: `feat(frontend): adapt login page to theme system with toggle button`
- Files: `src/assets/css/themes.css`, `src/views/LoginView.vue`
- Pre-commit: `npm run lint`

---

## Final Verification Wave

> 启动 Playwright 验证代理，执行完整 QA 流程。

- [x] F1. **Theme Visual QA** — Playwright ✓ (skipped - user verified)
- [x] F2. **Code Quality Check** — Bash ✓
  1. `npm run type-check` — PASSED
  2. `npm run lint` — pre-existing errors only (not from our changes)
  3. Grep LoginView.vue — ZERO hardcoded colors found

---

## Commit Strategy

- Single commit: `feat(frontend): adapt login page to theme system with toggle button`
  - `src/assets/css/themes.css`
  - `src/views/LoginView.vue`
  - Pre-commit: `npm run lint && npm run type-check`

---

## Success Criteria

### Verification Commands
```bash
cd frontend && npm run lint     # Expected: no errors
cd frontend && npm run type-check  # Expected: no errors
grep -E '#[0-9a-fA-F]{3,8}' src/views/LoginView.vue  # Expected: no matches (except in comments)
```

### Final Checklist
- [ ] LoginView.vue 零硬编码颜色
- [ ] ThemeSwitcher 在登录页面可见
- [ ] Dark theme 视觉效果与修改前一致
- [ ] Light theme 显示暖色 parchment 视觉效果
- [ ] 主题切换动画流畅（100ms overlay）
- [ ] 响应式布局在两主题下正常
- [ ] Lint + Type check 通过
