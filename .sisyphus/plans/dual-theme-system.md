# Dual Theme System — Starry Night & Parchment

## TL;DR

> **Quick Summary**: Implement a complete dual-theme system for Madousho.ai using Naive UI's NConfigProvider. Dark theme ("Starry Night") features deep purple/magic blue tones with subtle glow animations. Light theme ("Parchment") uses medieval CSS noise texture with warm brown/amber palette.
>
> **Deliverables**:
> - Theme store (Pinia) with localStorage persistence + system preference listener
> - Two complete GlobalThemeOverrides definitions
> - NConfigProvider + NGlobalStyle integration in App.vue
> - ThemeSwitcher component (sun/moon toggle in Header)
> - CSS complement system (SVG noise texture + gradient backgrounds)
> - FOUC prevention (inline theme init before Vue mount)
> - LoginView excluded from theme system (stays dark always)
>
> **Estimated Effort**: Medium
> **Parallel Execution**: YES - 3 waves
> **Critical Path**: Task 1 → Task 5 → Task 6 → Task 8 → F1-F3

---

## Context

### Original Request
用户要求设计两套 Naive UI 全局主题：一套暗色模拟星空+魔法（神秘感），一套亮色设计成中世纪羊皮纸风格。

### Interview Summary
**Key Discussions**:
- Theme switching: 系统偏好自动跟随 + 手动覆盖（Header 按钮）
- 星空主题: 轻量渐变/微光动画，不需要重粒子效果
- 羊皮纸主题: CSS 噪点模拟纹理，不用图片
- Persistence: localStorage 持久化用户选择

**Research Findings**:
- Naive UI 通过 `NConfigProvider` + `theme-overrides` 实现主题定制
- `darkTheme` 对象提供暗色基础，`null` 为亮色
- `NGlobalStyle` 组件确保样式正确注入
- 项目使用 Pinia 状态管理，有 localStorage 持久化模式参考

### Metis Review (Gaps Addressed)
- **LoginView scope**: EXCLUDED — stays dark always, pre-auth no toggle needed
- **FOUC prevention**: Theme store init BEFORE app mount in main.ts
- **CSS noise texture**: SVG feTurbulence data URI (opacity 0.03-0.05)
- **System preference live listener**: `matchMedia` change event in store
- **Store pattern**: 独立的 theme.store.ts，localStorage key: `madousho_theme`，同步初始化防 FOUC

---

## Work Objectives

### Core Objective
为 Madousho.ai 前端创建完整的双主题切换系统，包含暗色（星空魔法）和亮色（羊皮纸）两套 Naive UI 主题配置。

### Concrete Deliverables
- `frontend/src/stores/theme.store.ts` — 主题状态管理
- `frontend/src/theme/starry-night.ts` — 星空暗色主题配置
- `frontend/src/theme/parchment.ts` — 羊皮纸亮色主题配置
- `frontend/src/theme/index.ts` — 主题统一导出
- `frontend/src/components/ThemeSwitcher.vue` — 主题切换按钮组件
- `frontend/src/assets/css/themes.css` — CSS 补充样式（动画、纹理）
- `frontend/src/App.vue` — 集成 NConfigProvider + NGlobalStyle

### Definition of Done
- [ ] 用户可以手动切换主题，刷新后保持选择
- [ ] 默认跟随系统 prefers-color-scheme（matchMedia 监听）
- [ ] 暗色主题: 深紫/魔法蓝调色，微光渐变动画
- [ ] 亮色主题: 羊皮纸 SVG 噪点纹理，墨棕调色
- [ ] 所有 Naive UI 组件（Button, Input, Card 等）正确应用主题
- [ ] LoginView 保持现有暗色风格（不在主题系统内）
- [ ] 无 FOUC 闪烁（主题初始化在 Vue mount 之前）

### Must Have
- NConfigProvider 包裹根组件 + NGlobalStyle
- 两套完整的 GlobalThemeOverrides（common 级别）
- localStorage 持久化 + 系统偏好实时监听
- Header 切换按钮（sun/moon 图标）
- 系统偏好检测 + 手动覆盖逻辑（手动优先）
- 主题 store 在 main.ts 中早于 app.mount() 初始化

### Must NOT Have (Guardrails)
- 不要引入新的 npm 依赖（仅用 naive-ui 现有能力）
- 不要为每个组件单独定制主题（只用 common 级别）
- 不要加载外部字体文件（使用系统字体栈）
- 不要使用重动画/粒子效果（保持轻量渐变/微光）
- 不要修改 LoginView.vue（始终暗色，不在主题系统内）
- 不要使用 `:deep()` 覆盖 Naive UI 内部样式（只用 themeOverrides）
- 不要使用 `!important`

---

## Verification Strategy (MANDATORY)

### Test Decision
- **Infrastructure exists**: YES (Vitest + Vue Test Utils)
- **Automated tests**: YES (Tests-after)
- **Framework**: Vitest
- **Tests**: 主题 store 逻辑测试 + 组件渲染测试

### QA Policy
- **Frontend/UI**: Playwright — 验证主题切换、颜色变化、持久化
- **Store Logic**: Vitest — 测试主题 store 的切换和持久化逻辑

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Foundation — all independent):
├── Task 1: Theme store (Pinia) with localStorage
├── Task 2: Starry Night theme definition
├── Task 3: Parchment theme definition
└── Task 4: CSS complement styles (animations + textures)

Wave 2 (Integration — depends on Wave 1):
├── Task 5: NConfigProvider + NGlobalStyle in App.vue (depends: 1, 2, 3)
├── Task 6: ThemeSwitcher component (depends: 1)
└── Task 7: Theme index.ts + exports (depends: 2, 3)

Wave 3 (Adaptation — depends on Wave 2):
├── Task 8: main.ts early theme init (FOUC prevention) (depends: 1, 5)
└── Task 9: Header integration + responsive (depends: 5, 6)

Wave FINAL:
├── F1: Visual QA (both themes, all pages)
├── F2: Store persistence verification
└── F3: System preference detection test
```

### Dependency Matrix
- **1** → 5, 6
- **2, 3** → 5, 7
- **4** → (no blocks, CSS only)
- **5** → 8, 9
- **6** → 9
- **7** → (no blocks)
- **8, 9** → FINAL

### Agent Dispatch Summary
- **Wave 1**: 4 parallel (T1 quick, T2-T4 unspecified-low)
- **Wave 2**: 3 parallel (T5 unspecified-high, T6-T7 quick)
- **Wave 3**: 2 parallel (T8 quick, T9 unspecified-low)
- **FINAL**: 3 parallel (F1-F3 unspecified-high)

---

## TODOs

- [x] 1. Theme Store (Pinia) with localStorage persistence

  **What to do**:
  - Create `frontend/src/stores/theme.store.ts` — 独立的主题 store，与 auth 完全无关
  - State:
    - `userPreference: 'starry-night' | 'parchment' | null` (null = 跟随系统)
    - `systemPreference: 'starry-night' | 'parchment'` (从 matchMedia 读取)
  - Computed:
    - `resolvedTheme` — userPreference ?? systemPreference
    - `isDark` — resolvedTheme === 'starry-night'
    - `naiveTheme` — darkTheme object 或 null（供 NConfigProvider 使用）
  - Actions:
    - `setTheme(name)` — 设置 userPreference，持久化，更新 data-theme 属性
    - `resetToSystem()` — 清除 userPreference，恢复跟随系统
    - `toggle()` — starry-night ↔ parchment 切换
    - `loadFromStorage()` — 从 localStorage 读取，同步设置 data-theme
    - `initSystemListener()` — 监听 matchMedia 变化，仅在 userPreference 为 null 时响应
  - 持久化: `localStorage.setItem('madousho_theme', JSON.stringify({ userPreference }))`
  - FOUC 防止: `loadFromStorage()` 内同步设置 `document.documentElement.setAttribute('data-theme', ...)`
  - 导出: 从 `frontend/src/stores/index.ts` 重新导出
  - 测试: `frontend/src/stores/__tests__/theme.store.test.ts`

  **Must NOT do**:
  - 不要引用 auth 相关的任何代码（这是独立的主题 store）
  - 不要硬编码主题颜色到 store 中（颜色在主题定义文件里）
  - 不要使用 CSS 变量名作为 store 状态

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Pinia store with localStorage, straightforward logic
  - **Skills**: []
    - No special skills needed, pure logic

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 2, 3, 4)
  - **Blocks**: Task 5, Task 6
  - **Blocked By**: None

  **References** (CRITICAL):

  **Pattern References** (仅参考 Pinia 语法和 localStorage 持久化模式):
  - `frontend/src/stores/counter.ts` — Pinia setup store 基本结构（defineStore + ref）

  **API/Type References**:
  - `naive-ui` exports: `darkTheme` — 暗色主题基础对象（供 NConfigProvider 使用）
  - `window.matchMedia('(prefers-color-scheme: dark)')` — 系统暗色偏好检测

  **Acceptance Criteria**:
  - [ ] Store file created at `frontend/src/stores/theme.store.ts`
  - [ ] Test file created at `frontend/src/stores/__tests__/theme.store.test.ts`
  - [ ] `npm run test:unit -- --run theme.store` passes all tests

  **QA Scenarios**:

  ```
  Scenario: Theme store initializes from localStorage
    Tool: Vitest
    Preconditions: localStorage has `madousho_theme: {"userPreference":"starry-night"}`
    Steps:
      1. Create store instance
      2. Assert currentTheme is 'starry-night'
      3. Assert isDark is true
    Expected Result: Store loads saved preference correctly
    Evidence: .sisyphus/evidence/task-1-store-init.txt

  Scenario: Theme toggle switches between themes
    Tool: Vitest
    Preconditions: Fresh store (no localStorage)
    Steps:
      1. Create store, assert default follows system preference
      2. Call toggle()
      3. Assert theme switched to opposite
      4. Call toggle() again
      5. Assert theme switched back
    Expected Result: Toggle correctly alternates themes
    Evidence: .sisyphus/evidence/task-1-store-toggle.txt

  Scenario: Theme persists to localStorage
    Tool: Vitest
    Preconditions: Fresh store
    Steps:
      1. Call setTheme('parchment')
      2. Read localStorage.getItem('madousho_theme')
      3. Assert JSON contains userPreference: 'parchment'
    Expected Result: Preference saved to localStorage
    Evidence: .sisyphus/evidence/task-1-store-persist.txt
  ```

  **Commit**: YES
  - Message: `feat(theme): add Pinia theme store with localStorage persistence`
  - Files: `frontend/src/stores/theme.store.ts`, `frontend/src/stores/__tests__/theme.store.test.ts`
  - Pre-commit: `cd frontend && npm run test:unit -- --run theme.store`

---

- [x] 2. Starry Night Dark Theme Definition

  **What to do**:
  - Create `frontend/src/theme/starry-night.ts`
  - Export `starryNightOverrides: GlobalThemeOverrides` object
  - common section: deep purple primary (#7c3aed), magic blue info (#6366f1), star gold warning (#fbbf24)
  - Background: bodyColor `#0a0a14`, cardColor `rgba(18, 16, 31, 0.85)`, inputColor `rgba(18, 16, 31, 0.6)`
  - Text: textColor1 `#e2dff0`, textColor2 `rgba(226, 223, 240, 0.65)`
  - Border: borderColor `rgba(124, 58, 237, 0.2)`, dividerColor `rgba(124, 58, 237, 0.15)`
  - Scrollbar: scrollbarColor `rgba(124, 58, 237, 0.3)`
  - Font: fontFamily `'Noto Sans SC', sans-serif`
  - Component overrides: Button (glow hover), Input (border glow), Card (backdrop)

  **Must NOT do**:
  - 不要覆盖 naive-ui 的 darkTheme 基础（这个是 themeOverrides，不是 theme）
  - 不要设置 animation 相关属性（动画在 CSS 文件中）

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
    - Reason: Pure configuration object definition, no complex logic
  - **Skills**: []
    - Theme token configuration only

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 3, 4)
  - **Blocks**: Task 5, Task 7
  - **Blocked By**: None

  **References**:
  - Naive UI `GlobalThemeOverrides` type — all available common tokens and component tokens
  - `frontend/src/views/LoginView.vue:132-140` — Existing purple gradient color palette to match

  **Acceptance Criteria**:
  - [ ] File created at `frontend/src/theme/starry-night.ts`
  - [ ] Exports `starryNightOverrides` typed as `GlobalThemeOverrides`
  - [ ] TypeScript compiles: `npx vue-tsc --noEmit` passes

  **QA Scenarios**:

  ```
  Scenario: Starry Night theme object is valid
    Tool: Bash (node REPL)
    Preconditions: None
    Steps:
      1. Import starryNightOverrides
      2. Assert common.primaryColor equals '#7c3aed'
      3. Assert common.bodyColor equals '#0a0a14'
      4. Assert common.textColor1 equals '#e2dff0'
    Expected Result: All color tokens match design spec
    Evidence: .sisyphus/evidence/task-2-starry-validate.txt

  Scenario: Starry Night has all required common tokens
    Tool: Bash (node REPL)
    Preconditions: Import starryNightOverrides
    Steps:
      1. Check common has: primaryColor, primaryColorHover, primaryColorPressed
      2. Check common has: infoColor, successColor, warningColor, errorColor
      3. Check common has: bodyColor, cardColor, inputColor
      4. Check common has: textColor1, textColor2, textColor3
      5. Check common has: borderColor, dividerColor
    Expected Result: All required tokens present (≥20 common tokens)
    Evidence: .sisyphus/evidence/task-2-starry-tokens.txt
  ```

  **Commit**: YES
  - Message: `feat(theme): add starry night dark theme definition`
  - Files: `frontend/src/theme/starry-night.ts`
  - Pre-commit: `cd frontend && npx vue-tsc --noEmit`

---

- [x] 3. Parchment Light Theme Definition

  **What to do**:
  - Create `frontend/src/theme/parchment.ts`
  - Export `parchmentOverrides: GlobalThemeOverrides` object
  - common section: saddle brown primary (#8B4513), dark gold warning (#B8860B), dark red error (#8B0000)
  - Background: bodyColor `#F5E6C8`, cardColor `#EDE0CC`, inputColor `#F0E4CC`
  - Text: textColor1 `#3D2B1F` (墨水棕), textColor2 `rgba(61, 43, 31, 0.7)`
  - Border: borderColor `rgba(93, 58, 26, 0.3)`, dividerColor `rgba(93, 58, 26, 0.2)`
  - Scrollbar: scrollbarColor `rgba(139, 69, 19, 0.3)`
  - Font: fontFamily `'Noto Sans SC', 'Noto Serif SC', serif` (衬线字体更有古书感)
  - Component overrides: Button (warm tones), Card (parchment tint)

  **Must NOT do**:
  - 不要使用过亮的白色（保持温暖的米黄色调）
  - 不要设置 animation 属性

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
    - Reason: Pure configuration, mirror of Task 2
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2, 4)
  - **Blocks**: Task 5, Task 7
  - **Blocked By**: None

  **References**:
  - Naive UI `GlobalThemeOverrides` type
  - `frontend/src/theme/starry-night.ts` — Mirror structure for consistency

  **Acceptance Criteria**:
  - [ ] File created at `frontend/src/theme/parchment.ts`
  - [ ] Exports `parchmentOverrides` typed as `GlobalThemeOverrides`
  - [ ] TypeScript compiles: `npx vue-tsc --noEmit` passes

  **QA Scenarios**:

  ```
  Scenario: Parchment theme object is valid
    Tool: Bash (node REPL)
    Preconditions: None
    Steps:
      1. Import parchmentOverrides
      2. Assert common.primaryColor equals '#8B4513'
      3. Assert common.bodyColor equals '#F5E6C8'
      4. Assert common.textColor1 equals '#3D2B1F'
    Expected Result: All color tokens match design spec
    Evidence: .sisyphus/evidence/task-3-parchment-validate.txt

  Scenario: Parchment theme uses serif font
    Tool: Bash (node REPL)
    Preconditions: Import parchmentOverrides
    Steps:
      1. Check common.fontFamily contains 'Noto Serif SC' or 'serif'
    Expected Result: Serif font stack for medieval feel
    Evidence: .sisyphus/evidence/task-3-parchment-font.txt
  ```

  **Commit**: YES
  - Message: `feat(theme): add parchment light theme definition`
  - Files: `frontend/src/theme/parchment.ts`
  - Pre-commit: `cd frontend && npx vue-tsc --noEmit`

---

- [x] 4. CSS Complement Styles (Animations + Textures)

  **What to do**:
  - Create `frontend/src/assets/css/themes.css`
  - **Starry Night extras**:
    - Subtle gradient background on body (dark purple gradient)
    - Micro-glow animation on focus (`@keyframes focus-glow`)
    - Soft pulsing border animation for cards (optional, very subtle)
  - **Parchment extras**:
    - CSS noise texture via SVG feTurbulence filter as inline data URI
    - Implementation: `<filter id="noise"><feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="4" stitchTiles="stitch"/></filter>`
    - Applied as `background-image: url("data:image/svg+xml,...")` with opacity 0.03-0.05
    - Warm gradient overlay on body
    - Vintage border style for cards (subtle double-border effect)
  - **Theme transitions**: Smooth color transition (`transition: color 0.3s, background-color 0.3s`)
  - **Dark class support**: `[data-theme="starry-night"]` and `[data-theme="parchment"]` selectors
  - Import in `main.css`

  **Must NOT do**:
  - 不要使用 JavaScript/Canvas 星星粒子
  - 不要使用外部图片文件
  - 不要覆盖 Naive UI 组件样式（只补充背景和纹理）

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: CSS animations, textures, visual effects
  - **Skills**: []
    - Pure CSS work

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2, 3)
  - **Blocks**: None (CSS is additive)
  - **Blocked By**: None

  **References**:
  - `frontend/src/assets/base.css:39-51` — Existing dark mode CSS variable pattern
  - `frontend/src/views/LoginView.vue:186-196` — Existing pulse animation pattern to follow
  - `frontend/src/views/LoginView.vue:377-384` — Existing shimmer animation pattern

  **Acceptance Criteria**:
  - [ ] File created at `frontend/src/assets/css/themes.css`
  - [ ] Imported in `frontend/src/assets/main.css`
  - [ ] No external dependencies (fonts, images)

  **QA Scenarios**:

  ```
  Scenario: Starry Night background gradient applies
    Tool: Playwright
    Preconditions: App with dark theme active
    Steps:
      1. Navigate to home page
      2. Get computed style of body background
      3. Assert contains gradient or dark purple color
    Expected Result: Subtle dark purple gradient on body
    Evidence: .sisyphus/evidence/task-4-starry-bg.png

  Scenario: Parchment noise texture applies
    Tool: Playwright
    Preconditions: App with parchment theme active
    Steps:
      1. Navigate to home page
      2. Get computed style of body
      3. Assert background-image contains noise texture (SVG filter or data URI)
    Expected Result: CSS noise texture visible on body
    Evidence: .sisyphus/evidence/task-4-parchment-texture.png

  Scenario: Theme transitions are smooth
    Tool: Playwright
    Preconditions: App loaded
    Steps:
      1. Click theme toggle
      2. Observe transition duration of body element
      3. Assert transition includes color and background-color
    Expected Result: Smooth 0.3s transition between themes
    Evidence: .sisyphus/evidence/task-4-transition.mp4
  ```

  **Commit**: YES
  - Message: `feat(theme): add CSS complement styles and textures`
  - Files: `frontend/src/assets/css/themes.css`, `frontend/src/assets/main.css`
  - Pre-commit: None

---

- [x] 5. NConfigProvider + NGlobalStyle Integration in App.vue

  **What to do**:
  - Modify `frontend/src/App.vue`:
    - Import NConfigProvider, NGlobalStyle from naive-ui
    - Import darkTheme from naive-ui
    - Import useThemeStore
    - Import theme definitions (starryNightOverrides, parchmentOverrides)
    - Wrap template with `<n-config-provider :theme="naiveTheme" :theme-overrides="themeOverrides">`
    - Add `<n-global-style />` inside
    - Set `data-theme` attribute on root div for CSS selectors
    - Computed `naiveTheme`: darkTheme if isDark, null if light
    - Computed `themeOverrides`: select starryNightOverrides or parchmentOverrides based on currentTheme

  **Must NOT do**:
  - 不要移除现有的 RouterView 和 BackendSwitcher
  - 不要改变 header 的布局结构

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Integration task touching core app structure, needs careful handling
  - **Skills**: []
    - Vue integration work

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2 (with Tasks 6, 7)
  - **Blocks**: Task 8, Task 9
  - **Blocked By**: Task 1, Task 2, Task 3

  **References**:
  - `frontend/src/App.vue:1-35` — Current App.vue structure
  - `frontend/src/main.ts:1-25` — App bootstrap with naive plugin
  - Naive UI NConfigProvider docs — `:theme` and `:theme-overrides` props

  **Acceptance Criteria**:
  - [ ] App.vue wraps content in n-config-provider
  - [ ] NGlobalStyle present
  - [ ] Theme switching works without page reload
  - [ ] Existing components (RouterView, BackendSwitcher) still render

  **QA Scenarios**:

  ```
  Scenario: App renders with NConfigProvider
    Tool: Playwright
    Preconditions: Dev server running
    Steps:
      1. Navigate to home page
      2. Check DOM for n-config-provider element
      3. Check n-global-style is rendered
    Expected Result: Both components present in DOM
    Evidence: .sisyphus/evidence/task-5-provider-dom.png

  Scenario: Theme switch updates all Naive UI components
    Tool: Playwright
    Preconditions: App loaded in parchment theme
    Steps:
      1. Inspect a Button element background color
      2. Note the brown/amber tone
      3. Switch to starry night theme
      4. Re-inspect the same Button
      5. Assert background changed to purple tones
    Expected Result: All Naive UI components update colors on theme switch
    Evidence: .sisyphus/evidence/task-5-theme-switch.mp4
  ```

  **Commit**: YES
  - Message: `feat(theme): integrate NConfigProvider with dual theme support`
  - Files: `frontend/src/App.vue`
  - Pre-commit: `cd frontend && npm run type-check`

---

- [x] 6. ThemeSwitcher Component

  **What to do**:
  - Create `frontend/src/components/ThemeSwitcher.vue`
  - NButton with icon (sun for light, moon for dark)
  - NTooltip showing theme name
  - Click handler calls themeStore.toggle()
  - Transition animation on icon swap
  - Size: small/medium, minimal visual footprint
  - Icon: use NIcon or emoji (🌙/☀️)

  **Must NOT do**:
  - 不要使用外部图标库（保持简单）
  - 不要弹出选择菜单（直接切换）

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple component with button + icon + click handler
  - **Skills**: []
    - Basic Vue component

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 5, 7)
  - **Blocks**: Task 9
  - **Blocked By**: Task 1

  **References**:
  - `frontend/src/components/BackendSwitcher.vue` — Component pattern to follow
  - `frontend/src/stores/theme.store.ts` — Store API to consume

  **Acceptance Criteria**:
  - [ ] Component renders sun/moon icon based on current theme
  - [ ] Clicking toggles theme
  - [ ] Icon animates on switch

  **QA Scenarios**:

  ```
  Scenario: ThemeSwitcher shows correct icon
    Tool: Playwright
    Preconditions: App in starry night (dark) theme
    Steps:
      1. Find theme switcher button
      2. Assert icon shows sun (☀️) indicating "switch to light"
      3. Click the button
      4. Assert icon changes to moon (🌙) indicating "switch to dark"
    Expected Result: Icon toggles correctly with theme
    Evidence: .sisyphus/evidence/task-6-icon-toggle.mp4

  Scenario: ThemeSwitcher persists after page reload
    Tool: Playwright
    Preconditions: Switch to parchment theme
    Steps:
      1. Reload page
      2. Assert theme is still parchment
      3. Assert switcher icon shows moon (switch to dark option)
    Expected Result: Theme persists across reloads
    Evidence: .sisyphus/evidence/task-6-persist.txt
  ```

  **Commit**: YES (groups with Task 9)
  - Message: `feat(theme): add theme switcher component`
  - Files: `frontend/src/components/ThemeSwitcher.vue`
  - Pre-commit: None

---

- [x] 7. Theme Index and Exports

  **What to do**:
  - Create `frontend/src/theme/index.ts`
  - Re-export `starryNightOverrides` from `./starry-night`
  - Re-export `parchmentOverrides` from `./parchment`
  - Export `type ThemeName = 'starry-night' | 'parchment'`
  - Export helper: `getThemeOverrides(name: ThemeName): GlobalThemeOverrides`

  **Must NOT do**:
  - 不要在这里导入 Vue（纯 TypeScript 模块）

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple barrel export file
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 5, 6)
  - **Blocks**: None
  - **Blocked By**: Task 2, Task 3

  **Acceptance Criteria**:
  - [ ] File created at `frontend/src/theme/index.ts`
  - [ ] All exports accessible via `import { ... } from '@/theme'`

  **QA Scenarios**:

  ```
  Scenario: Theme index exports correctly
    Tool: Bash (node REPL)
    Preconditions: None
    Steps:
      1. Import { starryNightOverrides, parchmentOverrides, getThemeOverrides } from '@/theme'
      2. Assert starryNightOverrides is defined
      3. Assert parchmentOverrides is defined
      4. Call getThemeOverrides('starry-night') and assert equals starryNightOverrides
    Expected Result: All exports work correctly
    Evidence: .sisyphus/evidence/task-7-exports.txt
  ```

  **Commit**: YES (groups with Tasks 2, 3)
  - Message: `feat(theme): add theme module index and exports`
  - Files: `frontend/src/theme/index.ts`
  - Pre-commit: `cd frontend && npx vue-tsc --noEmit`

---

- [x] 8. Early Theme Init in main.ts (FOUC Prevention)

  **What to do**:
  - Modify `frontend/src/main.ts`:
    - Import and initialize theme store BEFORE `app.mount()`
    - Call `useThemeStore().loadFromStorage()` in bootstrap function, before mount
    - This ensures theme is loaded from localStorage before Vue renders
    - Prevents Flash of Unstyled Content (FOUC)
  - The store's `loadFromStorage()` should also set `document.documentElement.setAttribute('data-theme', ...)` immediately
  - This way even if Vue hasn't hydrated, the CSS variables are active

  **Must NOT do**:
  - 不要在这里做异步操作（必须同步加载主题）
  - 不要修改 LoginView.vue（LoginView 不在主题系统内）

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple initialization logic, 3-5 lines of code
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3 (with Task 9)
  - **Blocks**: None (final)
  - **Blocked By**: Task 1, Task 5

  **References**:
  - `frontend/src/main.ts:1-25` — Current bootstrap function
  - `frontend/src/stores/theme.store.ts` — loadFromStorage function to call

  **Acceptance Criteria**:
  - [ ] Theme store initialized before app.mount()
  - [ ] data-theme attribute set on documentElement synchronously
  - [ ] No FOUC visible on page reload

  **QA Scenarios**:

  ```
  Scenario: No FOUC on page reload with saved theme
    Tool: Playwright
    Preconditions: localStorage has parchment theme saved
    Steps:
      1. Navigate to app
      2. Immediately check document.documentElement.getAttribute('data-theme')
      3. Assert equals 'parchment' (no delay)
    Expected Result: Theme applied before any render
    Evidence: .sisyphus/evidence/task-8-no-fouc.txt

  Scenario: Bootstrap order is correct
    Tool: Bash (grep)
    Preconditions: main.ts source code
    Steps:
      1. Verify loadFromStorage() call appears BEFORE app.mount() in code
    Expected Result: Theme init happens first
    Evidence: .sisyphus/evidence/task-8-bootstrap-order.txt
  ```

  **Commit**: YES
  - Message: `feat(theme): prevent FOUC with early theme initialization`
  - Files: `frontend/src/main.ts`
  - Pre-commit: `cd frontend && npm run type-check`

---

- [x] 9. Header Integration + Responsive Theme Switcher

  **What to do**:
  - Modify `frontend/src/App.vue`:
    - Import and add ThemeSwitcher to header
    - Position: right side of header (next to BackendSwitcher)
    - Ensure theme switcher visible on both authenticated and non-authenticated pages
    - Add theme switcher to login page header (or floating button)
  - Responsive: theme switcher works on mobile (smaller icon)
  - Set `data-theme` attribute on root div dynamically

  **Must NOT do**:
  - 不要改变 header 的 flex 布局方向
  - 不要让 theme switcher 太大

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
    - Reason: Layout integration, positioning adjustments
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3 (with Task 8)
  - **Blocks**: None (final)
  - **Blocked By**: Task 5, Task 6

  **References**:
  - `frontend/src/App.vue:10-16` — Current header layout

  **Acceptance Criteria**:
  - [ ] ThemeSwitcher visible in header
  - [ ] Works on both authenticated and non-authenticated views
  - [ ] data-theme attribute updates on root div

  **QA Scenarios**:

  ```
  Scenario: ThemeSwitcher in header
    Tool: Playwright
    Preconditions: User authenticated
    Steps:
      1. Navigate to home page
      2. Assert ThemeSwitcher button is visible in header
      3. Click it
      4. Assert theme changes
    Expected Result: Theme switcher works in header
    Evidence: .sisyphus/evidence/task-9-header-switch.mp4

  Scenario: data-theme attribute updates
    Tool: Playwright
    Preconditions: App loaded
    Steps:
      1. Check root div has data-theme="starry-night"
      2. Switch theme
      3. Check root div now has data-theme="parchment"
    Expected Result: data-theme attribute tracks current theme
    Evidence: .sisyphus/evidence/task-9-data-theme.txt
  ```

  **Commit**: YES (groups with Task 6)
  - Message: `feat(theme): add theme switcher to header and set data-theme`
  - Files: `frontend/src/App.vue`
  - Pre-commit: `cd frontend && npm run type-check`

---

## Final Verification Wave

- [x] F1. **Visual QA — Both Themes, All Pages** — `unspecified-high` + Playwright
  Test every page in both themes:
  - Login page (always dark — verify unaffected by theme system)
  - Home page (dark + light)
  - Theme switch transition
  - All Naive UI components (buttons, inputs, cards, alerts)
  - Screenshot evidence for each combination
  Output: `Pages [N/N] × Themes [2/2] | LoginView unaffected [YES/NO] | VERDICT`

- [x] F2. **Store Persistence & System Preference** — `unspecified-high`
  Test localStorage persistence:
  - Set theme → reload → verify theme preserved
  - Clear localStorage → verify falls back to system preference
  - Change system preference → verify auto-switch (when no user override)
  - Set override → change system → verify override takes priority
  - Verify no FOUC on reload
  Output: `Persistence [PASS/FAIL] | System [PASS/FAIL] | Override [PASS/FAIL] | FOUC [PASS/FAIL] | VERDICT`

- [x] F3. **TypeScript & Build Check** — `unspecified-high`
  Run: `cd frontend && npm run type-check && npm run build`
  Check for: type errors, build warnings, bundle size impact
  Output: `TypeScript [PASS/FAIL] | Build [PASS/FAIL] | Bundle [+N KB] | VERDICT`

---

## Commit Strategy

- **Wave 1**: `feat(theme): foundation — store + theme definitions + CSS` (T1, T2, T3, T4)
- **Wave 2**: `feat(theme): integration — App.vue + switcher + exports` (T5, T6, T7)
- **Wave 3**: `feat(theme): integration — main.ts init + header` (T8, T9)

---

## Success Criteria

### Verification Commands
```bash
cd frontend && npm run type-check    # Expected: 0 errors
cd frontend && npm run test:unit -- --run theme.store  # Expected: all pass
cd frontend && npm run build         # Expected: builds to ../public/
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] All tests pass
- [ ] Both themes visually verified
- [ ] Theme persists across page reload
- [ ] System preference detected correctly
- [ ] No new npm dependencies added
