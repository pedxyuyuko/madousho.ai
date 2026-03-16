# Frontend SPA Scaffolding for Madousho.ai

## TL;DR

> **Quick Summary**: 为现有 Python/FastAPI 后端项目搭建 Vue 3 + Vite + TypeScript 前端 SPA 脚手架，配置开发工具链、状态管理、Mock API、测试框架和构建管线，**不包含任何具体页面或组件实现**。
> 
> **Deliverables**:
> - [ ] 完整的 `frontend/` 项目结构（Vue 3 + Vite + TypeScript）
> - [ ] 开发环境配置（Vite 代理、SCSS、TypeScript）
> - [ ] UI 框架集成（naive-ui）
> - [ ] 状态管理（Pinia stores 基础结构）
> - [ ] Mock API 基础设施（MSW handlers）
> - [ ] 测试框架配置（Vitest + Vue Test Utils）
> - [ ] 构建管线（输出到 `public/`）
> - [ ] 路由配置（空路由，无页面组件）
> 
> **Estimated Effort**: Small
> **Parallel Execution**: NO - Sequential (scaffolding has strong dependencies)
> **Critical Path**: Project Init → Dependencies → Config → Core Infra → Build Verify

---

## Context

### Original Request
用户希望为 madousho.ai (魔导书) 项目添加前端 SPA。Phase 1 是技术选型和脚手架搭建（使用 mock 数据），Phase 2 将对接真实后端 API。

### Interview Summary
**Key Discussions**:
- **技术栈选择**: Vue 3 + Vite + TypeScript（中文生态好，学习曲线适中）
- **UI 组件库**: naive-ui（中文优先设计，TypeScript 支持优秀）
- **状态管理**: Pinia（Vue 官方推荐，轻量）
- **CSS 策略**: SCSS/Sass + naive-ui 组件样式
- **Mock 数据**: MSW (Mock Service Worker) - 拦截网络请求，提供接近真实的 API 模拟
- **测试框架**: Vitest + Vue Test Utils
- **包管理器**: pnpm
- **项目位置**: `frontend/` 目录（项目根目录下）
- **构建输出**: `public/` 目录（由 FastAPI 提供服务）
- **范围限制**: 只搭建脚手架，不做任何页面或组件

**Research Findings**:
- **从 explore agent**: 项目无现有前端代码；FastAPI 已配置静态文件服务；API 端点包括 `/api/v1/flows` CRUD 和 `/api/v1/health`；数据库模型为 Flow 和 Task
- **从 Oracle**: 推荐 Vue 3 + naive-ui 作为最佳中文开发者体验；建议使用 OpenAPI 规范生成 TypeScript API 客户端；推荐前端/后端严格分离的目录结构
- **从 Metis**: 发现 CORS 中间件缺失（开发需要）；静态文件挂载顺序需验证；需要 Bearer token 拦截器；建议明确排除范围避免 scope creep

### Metis Review
**Identified Gaps** (addressed):
- **CORS 配置**: 将通过 Vite 代理解决（不直接跨域），无需修改后端
- **Auth token 存储**: Phase 1 使用 MSW mock，token 注入为占位符实现
- **构建输出路径**: Vite 配置 `build.outDir: '../public'` 从 frontend/ 输出到项目根
- **MSW 生产环境**: 通过 `import.meta.env.DEV` 确保仅开发环境启用
- **中文支持**: 添加中文字体栈 SCSS 变量
- **范围限制**: 明确只搭建脚手架，不做任何页面或组件

---

## Work Objectives

### Core Objective
创建一个完整、可运行的 Vue 3 前端项目脚手架，包含所有必要的开发工具、组件库、状态管理、mock API 和测试配置，**不包含任何页面或组件实现**，为后续真实 API 集成和页面开发奠定基础。

### Concrete Deliverables
- `frontend/` 目录结构（Vue 3 + Vite + TypeScript）
- Vite 配置（代理、SCSS、构建输出）
- naive-ui 集成（全局注册）
- Pinia store 基础结构（目录和入口文件）
- MSW 配置（handlers for existing API endpoints）
- Vitest 配置（测试框架设置）
- 路由配置（Vue Router，空路由表）
- API 客户端（Axios + Bearer token 拦截器）
- SCSS 基础配置（变量、混入、中文字体）
- README 开发文档
- **无页面组件**（纯脚手架）
- **无业务组件**（纯脚手架）

### Definition of Done
- [ ] `pnpm build` 成功，输出到 `public/` 目录
- [ ] `pnpm dev` 启动 Vite 开发服务器，代理 API 调用
- [ ] `pnpm exec vue-tsc --noEmit` 类型检查通过
- [ ] `pnpm test:run` 测试框架就绪（可能无测试）
- [ ] FastAPI 在 `http://localhost:8000/` 提供前端服务（空白页面）
- [ ] MSW handlers 已配置（可用但无页面调用）
- [ ] 路由已配置（空路由表，无页面组件）
- [ ] 所有工具链就绪，可以开始开发页面
- [ ] **无页面组件**（纯脚手架）
- [ ] **无业务组件**（纯脚手架）

### Must Have
- Vue 3 (Composition API with `<script setup>`) + Vite + TypeScript
- naive-ui 组件库集成
- Pinia 状态管理
- SCSS/Sass 支持
- MSW mock 数据
- Vitest 测试框架
- Vite 开发服务器代理 `/api/v1` 到 FastAPI 后端
- 构建输出到 `public/` 目录
- 中文字体栈支持
- Bearer token 拦截器（即使 mock 也需包含）

### Must NOT Have (Guardrails)
- ❌ **任何页面组件**（无 FlowList、FlowDetail 等页面）
- ❌ **任何业务组件**（无布局组件、表单组件等）
- ❌ **真实 API 集成**（Phase 2）
- ❌ **认证 UI**（登录页面、token 输入）
- ❌ **Task CRUD**（API 暂不支持）
- ❌ **WebSocket 支持**
- ❌ **i18n 实现**（中英文切换）
- ❌ **部署配置**（Dockerfile、Nginx、CI/CD）
- ❌ **性能优化**（代码分割、懒加载）
- ❌ **E2E 测试**（Playwright 设置）
- ❌ **组件库 storybook/文档**

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: NO (new frontend project)
- **Automated tests**: YES (Vitest + Vue Test Utils)
- **Framework**: Vitest (Vite-native testing)
- **Test setup**: Configure MSW for test environment

### QA Policy
Every task MUST include agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **Frontend/UI**: Use Playwright (playwright skill) — Navigate, interact, assert DOM, screenshot
- **CLI/Build**: Use Bash — Run pnpm commands, verify outputs
- **File Structure**: Use Bash — Verify file existence, grep content
- **Type Safety**: Use Bash — Run vue-tsc type checking

---

## Execution Strategy

### Sequential Execution (Scaffolding has strong dependencies)

```
Step 1: Project Initialization
├── Task 1: Initialize Vue 3 project with Vite
└── Task 2: Install core dependencies

Step 2: Configuration & Infrastructure
├── Task 3: Configure Vite (proxy, SCSS, build output)
├── Task 4: Set up TypeScript configuration
├── Task 5: Configure SCSS/Sass with Chinese font variables
└── Task 6: Integrate naive-ui

Step 3: Core Infrastructure
├── Task 7: Set up Pinia store structure
├── Task 8: Configure MSW for mock API
├── Task 9: Create API client with Bearer token interceptor
└── Task 10: Set up Vue Router (empty routes)

Step 4: Testing & Verification
├── Task 11: Configure Vitest with Vue Test Utils
└── Task 12: Verify build pipeline

Critical Path: Task 1 → Task 2 → Task 3 → Task 7 → Task 11 → Task 12
```

---

## TODOs

- [x] 1. Initialize Vue 3 project with Vite

  **What to do**:
  - Run `pnpm create vue@latest frontend` with options: TypeScript, Vue Router, Pinia, Vitest, ESLint
  - Verify project structure created correctly
  - Check that package.json has correct dependencies

  **Must NOT do**:
  - Do not add extra dependencies yet (next task)
  - Do not modify generated config files yet

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple project initialization command
  - **Skills**: []
    - No special skills needed

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential - first step
  - **Blocks**: All subsequent tasks
  - **Blocked By**: None

  **References**:
  - **Pattern References**: None (new project)
  - **API/Type References**: None
  - **Test References**: None
  - **External References**: https://vuejs.org/guide/quick-start.html#creating-a-vue-application

  **Acceptance Criteria**:
  - [ ] Directory `frontend/` exists with `package.json`, `vite.config.ts`, `tsconfig.json`
  - [ ] `package.json` contains `vue`, `vue-router`, `pinia`, `vitest` dependencies
  - [ ] `frontend/src/main.ts` exists with Vue app creation

  **QA Scenarios (MANDATORY)**:
  ```
  Scenario: Project initialization creates correct structure
    Tool: Bash
    Preconditions: Clean workspace
    Steps:
      1. Run `pnpm create vue@latest frontend` with TypeScript, Router, Pinia, Vitest
      2. Verify `frontend/package.json` exists
      3. Verify `frontend/vite.config.ts` exists
      4. Verify `frontend/tsconfig.json` exists
      5. Verify `frontend/src/main.ts` exists
    Expected Result: All files exist with correct Vue 3 + TypeScript configuration
    Failure Indicators: Missing files, wrong dependencies in package.json
    Evidence: .sisyphus/evidence/task-01-project-init.txt

  Scenario: Package.json has required dependencies
    Tool: Bash
    Preconditions: Project initialized
    Steps:
      1. Read `frontend/package.json`
      2. Verify `vue` is in dependencies
      3. Verify `vue-router` is in dependencies
      4. Verify `pinia` is in dependencies
      5. Verify `vitest` is in devDependencies
    Expected Result: All core dependencies present
    Failure Indicators: Missing dependencies, wrong versions
    Evidence: .sisyphus/evidence/task-01-dependencies.txt
  ```

  **Commit**: YES
  - Message: `feat(frontend): initialize Vue 3 project with Vite`
  - Files: `frontend/*`

- [x] 2. Install core dependencies

  **What to do**:
  - Install `naive-ui` for UI components
  - Install `sass` for SCSS support
  - Install `msw` for mock API
  - Install `@vicons/ionicons5` for icons (naive-ui compatible)
  - Install `axios` for HTTP client
  - Verify all dependencies install correctly

  **Must NOT do**:
  - Do not install dev dependencies that come with create-vue
  - Do not modify any config files yet

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple dependency installation
  - **Skills**: []
    - No special skills needed

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential - after Task 1
  - **Blocks**: Tasks 3-12
  - **Blocked By**: Task 1

  **References**:
  - **External References**: 
    - https://www.naiveui.com/en-US/os-theme/docs/installation
    - https://mswjs.io/docs/getting-started

  **Acceptance Criteria**:
  - [ ] `pnpm install` completes without errors
  - [ ] `naive-ui` in dependencies
  - [ ] `sass` in devDependencies
  - [ ] `msw` in devDependencies
  - [ ] `axios` in dependencies

  **QA Scenarios (MANDATORY)**:
  ```
  Scenario: Dependencies install successfully
    Tool: Bash
    Preconditions: Project initialized (Task 1 complete)
    Steps:
      1. Run `cd frontend && pnpm add naive-ui axios @vicons/ionicons5`
      2. Run `cd frontend && pnpm add -D sass msw`
      3. Verify `node_modules/naive-ui` exists
      4. Verify `node_modules/msw` exists
    Expected Result: All dependencies installed, no errors
    Failure Indicators: pnpm errors, missing node_modules
    Evidence: .sisyphus/evidence/task-02-dependencies-install.txt
  ```

  **Commit**: YES
  - Message: `chore(frontend): install naive-ui, sass, msw, axios`
  - Files: `frontend/package.json`, `frontend/pnpm-lock.yaml`

- [x] 3. Configure Vite (proxy, SCSS, build output)

  **What to do**:
  - Configure Vite dev server proxy for `/api/v1` to `http://localhost:8000`
  - Set `build.outDir` to `../public`
  - Configure SCSS preprocessor options
  - Add global SCSS variables import
  - Configure naive-ui auto-import

  **Must NOT do**:
  - Do not create actual SCSS files yet (Task 5)
  - Do not modify Vue component files

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Configuration file editing
  - **Skills**: []
    - No special skills needed

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential - after Task 2
  - **Blocks**: Tasks 4-12
  - **Blocked By**: Task 2

  **References**:
  - **External References**: https://vitejs.dev/config/

  **Acceptance Criteria**:
  - [ ] `vite.config.ts` has proxy configuration for `/api/v1`
  - [ ] `vite.config.ts` has `build.outDir: '../public'`
  - [ ] SCSS preprocessor configured
  - [ ] naive-ui auto-import configured (if using unplugin-vue-components)

  **QA Scenarios (MANDATORY)**:
  ```
  Scenario: Vite proxy configuration is correct
    Tool: Bash
    Preconditions: Task 2 complete
    Steps:
      1. Read `frontend/vite.config.ts`
      2. Verify proxy config for `/api/v1` exists
      3. Verify target is `http://localhost:8000`
      4. Verify `build.outDir` is `../public`
    Expected Result: Correct proxy and build configuration
    Failure Indicators: Missing proxy config, wrong outDir
    Evidence: .sisyphus/evidence/task-03-vite-config.txt
  ```

  **Commit**: YES
  - Message: `config(frontend): configure Vite proxy and build output`
  - Files: `frontend/vite.config.ts`

- [x] 4. Set up TypeScript configuration

  **What to do**:
  - Review and adjust `tsconfig.json` for Vue 3 + TypeScript best practices
  - Configure path aliases (`@/` for `src/`)
  - Ensure strict mode enabled
  - Add naive-ui type declarations if needed

  **Must NOT do**:
  - Do not disable strict mode
  - Do not add unrelated type configurations

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: TypeScript configuration adjustment
  - **Skills**: []
    - No special skills needed

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential - after Task 3
  - **Blocks**: Tasks 5-12
  - **Blocked By**: Task 3

  **References**:
  - **External References**: https://vuejs.org/guide/typescript/overview.html

  **Acceptance Criteria**:
  - [ ] `tsconfig.json` has path aliases configured
  - [ ] Strict mode enabled
  - [ ] `pnpm exec vue-tsc --noEmit` passes (may need existing files first)

  **QA Scenarios (MANDATORY)**:
  ```
  Scenario: TypeScript configuration is valid
    Tool: Bash
    Preconditions: Task 3 complete
    Steps:
      1. Read `frontend/tsconfig.json`
      2. Verify `strict: true` is set
      3. Verify path aliases configured (`@/` → `src/`)
      4. Run `cd frontend && pnpm exec vue-tsc --noEmit` (may pass or show existing issues)
    Expected Result: TypeScript config valid, strict mode enabled
    Failure Indicators: Missing strict mode, broken path aliases
    Evidence: .sisyphus/evidence/task-04-typescript-config.txt
  ```

  **Commit**: YES
  - Message: `config(frontend): configure TypeScript with path aliases`
  - Files: `frontend/tsconfig.json`

- [x] 5. Configure SCSS/Sass with Chinese font variables

  **What to do**:
  - Create `frontend/src/assets/scss/_variables.scss` with:
    - Chinese font stack variables
    - Color palette variables
    - Spacing/sizing variables
  - Create `frontend/src/assets/scss/main.scss` with global styles
  - Create `frontend/src/assets/scss/_mixins.scss` with common mixins
  - Configure Vite to auto-import `_variables.scss` (optional)

  **Must NOT do**:
  - Do not create component-specific styles yet
  - Do not override naive-ui theme variables directly in SCSS

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: SCSS file creation with standard variables
  - **Skills**: []
    - No special skills needed

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential - after Task 4
  - **Blocks**: Tasks 6-12
  - **Blocked By**: Task 4

  **References**:
  - **Pattern References**: Chinese font stack from Metis analysis
  - **External References**: https://sass-lang.com/documentation

  **Acceptance Criteria**:
  - [ ] `_variables.scss` exists with font, color, spacing variables
  - [ ] `main.scss` exists with global styles
  - [ ] `_mixins.scss` exists with common mixins
  - [ ] Chinese font stack includes Noto Sans SC, PingFang SC, Microsoft YaHei

  **QA Scenarios (MANDATORY)**:
  ```
  Scenario: SCSS files created with Chinese font support
    Tool: Bash
    Preconditions: Task 4 complete
    Steps:
      1. Verify `frontend/src/assets/scss/_variables.scss` exists
      2. Verify file contains `$font-family-cn` variable
      3. Verify file contains `Noto Sans SC` font
      4. Verify `frontend/src/assets/scss/main.scss` exists
      5. Verify `frontend/src/assets/scss/_mixins.scss` exists
    Expected Result: All SCSS files exist with proper Chinese font stack
    Failure Indicators: Missing files, no Chinese font variables
    Evidence: .sisyphus/evidence/task-05-scss-setup.txt
  ```

  **Commit**: YES
  - Message: `style(frontend): set up SCSS with Chinese font variables`
  - Files: `frontend/src/assets/scss/*`

- [x] 6. Integrate naive-ui

  **What to do**:
  - Import naive-ui in `main.ts`
  - Configure naive-ui global theme (if needed)
  - Set up naive-ui provider component
  - Verify components render correctly

  **Must NOT do**:
  - Do not customize theme extensively (keep defaults)
  - Do not import all components (use tree-shaking)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple library integration
  - **Skills**: []
    - No special skills needed

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential - after Task 5
  - **Blocks**: Tasks 7-12
  - **Blocked By**: Task 5

  **References**:
  - **External References**: https://www.naiveui.com/en-US/os-theme/docs/installation

  **Acceptance Criteria**:
  - [ ] `main.ts` imports naive-ui
  - [ ] `NConfigProvider` wraps app (optional but recommended)
  - [ ] At least one naive-ui component renders in browser

  **QA Scenarios (MANDATORY)**:
  ```
  Scenario: naive-ui integrated in main.ts
    Tool: Bash
    Preconditions: Task 5 complete
    Steps:
      1. Read `frontend/src/main.ts`
      2. Verify naive-ui import exists
      3. Verify app uses naive-ui components
      4. Run `cd frontend && pnpm exec vue-tsc --noEmit` (type check)
    Expected Result: naive-ui integrated, type check passes
    Failure Indicators: Missing import, type errors
    Evidence: .sisyphus/evidence/task-06-naive-ui-integration.txt
  ```

  **Commit**: YES
  - Message: `feat(frontend): integrate naive-ui component library`
  - Files: `frontend/src/main.ts`

- [x] 7. Set up Pinia store structure

  **What to do**:
  - Create `frontend/src/stores/modules/` directory
  - Create `frontend/src/stores/index.ts` barrel export
  - Create `frontend/src/stores/modules/example.store.ts` with:
    - Empty state
    - Empty actions
    - Empty getters
    - TypeScript types
  - Configure Pinia in `main.ts` (if not already)

  **Must NOT do**:
  - Do not add business-specific stores (flow, task, etc.)
  - Do not add mock data
  - Do not add real API calls

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
    - Reason: Store creation with TypeScript types
  - **Skills**: []
    - No special skills needed

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential - after Task 6
  - **Blocks**: Tasks 8-12
  - **Blocked By**: Task 6

  **References**:
  - **External References**: https://pinia.vuejs.org/

  **Acceptance Criteria**:
  - [ ] `frontend/src/stores/modules/` directory exists
  - [ ] `frontend/src/stores/index.ts` barrel export exists
  - [ ] `example.store.ts` exists with empty state, actions, getters
  - [ ] Store exports properly
  - [ ] Type-safe store definition

  **QA Scenarios (MANDATORY)**:
  ```
  Scenario: Pinia store structure created
    Tool: Bash
    Preconditions: Task 6 complete
    Steps:
      1. Verify `frontend/src/stores/modules/` directory exists
      2. Verify `frontend/src/stores/index.ts` barrel export exists
      3. Verify `example.store.ts` exists with empty state
      4. Verify store exports properly
      5. Run type check `cd frontend && pnpm exec vue-tsc --noEmit`
    Expected Result: Store structure created with proper TypeScript types
    Failure Indicators: Missing directories, type errors
    Evidence: .sisyphus/evidence/task-07-pinia-store.txt
  ```

  **Commit**: YES
  - Message: `feat(frontend): set up Pinia store structure`
  - Files: `frontend/src/stores/*`

- [x] 8. Configure MSW for mock API

  **What to do**:
  - Create `frontend/src/mocks/handlers.ts` with empty handlers array
  - Create `frontend/src/mocks/browser.ts` for browser MSW setup
  - Create `frontend/src/mocks/node.ts` for Node.js MSW setup (testing)
  - Initialize MSW in `main.ts` (only in dev mode)

  **Must NOT do**:
  - Do not enable MSW in production builds
  - Do not add handlers for specific API endpoints (scaffolding only)
  - Do not add mock data

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
    - Reason: MSW infrastructure setup
  - **Skills**: []
    - No special skills needed

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential - after Task 7
  - **Blocks**: Tasks 9-12
  - **Blocked By**: Task 7

  **References**:
  - **External References**: https://mswjs.io/docs/getting-started

  **Acceptance Criteria**:
  - [ ] `handlers.ts` exists with empty handlers array
  - [ ] `browser.ts` and `node.ts` exist
  - [ ] MSW only initializes in development mode
  - [ ] MSW infrastructure ready for adding handlers later

  **QA Scenarios (MANDATORY)**:
  ```
  Scenario: MSW infrastructure configured
    Tool: Bash
    Preconditions: Task 7 complete
    Steps:
      1. Verify `frontend/src/mocks/handlers.ts` exists
      2. Verify file contains empty handlers array
      3. Verify `frontend/src/mocks/browser.ts` exists
      4. Verify `frontend/src/mocks/node.ts` exists
      5. Read `frontend/src/main.ts`
      6. Verify MSW initialization wrapped in `import.meta.env.DEV` check
    Expected Result: MSW infrastructure ready for adding handlers later
    Failure Indicators: Missing files, no env check
    Evidence: .sisyphus/evidence/task-08-msw-setup.txt
  ```

  **Commit**: YES
  - Message: `feat(frontend): configure MSW mock API infrastructure`
  - Files: `frontend/src/mocks/*`, `frontend/src/main.ts`

- [x] 9. Create API client with Bearer token interceptor

  **What to do**:
  - Create `frontend/src/api/client.ts` with Axios instance
  - Configure base URL to `/api/v1`
  - Add request interceptor to inject Bearer token
  - Add response interceptor for error handling
  - Export types for API responses (empty interfaces)

  **Must NOT do**:
  - Do not implement actual authentication (Phase 2)
  - Do not hardcode tokens (use placeholder)
  - Do not add specific API functions (flows.ts, etc.)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: API client setup with Axios
  - **Skills**: []
    - No special skills needed

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential - after Task 8
  - **Blocks**: Tasks 10-12
  - **Blocked By**: Task 8

  **References**:
  - **External References**: https://axios-http.com/docs/intro

  **Acceptance Criteria**:
  - [ ] `client.ts` exists with Axios instance configured
  - [ ] Bearer token interceptor configured
  - [ ] Base URL set to `/api/v1`
  - [ ] Types exported for API responses

  **QA Scenarios (MANDATORY)**:
  ```
  Scenario: API client configured with Bearer token interceptor
    Tool: Bash
    Preconditions: Task 8 complete
    Steps:
      1. Verify `frontend/src/api/client.ts` exists
      2. Verify Axios instance created with baseURL `/api/v1`
      3. Verify request interceptor adds Authorization header
      4. Verify response interceptor exists for error handling
      5. Verify types exported for API responses
    Expected Result: API client ready with auth interceptor
    Failure Indicators: Missing files, no interceptor, wrong base URL
    Evidence: .sisyphus/evidence/task-09-api-client.txt
  ```

  **Commit**: YES
  - Message: `feat(frontend): create API client with Bearer token interceptor`
  - Files: `frontend/src/api/*`

- [x] 10. Set up Vue Router (empty routes)

  **What to do**:
  - Configure empty router in `frontend/src/router/index.ts`
  - Set up router instance with history mode
  - Integrate router in `main.ts` (if not already)
  - Verify router works in App.vue with `<router-view>`

  **Must NOT do**:
  - Do not add any route definitions (pages will be added later)
  - Do not add authentication guards (Phase 2)
  - Do not add layout components

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Router configuration
  - **Skills**: []
    - No special skills needed

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential - after Task 9
  - **Blocks**: Task 11
  - **Blocked By**: Task 9

  **References**:
  - **External References**: https://router.vuejs.org/

  **Acceptance Criteria**:
  - [ ] Router instance created with history mode
  - [ ] Router integrated in App.vue with `<router-view>`
  - [ ] No route definitions (empty routes array)

  **QA Scenarios (MANDATORY)**:
  ```
  Scenario: Vue Router configured with empty routes
    Tool: Bash
    Preconditions: Task 9 complete
    Steps:
      1. Read `frontend/src/router/index.ts`
      2. Verify router instance created
      3. Verify routes array is empty or contains only root path
      4. Read `frontend/src/App.vue`
      5. Verify `<router-view>` component exists
    Expected Result: Router configured but with no page routes
    Failure Indicators: Route definitions present, missing router-view
    Evidence: .sisyphus/evidence/task-10-router.txt
  ```

  **Commit**: YES
  - Message: `feat(frontend): set up Vue Router (empty routes)`
  - Files: `frontend/src/router/*`, `frontend/src/App.vue`

- [x] 11. Configure Vitest with Vue Test Utils

  **What to do**:
  - Verify Vitest configuration in `vite.config.ts`
  - Configure Vue Test Utils
  - Set up test utilities/helpers
  - Create test setup file if needed
  - Configure MSW for test environment

  **Must NOT do**:
  - Do not write extensive tests yet (scaffolding only)
  - Do not add E2E testing setup
  - Do not test components (no components exist)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Testing configuration
  - **Skills**: []
    - No special skills needed

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential - after Task 10
  - **Blocks**: Task 12
  - **Blocked By**: Task 10

  **References**:
  - **External References**: 
    - https://vitest.dev/
    - https://test-utils.vuejs.org/

  **Acceptance Criteria**:
  - [ ] Vitest configured in `vite.config.ts`
  - [ ] Test setup file exists
  - [ ] MSW configured for test environment
  - [ ] `pnpm test:run` passes (even with no tests)

  **QA Scenarios (MANDATORY)**:
  ```
  Scenario: Vitest configured and runs
    Tool: Bash
    Preconditions: Task 10 complete
    Steps:
      1. Read `frontend/vite.config.ts` for Vitest config
      2. Verify test configuration exists
      3. Run `cd frontend && pnpm test:run` (may have no tests yet)
      4. Verify command exits with success (0) or appropriate code
    Expected Result: Vitest configured, test command runs
    Failure Indicators: Missing config, test command fails
    Evidence: .sisyphus/evidence/task-11-vitest-config.txt
  ```

  **Commit**: YES
  - Message: `test(frontend): configure Vitest with Vue Test Utils`
  - Files: `frontend/vite.config.ts`, `frontend/src/test/*`

- [x] 12. Verify build pipeline

  **What to do**:
  - Run `pnpm build` and verify output in `public/`
  - Run `pnpm exec vue-tsc --noEmit` and verify no type errors
  - Verify FastAPI serves built frontend at `http://localhost:8000/`
  - Create basic README.md with development instructions

  **Must NOT do**:
  - Do not modify backend code
  - Do not add deployment configurations
  - Do not run component tests (no components exist)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Verification commands
  - **Skills**: []
    - No special skills needed

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential - final task
  - **Blocks**: None
  - **Blocked By**: Task 11

  **References**:
  - **Pattern References**: Vite config from Task 3
  - **External References**: https://vitejs.dev/guide/build.html

  **Acceptance Criteria**:
  - [ ] `pnpm build` completes successfully
  - [ ] `public/` directory created with `index.html` and assets
  - [ ] `pnpm exec vue-tsc --noEmit` passes with no errors
  - [ ] FastAPI serves frontend at root path
  - [ ] README.md exists with setup instructions

  **QA Scenarios (MANDATORY)**:
  ```
  Scenario: Build pipeline produces correct output
    Tool: Bash
    Preconditions: Tasks 1-11 complete
    Steps:
      1. Run `cd frontend && pnpm build`
      2. Verify exit code is 0 (success)
      3. Verify `public/index.html` exists at project root
      4. Verify `public/assets/` directory exists
      5. Verify `public/assets/*.js` files exist
    Expected Result: Build succeeds, output in public/ directory
    Failure Indicators: Build errors, missing output files
    Evidence: .sisyphus/evidence/task-12-build.txt

  Scenario: Type checking passes
    Tool: Bash
    Preconditions: Task 12 complete
    Steps:
      1. Run `cd frontend && pnpm exec vue-tsc --noEmit`
      2. Verify exit code is 0 (no type errors)
      3. Verify no error output
    Expected Result: No TypeScript errors
    Failure Indicators: Type errors in output
    Evidence: .sisyphus/evidence/task-12-typecheck.txt

  Scenario: FastAPI serves frontend
    Tool: Bash
    Preconditions: Build complete, FastAPI running
    Steps:
      1. Start FastAPI server `cd /path/to/project && python -m madousho serve`
      2. Wait for server to start
      3. Run `curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/`
      4. Verify HTTP 200 response
      5. Run `curl -s http://localhost:8000/ | head -n 5`
      6. Verify HTML contains Vue app div
    Expected Result: FastAPI serves frontend successfully
    Failure Indicators: 404 error, wrong content
    Evidence: .sisyphus/evidence/task-12-fastapi-serve.txt
  ```

  **Commit**: YES
  - Message: `docs(frontend): verify build pipeline and add README`
  - Files: `README.md` (update if exists, create if not)

---

## Final Verification Wave (MANDATORY — after ALL implementation tasks)

> 4 review agents run in PARALLEL. ALL must APPROVE. Rejection → fix → re-run.

- [ ] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists (read file, curl endpoint, run command). For each "Must NOT Have": search codebase for forbidden patterns — reject with file:line if found. Check evidence files exist in .sisyphus/evidence/. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [ ] F2. **Code Quality Review** — `unspecified-high`
  Run `pnpm exec vue-tsc --noEmit` + `pnpm test:run`. Review all changed files for: `as any`/`@ts-ignore`, empty catches, console.log in prod, commented-out code, unused imports. Check AI slop: excessive comments, over-abstraction, generic names (data/result/item/temp).
  Output: `TypeScript [PASS/FAIL] | Tests [N pass/N fail] | Files [N clean/N issues] | VERDICT`

- [ ] F3. **Real Manual QA** — `unspecified-high` (+ `playwright` skill)
  Start from clean state. Execute EVERY QA scenario from EVERY task — follow exact steps, capture evidence. Test build pipeline: `pnpm build` produces output in `public/`. Test dev server starts and proxies API calls. Save to `.sisyphus/evidence/final-qa/`.
  Output: `Scenarios [N/N pass] | Build [PASS/FAIL] | Dev Server [PASS/FAIL] | VERDICT`

- [ ] F4. **Scope Fidelity Check** — `deep`
  For each task: read "What to do", read actual diff (git log/diff). Verify 1:1 — everything in spec was built (no missing), nothing beyond spec was built (no creep). Check "Must NOT do" compliance. **Specifically verify NO page components or business components were created**. Detect cross-task contamination: Task N touching Task M's files. Flag unaccounted changes.
  Output: `Tasks [N/N compliant] | Contamination [CLEAN/N issues] | Unaccounted [CLEAN/N files] | VERDICT`

---

## Commit Strategy

- **1**: `feat(frontend): initialize Vue 3 project with Vite` — frontend/*
- **2**: `chore(frontend): install naive-ui, sass, msw, axios` — frontend/package.json, frontend/pnpm-lock.yaml
- **3**: `config(frontend): configure Vite proxy and build output` — frontend/vite.config.ts
- **4**: `config(frontend): configure TypeScript with path aliases` — frontend/tsconfig.json
- **5**: `style(frontend): set up SCSS with Chinese font variables` — frontend/src/assets/scss/*
- **6**: `feat(frontend): integrate naive-ui component library` — frontend/src/main.ts
- **7**: `feat(frontend): set up Pinia store structure` — frontend/src/stores/*
- **8**: `feat(frontend): configure MSW mock API infrastructure` — frontend/src/mocks/*, frontend/src/main.ts
- **9**: `feat(frontend): create API client with Bearer token interceptor` — frontend/src/api/*
- **10**: `feat(frontend): set up Vue Router (empty routes)` — frontend/src/router/*, frontend/src/App.vue
- **11**: `test(frontend): configure Vitest with Vue Test Utils` — frontend/vite.config.ts, frontend/src/test/*
- **12**: `docs(frontend): verify build pipeline and add README` — README.md

---

## Success Criteria

### Verification Commands
```bash
# 1. Project structure exists
test -f frontend/package.json && test -f frontend/vite.config.ts && test -f frontend/tsconfig.json

# 2. Dependencies install successfully
cd frontend && pnpm install

# 3. Build succeeds
cd frontend && pnpm build && test -d ../public/assets && test -f ../public/index.html

# 4. Type check passes
cd frontend && pnpm exec vue-tsc --noEmit

# 5. Vitest configured (tests may not exist yet)
cd frontend && pnpm test:run

# 6. MSW infrastructure exists
test -f frontend/src/mocks/handlers.ts && test -f frontend/src/mocks/browser.ts && test -f frontend/src/mocks/node.ts

# 7. Pinia store structure exists
test -f frontend/src/stores/modules/example.store.ts && test -f frontend/src/stores/index.ts

# 8. Router configured (empty)
test -f frontend/src/router/index.ts

# 9. Naive-ui integrated
grep -q "naive-ui" frontend/src/main.ts

# 10. SCSS configured
test -f frontend/src/assets/scss/_variables.scss && test -f frontend/src/assets/scss/main.scss

# 11. API client configured
test -f frontend/src/api/client.ts && grep -q "axios" frontend/src/api/client.ts
```

### Final Checklist
- [ ] All "Must Have" features implemented
- [ ] All "Must NOT Have" features absent
- [ ] Build produces correct output
- [ ] Type checking passes
- [ ] MSW mock API infrastructure ready
- [ ] Pinia store structure ready
- [ ] Router configured (empty routes)
- [ ] SCSS with Chinese fonts configured
- [ ] Documentation complete
- [ ] **No pages or components implemented** (scaffolding only)