# 前端 i18n 国际化改造

## TL;DR

> **目标**: 为 Vue 3 前端添加 vue-i18n 国际化支持，初始仅支持中文（zh-CN）
> 
> **交付物**:
> - `src/locales/zh-CN/*.json` — 5 个翻译文件
> - `src/i18n.ts` — vue-i18n 插件配置
> - 4 个组件 + 2 个基础设施文件更新
> - 2 个测试文件更新 + 1 个 i18n 冒烟测试
> 
> **工作量**: Medium
> **并行执行**: YES — 2-3 波次
> **关键路径**: 依赖安装 → 翻译文件 → 插件配置 → 组件替换 → 测试更新

---

## Context

### 原始需求
用户要求为 Madousho.ai 前端添加 i18n 国际化支持，暂时只支持中文，但保留未来扩展到英文的能力。

### 讨论摘要
**关键决策**:
- **框架**: vue-i18n v9 + @intlify/unplugin-vue-i18n（Vue 官方推荐，Vite 优化插件）
- **文件组织**: 按功能模块分文件（`common.json`, `login.json`, `home.json`, `backend.json`, `theme.json`）
- **Naive UI**: 通过 `NConfigProvider :locale="zhCN"` 联动
- **品牌名**: "Madousho.ai" 保留英文不翻译
- **翻译键**: 点分层级（`login.title`, `login.form.tokenLabel`）
- **测试策略**: 更新现有测试的断言从英文改为中文，添加 i18n 冒烟测试
- **范围**: 所有现有组件（LoginView, HomeView, BackendSwitcher, ThemeSwitcher, App.vue）
- **排除**: client.ts 控制台错误消息（开发者面向）、语言切换组件、`<i18n>` SFC 块

**研究发现**:
- Vue 3.5.29, Vite 7.3.1, Naive UI 2.44.1, TypeScript 5.9.3
- 硬编码字符串共 14 个需要翻译
- 9 个测试断言需要更新
- 已有中文字符串："已连接"（HomeView）

### Metis 评审
**识别并已解决的问题**:
- ✅ 缺失 key 回退策略：开发环境显示 key 名，生产环境静默
- ✅ HomeView 已有中文 "已连接" 需要转为翻译 key
- ✅ BackendSwitcher 的 `+` 前缀放在翻译 key 内
- ✅ ThemeSwitcher 的 aria-label 需要翻译（无障碍关键）
- ✅ 测试中需要注入 i18n 插件

**明确的边界**:
- ❌ 不创建语言切换器
- ❌ 不添加除 zh-CN 以外的 locale
- ❌ 不翻译控制台错误消息
- ❌ 不使用 `<i18n>` SFC 块
- ❌ 不处理复数/日期/数字格式化

---

## Work Objectives

### 核心目标
为 Madousho.ai 前端建立完整的 i18n 基础设施，将所有用户可见的硬编码英文字符串替换为中文翻译。

### 具体交付物
1. `src/locales/zh-CN/common.json` — 通用文案
2. `src/locales/zh-CN/login.json` — 登录页文案
3. `src/locales/zh-CN/home.json` — 首页文案
4. `src/locales/zh-CN/backend.json` — 后端切换文案
5. `src/locales/zh-CN/theme.json` — 主题切换文案
6. `src/i18n.ts` — vue-i18n 插件配置
7. `vite.config.ts` — 添加 unplugin-vue-i18n
8. `main.ts` — 注册 i18n 插件
9. `App.vue` — Naive UI locale 联动
10. `LoginView.vue` — 11 个字符串替换
11. `HomeView.vue` — 1 个字符串替换
12. `BackendSwitcher.vue` — 2 个字符串替换
13. `ThemeSwitcher.vue` — 2 个 aria-label 替换
14. `LoginView.test.ts` — 断言更新 + i18n 注入
15. `BackendSwitcher.test.ts` — 断言更新 + i18n 注入
16. 新 i18n 冒烟测试

### 完成定义
- [ ] `npm run build` 通过（类型检查 + 构建）
- [ ] `npm run test:unit` 全部通过
- [ ] 覆盖率 ≥90%
- [ ] 所有用户可见文案使用 `$t()` 调用
- [ ] Naive UI 组件使用中文 locale
- [ ] 测试断言使用中文字符串

### 必须有
- vue-i18n v9 + @intlify/unplugin-vue-i18n
- 按模块分文件的翻译结构
- Naive UI zhCN locale 联动
- 品牌名 "Madousho.ai" 保持英文
- 所有测试通过

### 必须没有
- 语言切换组件
- zh-CN 以外的 locale
- `<i18n>` SFC 块
- 控制台错误消息翻译
- 复数/日期/数字格式化

---

## Verification Strategy (MANDATORY)

> **零人工干预** — 所有验证由代理执行。

### 测试策略
- **框架**: Vitest（现有）
- **更新现有测试**: LoginView, BackendSwitcher 断言从英文改为中文
- **新增测试**: i18n 冒烟测试验证 `$t()` 返回正确中文
- **测试注入 i18n**: 通过 `global.plugins` 注入 vue-i18n 实例

### QA 策略
每个任务包含代理执行的 QA 场景：
- **前端 UI**: Playwright 验证渲染
- **构建**: `npm run build` + `npm run type-check`
- **测试**: `npm run test:unit`

---

## Execution Strategy

### 并行执行波次

```
Wave 1 (基础设施 — 可并行开始):
├── Task 1: 安装 vue-i18n 和 unplugin 依赖
├── Task 2: 创建 zh-CN 翻译文件（5 个 JSON）
├── Task 3: 创建 i18n.ts 插件配置
└── Task 4: 更新 vite.config.ts 添加 unplugin

Wave 2 (集成 + 组件 — 依赖 Wave 1):
├── Task 5: 更新 main.ts 注册 i18n 插件 + 更新 App.vue Naive UI locale
├── Task 6: 更新 LoginView.vue 替换 11 个字符串
├── Task 7: 更新 HomeView.vue 替换 1 个字符串
├── Task 8: 更新 BackendSwitcher.vue 替换 2 个字符串
└── Task 9: 更新 ThemeSwitcher.vue 替换 2 个 aria-label

Wave 3 (测试 — 依赖 Wave 2):
├── Task 10: 更新 LoginView.test.ts（断言 + i18n 注入）
├── Task 11: 更新 BackendSwitcher.test.ts（断言 + i18n 注入）
└── Task 12: 添加 i18n 冒烟测试

Wave 4 (验证):
└── Task 13: 最终验证（build + test + coverage）
```

### 依赖矩阵
- **Task 1-4**: 无依赖，可并行
- **Task 5-9**: 依赖 Task 1-4
- **Task 10-12**: 依赖 Task 5-9
- **Task 13**: 依赖 Task 10-12

### 关键路径
Task 1 → Task 5 → Task 6 → Task 10 → Task 13

### 代理分配摘要
- **Wave 1**: 4 个 quick 任务
- **Wave 2**: 5 个 unspecified-high 任务
- **Wave 3**: 3 个 unspecified-high 任务
- **Wave 4**: 1 个 quick 验证任务

---

## TODOs

> **关键**: 需要先检查 @intlify/unplugin-vue-i18n 是否支持 Vite 7.x。如果不支持，使用 @intlify/unplugin-vue-i18n 的最新版本或回退到手动配置。

- [ ] 1. 安装 vue-i18n 和 unplugin 依赖

  **What to do**:
  - 运行 `cd frontend && npm install vue-i18n@^9 @intlify/unplugin-vue-i18n@^3`
  - 检查 package.json 确认版本正确
  - 确保与现有 Vue 3.5.29 和 Vite 7.3.1 兼容
  - 如果版本冲突，选择兼容版本

  **Must NOT do**:
  - 不要更新其他依赖
  - 不要修改 lock 文件以外的内容

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 简单的 npm install 命令
  - **Skills**: []
  - **Skills Evaluated but Omitted**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 2, 3, 4)
  - **Blocks**: Task 5
  - **Blocked By**: None

  **References**:
  - `frontend/package.json` — 当前依赖版本，确保兼容性

  **Acceptance Criteria**:
  - [ ] `cd frontend && npm ls vue-i18n @intlify/unplugin-vue-i18n` 显示已安装版本
  - [ ] 无 npm install 错误

  **QA Scenarios**:
  ```
  Scenario: 依赖安装成功
    Tool: Bash
    Steps:
      1. cd frontend && npm ls vue-i18n @intlify/unplugin-vue-i18n
    Expected Result: 显示 vue-i18n v9.x 和 @intlify/unplugin-vue-i18n v3.x
    Evidence: .sisyphus/evidence/task-1-deps.txt

  Scenario: 构建仍通过
    Tool: Bash
    Steps:
      1. cd frontend && npm run build
    Expected Result: 退出码 0，无错误
    Evidence: .sisyphus/evidence/task-1-build.txt
  ```

  **Commit**: YES (groups with Wave 1)
  - Message: `feat(i18n): install vue-i18n and unplugin dependencies`
  - Files: `frontend/package.json`, `frontend/package-lock.json`

---

- [ ] 2. 创建 zh-CN 翻译文件

  **What to do**:
  - 创建 `frontend/src/locales/zh-CN/` 目录
  - 创建以下 5 个 JSON 文件：
    - `common.json`: `{ "brand": { "subtitle": "系统化 AI Agent 框架" } }`
    - `login.json`: 包含 title, description, form 字段, error, footer
    - `home.json`: `{ "status": { "connected": "已连接" } }`
    - `backend.json`: `{ "noBackend": "未连接后端", "addNew": "添加新后端" }`
    - `theme.json`: `{ "switchToLight": "切换到浅色主题", "switchToDark": "切换到深色主题" }`
  - 创建 `index.ts` 导出合并后的消息对象

  **Must NOT do**:
  - 不要翻译品牌名 "Madousho.ai"
  - 不要使用 `<i18n>` SFC 块格式
  - 不要包含除 zh-CN 以外的翻译

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 创建 JSON 文件，简单直接
  - **Skills**: []
  - **Skills Evaluated but Omitted**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 3, 4)
  - **Blocks**: Task 3, Task 5
  - **Blocked By**: None

  **References**:
  - `frontend/src/views/LoginView.vue:27-120` — 需要翻译的字符串（11 个）
  - `frontend/src/views/HomeView.vue:12` — "已连接"
  - `frontend/src/components/BackendSwitcher.vue:11,25` — "No backend", "+ Add new"
  - `frontend/src/components/ThemeSwitcher.vue:16` — aria-label

  **Acceptance Criteria**:
  - [ ] `ls frontend/src/locales/zh-CN/` 显示 5 个 JSON 文件
  - [ ] 每个 JSON 文件是有效的 JSON
  - [ ] 所有 14 个翻译字符串都有对应的 key

  **QA Scenarios**:
  ```
  Scenario: 翻译文件存在且有效
    Tool: Bash
    Steps:
      1. ls frontend/src/locales/zh-CN/*.json
      2. for f in frontend/src/locales/zh-CN/*.json; do python3 -m json.tool "$f" > /dev/null; done
    Expected Result: 5 个文件，全部是有效 JSON
    Evidence: .sisyphus/evidence/task-2-files.txt

  Scenario: 翻译键覆盖所有硬编码字符串
    Tool: Bash
    Steps:
      1. grep -r '"systematic\|"connect\|"base url\|"api token\|"no backend\|"add new\|"switch to' frontend/src/locales/zh-CN/ --include="*.json" -i
    Expected Result: 所有预期字符串都有对应翻译
    Evidence: .sisyphus/evidence/task-2-coverage.txt
  ```

  **Commit**: YES (groups with Wave 1)
  - Message: `feat(i18n): add zh-CN locale files`
  - Files: `frontend/src/locales/zh-CN/*.json`

---

- [ ] 3. 创建 i18n.ts 插件配置

  **What to do**:
  - 创建 `frontend/src/i18n.ts`
  - 使用 `createI18n` 配置：
    - `legacy: false`（Composition API 模式）
    - `locale: 'zh-CN'`
    - `fallbackLocale: 'zh-CN'`
    - `messages: { 'zh-CN': mergedMessages }`
    - `missingWarn: false`（生产环境静默）
    - `fallbackWarn: false`
  - 导出 `i18n` 实例供 `main.ts` 使用

  **Must NOT do**:
  - 不要创建语言切换函数
  - 不要支持多个 locale
  - 不要启用缺失 key 警告

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 简单的配置文件创建
  - **Skills**: []
  - **Skills Evaluated but Omitted**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2, 4)
  - **Blocks**: Task 5
  - **Blocked By**: Task 2

  **References**:
  - vue-i18n v9 文档: `https://vue-i18n.intlify.dev/guide/essentials/fallback.html`

  **Acceptance Criteria**:
  - [ ] `cat frontend/src/i18n.ts` 显示 createI18n 配置
  - [ ] TypeScript 类型检查通过

  **QA Scenarios**:
  ```
  Scenario: i18n 配置文件有效
    Tool: Bash
    Steps:
      1. cat frontend/src/i18n.ts
    Expected Result: 包含 createI18n 调用，locale 为 'zh-CN'
    Evidence: .sisyphus/evidence/task-3-config.txt

  Scenario: TypeScript 类型检查通过
    Tool: Bash
    Steps:
      1. cd frontend && npx vue-tsc --noEmit src/i18n.ts
    Expected Result: 无类型错误
    Evidence: .sisyphus/evidence/task-3-types.txt
  ```

  **Commit**: YES (groups with Wave 1)
  - Message: `feat(i18n): add i18n plugin configuration`
  - Files: `frontend/src/i18n.ts`

---

- [ ] 4. 更新 vite.config.ts 添加 unplugin-vue-i18n

  **What to do**:
  - 在 `frontend/vite.config.ts` 中导入 `VueI18nPlugin` from `@intlify/unplugin-vue-i18n`
  - 添加到 plugins 数组
  - 配置 `include: ['./src/locales/zh-CN/**/*.json']`

  **Must NOT do**:
  - 不要修改其他 Vite 配置
  - 不要修改 SCSS additionalData 配置

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 简单的配置修改
  - **Skills**: []
  - **Skills Evaluated but Omitted**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2, 3)
  - **Blocks**: Task 5
  - **Blocked By**: Task 1

  **References**:
  - `frontend/vite.config.ts` — 当前 Vite 配置

  **Acceptance Criteria**:
  - [ ] `grep -c "vue-i18n" frontend/vite.config.ts` ≥ 1
  - [ ] `cd frontend && npm run build` 通过

  **QA Scenarios**:
  ```
  Scenario: Vite 配置包含 unplugin
    Tool: Bash
    Steps:
      1. grep "vue-i18n" frontend/vite.config.ts
    Expected Result: 包含 VueI18nPlugin 导入和配置
    Evidence: .sisyphus/evidence/task-4-vite.txt

  Scenario: 构建通过
    Tool: Bash
    Steps:
      1. cd frontend && npm run build
    Expected Result: 退出码 0
    Evidence: .sisyphus/evidence/task-4-build.txt
  ```

  **Commit**: YES (groups with Wave 1)
  - Message: `feat(i18n): add unplugin-vue-i18n to Vite config`
  - Files: `frontend/vite.config.ts`

---

- [ ] 5. 更新 main.ts 注册 i18n + App.vue Naive UI locale

  **What to do**:
  - 在 `frontend/src/main.ts` 中：
    - 导入 i18n 实例
    - 在 `app.use(router)` 之前调用 `app.use(i18n)`
  - 在 `frontend/src/App.vue` 中：
    - 导入 `zhCN` from `naive-ui/es/locales`
    - 将 `<n-config-provider :locale="zhCN">` 添加到组件

  **Must NOT do**:
  - 不要修改 MSW 初始化逻辑
  - 不要修改主题 store 初始化

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 涉及两个文件，需要理解现有初始化流程
  - **Skills**: []
  - **Skills Evaluated but Omitted**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2 (with Tasks 6, 7, 8, 9)
  - **Blocks**: Tasks 6-9（组件需要 i18n 注册后才能使用 $t）
  - **Blocked By**: Tasks 1, 2, 3, 4

  **References**:
  - `frontend/src/main.ts` — 当前应用初始化顺序
  - `frontend/src/App.vue` — NConfigProvider 用法

  **Acceptance Criteria**:
  - [ ] `grep "app.use(i18n)" frontend/src/main.ts` 存在
  - [ ] `grep ":locale=" frontend/src/App.vue` 存在
  - [ ] `cd frontend && npm run build` 通过

  **QA Scenarios**:
  ```
  Scenario: i18n 插件注册
    Tool: Bash
    Steps:
      1. grep -A2 "app.use(i18n)" frontend/src/main.ts
    Expected Result: i18n 在 router 之前注册
    Evidence: .sisyphus/evidence/task-5-main.txt

  Scenario: Naive UI locale 注入
    Tool: Bash
    Steps:
      1. grep "zhCN" frontend/src/App.vue
    Expected Result: 包含 zhCN 导入和 :locale 绑定
    Evidence: .sisyphus/evidence/task-5-app.txt

  Scenario: 构建通过
    Tool: Bash
    Steps:
      1. cd frontend && npm run build
    Expected Result: 退出码 0
    Evidence: .sisyphus/evidence/task-5-build.txt
  ```

  **Commit**: YES
  - Message: `feat(i18n): integrate i18n plugin and Naive UI locale`
  - Files: `frontend/src/main.ts`, `frontend/src/App.vue`

---

- [ ] 6. 更新 LoginView.vue 替换 11 个字符串

  **What to do**:
  - 在 `frontend/src/views/LoginView.vue` 中：
    - 导入 `useI18n` from `vue-i18n`
    - 调用 `const { t } = useI18n()`
    - 替换以下字符串：
      - `'Systematic AI Agent Framework'` → `t('common.brand.subtitle')`
      - `'Connect'` (title) → `t('login.title')`
      - `'Enter your backend credentials to get started.'` → `t('login.description')`
      - `'Base URL'` → `t('login.form.baseUrl')`
      - `'API Token'` → `t('login.form.apiToken')`
      - `'Enter your API token'` → `t('login.form.tokenPlaceholder')`
      - `'Connecting...'` → `t('login.form.submitting')`
      - `'Connect'` (button) → `t('login.form.submit')`
      - `'Connection failed. Check your credentials.'` → `t('login.error.connectionFailed')`
      - `'Your credentials are stored locally and never shared.'` → `t('login.footer')`
    - 保留 `'Madousho.ai'` 不翻译

  **Must NOT do**:
  - 不要翻译品牌名 "Madousho.ai"
  - 不要修改组件逻辑或样式
  - 不要修改 API 错误消息（axios 返回的）

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 11 个字符串替换，需要仔细处理模板中的插值
  - **Skills**: []
  - **Skills Evaluated but Omitted**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 5, 7, 8, 9)
  - **Blocks**: Task 10
  - **Blocked By**: Task 5

  **References**:
  - `frontend/src/views/LoginView.vue` — 当前硬编码字符串
  - `frontend/src/locales/zh-CN/login.json` — 翻译文件（Task 2 创建）

  **Acceptance Criteria**:
  - [ ] `grep -c "\$t(" frontend/src/views/LoginView.vue` ≥ 10
  - [ ] `grep -c "useI18n" frontend/src/views/LoginView.vue` ≥ 1
  - [ ] `grep "Madousho.ai" frontend/src/views/LoginView.vue` 仍存在（品牌名不翻译）
  - [ ] `cd frontend && npm run build` 通过

  **QA Scenarios**:
  ```
  Scenario: 字符串替换完成
    Tool: Bash
    Steps:
      1. grep -c "\$t(" frontend/src/views/LoginView.vue
    Expected Result: 至少 10 个 $t() 调用
    Evidence: .sisyphus/evidence/task-6-replace.txt

  Scenario: 品牌名保留
    Tool: Bash
    Steps:
      1. grep "Madousho.ai" frontend/src/views/LoginView.vue
    Expected Result: 仍包含 "Madousho.ai" 文本
    Evidence: .sisyphus/evidence/task-6-brand.txt
  ```

  **Commit**: YES
  - Message: `feat(i18n): translate LoginView component`
  - Files: `frontend/src/views/LoginView.vue`

---

- [ ] 7. 更新 HomeView.vue 替换 1 个字符串

  **What to do**:
  - 在 `frontend/src/views/HomeView.vue` 中：
    - 导入 `useI18n` from `vue-i18n`
    - 调用 `const { t } = useI18n()`
    - 替换 `'已连接'` → `{{ t('home.status.connected') }}`

  **Must NOT do**:
  - 不要修改组件样式或逻辑

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 只有 1 个字符串替换
  - **Skills**: []
  - **Skills Evaluated but Omitted**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 5, 6, 8, 9)
  - **Blocks**: Task 10
  - **Blocked By**: Task 5

  **References**:
  - `frontend/src/views/HomeView.vue:12` — "已连接"

  **Acceptance Criteria**:
  - [ ] `grep "\$t(" frontend/src/views/HomeView.vue` 存在
  - [ ] `grep "已连接" frontend/src/views/HomeView.vue` 不存在（已替换）

  **QA Scenarios**:
  ```
  Scenario: 字符串替换完成
    Tool: Bash
    Steps:
      1. grep "t(" frontend/src/views/HomeView.vue
    Expected Result: 包含 $t() 调用
    Evidence: .sisyphus/evidence/task-7-home.txt
  ```

  **Commit**: YES (groups with Tasks 8, 9)
  - Message: `feat(i18n): translate HomeView component`
  - Files: `frontend/src/views/HomeView.vue`

---

- [ ] 8. 更新 BackendSwitcher.vue 替换 2 个字符串

  **What to do**:
  - 在 `frontend/src/components/BackendSwitcher.vue` 中：
    - 导入 `useI18n` from `vue-i18n`
    - 调用 `const { t } = useI18n()`
    - 替换 `'No backend'` → `t('backend.noBackend')`
    - 替换 `'+ Add new'` → `t('backend.addNew')`

  **Must NOT do**:
  - 不要修改下拉菜单逻辑
  - 不要修改后端切换功能

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 涉及 computed 属性中的字符串替换
  - **Skills**: []
  - **Skills Evaluated but Omitted**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 5, 6, 7, 9)
  - **Blocks**: Task 11
  - **Blocked By**: Task 5

  **References**:
  - `frontend/src/components/BackendSwitcher.vue:11,25` — 需要替换的字符串

  **Acceptance Criteria**:
  - [ ] `grep -c "\$t(" frontend/src/components/BackendSwitcher.vue` ≥ 2
  - [ ] `grep "No backend" frontend/src/components/BackendSwitcher.vue` 不存在
  - [ ] `grep "+ Add new" frontend/src/components/BackendSwitcher.vue` 不存在

  **QA Scenarios**:
  ```
  Scenario: 字符串替换完成
    Tool: Bash
    Steps:
      1. grep "t(" frontend/src/components/BackendSwitcher.vue
    Expected Result: 包含至少 2 个 $t() 调用
    Evidence: .sisyphus/evidence/task-8-backend.txt
  ```

  **Commit**: YES (groups with Tasks 7, 9)
  - Message: `feat(i18n): translate BackendSwitcher component`
  - Files: `frontend/src/components/BackendSwitcher.vue`

---

- [ ] 9. 更新 ThemeSwitcher.vue 替换 2 个 aria-label

  **What to do**:
  - 在 `frontend/src/components/ThemeSwitcher.vue` 中：
    - 导入 `useI18n` from `vue-i18n`
    - 调用 `const { t } = useI18n()`
    - 替换 `'Switch to light theme'` → `t('theme.switchToLight')`
    - 替换 `'Switch to dark theme'` → `t('theme.switchToDark')`

  **Must NOT do**:
  - 不要修改主题切换逻辑
  - 不要修改 emoji 图标

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 简单的 aria-label 替换
  - **Skills**: []
  - **Skills Evaluated but Omitted**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 5, 6, 7, 8)
  - **Blocks**: Task 10
  - **Blocked By**: Task 5

  **References**:
  - `frontend/src/components/ThemeSwitcher.vue:16` — aria-label

  **Acceptance Criteria**:
  - [ ] `grep "t(" frontend/src/components/ThemeSwitcher.vue` 存在
  - [ ] `grep "Switch to" frontend/src/components/ThemeSwitcher.vue` 不存在

  **QA Scenarios**:
  ```
  Scenario: aria-label 替换完成
    Tool: Bash
    Steps:
      1. grep "t(" frontend/src/components/ThemeSwitcher.vue
    Expected Result: 包含 $t() 调用
    Evidence: .sisyphus/evidence/task-9-theme.txt
  ```

  **Commit**: YES (groups with Tasks 7, 8)
  - Message: `feat(i18n): translate ThemeSwitcher aria-labels`
  - Files: `frontend/src/components/ThemeSwitcher.vue`

---

- [ ] 10. 更新 LoginView.test.ts

  **What to do**:
  - 在 `frontend/src/views/__tests__/LoginView.test.ts` 中：
    - 导入 `createI18n` 和 zh-CN 消息
    - 创建 i18n 实例：`legacy: false, locale: 'zh-CN', messages: { 'zh-CN': mergedMessages }`
    - 在 `mountLoginView()` 的 `global.plugins` 中添加 `i18n`
    - 更新断言：
      - `toContain('Connect')` → `toContain('连接')`
      - `toContain('Connecting...')` → `toContain('连接中...')`
      - `toContain('Connection failed. Check your credentials.')` → `toContain('连接失败，请检查你的凭据')`
    - 添加 i18n 冒烟测试：验证 `.form-title` 包含 `'连接'`

  **Must NOT do**:
  - 不要删除现有测试用例
  - 不要修改 mock 配置

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 测试更新需要理解 i18n 注入方式
  - **Skills**: []
  - **Skills Evaluated but Omitted**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3 (with Tasks 11, 12)
  - **Blocks**: Task 13
  - **Blocked By**: Task 6

  **References**:
  - `frontend/src/views/__tests__/LoginView.test.ts` — 当前测试（9 个英文断言）
  - `frontend/src/locales/zh-CN/login.json` — 对应翻译值

  **Acceptance Criteria**:
  - [ ] `grep -c "连接" frontend/src/views/__tests__/LoginView.test.ts` ≥ 3
  - [ ] `grep "Connect" frontend/src/views/__tests__/LoginView.test.ts` 不存在（除品牌名外）
  - [ ] `cd frontend && npm run test:unit -- src/views/__tests__/LoginView.test.ts` 通过

  **QA Scenarios**:
  ```
  Scenario: LoginView 测试全部通过
    Tool: Bash
    Steps:
      1. cd frontend && npm run test:unit -- src/views/__tests__/LoginView.test.ts
    Expected Result: 所有测试通过，0 失败
    Evidence: .sisyphus/evidence/task-10-login-test.txt
  ```

  **Commit**: YES
  - Message: `test(i18n): update LoginView tests for Chinese locale`
  - Files: `frontend/src/views/__tests__/LoginView.test.ts`

---

- [ ] 11. 更新 BackendSwitcher.test.ts

  **What to do**:
  - 在 `frontend/src/components/__tests__/BackendSwitcher.test.ts` 中：
    - 导入 `createI18n` 和 zh-CN 消息
    - 创建 i18n 实例
    - 在 `mountBackendSwitcher()` 的 `global.plugins` 中添加 `i18n`
    - 更新断言：
      - `toBe('No backend')` → `toBe('未连接后端')`
      - `toBe('+ Add new')` → `toBe('添加新后端')`（3 处）

  **Must NOT do**:
  - 不要删除现有测试用例
  - 不要修改 mock 配置

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 测试更新需要理解 i18n 注入方式
  - **Skills**: []
  - **Skills Evaluated but Omitted**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Tasks 10, 12)
  - **Blocks**: Task 13
  - **Blocked By**: Task 8

  **References**:
  - `frontend/src/components/__tests__/BackendSwitcher.test.ts` — 当前测试（4 个英文断言）
  - `frontend/src/locales/zh-CN/backend.json` — 对应翻译值

  **Acceptance Criteria**:
  - [ ] `grep -c "未连接后端\|添加" frontend/src/components/__tests__/BackendSwitcher.test.ts` ≥ 3
  - [ ] `grep "No backend\|+ Add new" frontend/src/components/__tests__/BackendSwitcher.test.ts` 不存在
  - [ ] `cd frontend && npm run test:unit -- src/components/__tests__/BackendSwitcher.test.ts` 通过

  **QA Scenarios**:
  ```
  Scenario: BackendSwitcher 测试全部通过
    Tool: Bash
    Steps:
      1. cd frontend && npm run test:unit -- src/components/__tests__/BackendSwitcher.test.ts
    Expected Result: 所有测试通过，0 失败
    Evidence: .sisyphus/evidence/task-11-backend-test.txt
  ```

  **Commit**: YES
  - Message: `test(i18n): update BackendSwitcher tests for Chinese locale`
  - Files: `frontend/src/components/__tests__/BackendSwitcher.test.ts`

---

- [ ] 12. 添加 i18n 冒烟测试

  **What to do**:
  - 创建 `frontend/src/__tests__/i18n.test.ts`
  - 测试用例：
    - `$t('login.title')` 返回 `'连接'`
    - `$t('backend.noBackend')` 返回 `'未连接后端'`
    - `$t('theme.switchToLight')` 返回 `'切换到浅色主题'`
    - 缺失 key 返回 key 名（fallback 行为）

  **Must NOT do**:
  - 不要测试组件渲染（那是组件测试的工作）
  - 不要测试 vue-i18n 内部功能

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 新测试文件，需要创建
  - **Skills**: []
  - **Skills Evaluated but Omitted**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Tasks 10, 11)
  - **Blocks**: Task 13
  - **Blocked By**: Task 2

  **References**:
  - `frontend/src/locales/zh-CN/*.json` — 翻译值

  **Acceptance Criteria**:
  - [ ] `cat frontend/src/__tests__/i18n.test.ts` 存在
  - [ ] `cd frontend && npm run test:unit -- src/__tests__/i18n.test.ts` 通过
  - [ ] 至少 4 个测试用例

  **QA Scenarios**:
  ```
  Scenario: i18n 冒烟测试通过
    Tool: Bash
    Steps:
      1. cd frontend && npm run test:unit -- src/__tests__/i18n.test.ts
    Expected Result: 所有测试通过
    Evidence: .sisyphus/evidence/task-12-smoke.txt
  ```

  **Commit**: YES
  - Message: `test(i18n): add i18n smoke tests`
  - Files: `frontend/src/__tests__/i18n.test.ts`

---

- [ ] 13. 最终验证

  **What to do**:
  - 运行 `cd frontend && npm run build` — 确保类型检查和构建通过
  - 运行 `cd frontend && npm run test:unit` — 确保所有测试通过
  - 检查覆盖率是否 ≥90%
  - 验证没有遗漏的硬编码英文字符串（排除品牌名和 console.error）

  **Must NOT do**:
  - 不要修改任何文件

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 运行验证命令
  - **Skills**: []
  - **Skills Evaluated but Omitted**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 4
  - **Blocks**: None
  - **Blocked By**: Tasks 10, 11, 12

  **Acceptance Criteria**:
  - [ ] `npm run build` 退出码 0
  - [ ] `npm run test:unit` 全部通过
  - [ ] 覆盖率 ≥90%
  - [ ] 无 TypeScript 错误

  **QA Scenarios**:
  ```
  Scenario: 完整构建通过
    Tool: Bash
    Steps:
      1. cd frontend && npm run build
    Expected Result: 退出码 0，无 TS 错误
    Evidence: .sisyphus/evidence/task-13-build.txt

  Scenario: 所有测试通过
    Tool: Bash
    Steps:
      1. cd frontend && npm run test:unit
    Expected Result: 所有测试通过
    Evidence: .sisyphus/evidence/task-13-test.txt

  Scenario: 覆盖率达标
    Tool: Bash
    Steps:
      1. cd frontend && npm run test:unit -- --coverage
    Expected Result: 覆盖率 ≥90%
    Evidence: .sisyphus/evidence/task-13-coverage.txt
  ```

  **Commit**: NO

---

## Final Verification Wave

> 4 个审查代理并行运行，全部必须 APPROVE。将综合结果呈现给用户，获得明确的 "okay" 后再完成。

- [ ] F1. **计划合规审计** — `oracle`
  端到端阅读计划。对于每个 "必须有"：验证实现存在。对于每个 "必须没有"：搜索代码库中是否有违规模式。检查证据文件存在于 .sisyphus/evidence/。比较交付物与计划。

- [ ] F2. **代码质量审查** — `unspecified-high`
  运行 `npm run build` + `npm run test:unit`。检查所有更改的文件：无 `as any`/`@ts-ignore`，无空 catch，无 console.log，无注释掉的代码，无未使用的导入。检查 AI slop：过多注释，过度抽象，通用名称。

- [ ] F3. **翻译完整性检查** — `deep`
  扫描所有 .vue 文件，确认没有遗漏的硬编码英文字符串（品牌名和 console.error 除外）。检查翻译键与组件使用的一致性。

- [ ] F4. **测试完整性检查** — `unspecified-high`
  确认所有受影响的测试都已更新。验证测试中的 i18n 注入方式一致。检查新增的冒烟测试覆盖了关键翻译键。

---

## Commit Strategy

**Wave 1**: `feat(i18n): install vue-i18n and unplugin dependencies + add locale files + plugin config + vite config`
- Files: `package.json`, `package-lock.json`, `src/locales/zh-CN/*.json`, `src/i18n.ts`, `vite.config.ts`

**Wave 2**: `feat(i18n): integrate i18n plugin and translate all components`
- Files: `main.ts`, `App.vue`, `LoginView.vue`, `HomeView.vue`, `BackendSwitcher.vue`, `ThemeSwitcher.vue`

**Wave 3**: `test(i18n): update tests for Chinese locale`
- Files: `LoginView.test.ts`, `BackendSwitcher.test.ts`, `i18n.test.ts`

---

## Success Criteria

### 验证命令
```bash
cd frontend && npm run build        # 退出码 0
cd frontend && npm run type-check   # 退出码 0
cd frontend && npm run test:unit    # 全部通过
cd frontend && npm run test:unit -- --coverage  # ≥90%
```

### 最终检查清单
- [ ] vue-i18n v9 和 unplugin-vue-i18n 已安装
- [ ] 5 个 zh-CN 翻译文件存在且有效
- [ ] i18n.ts 插件配置文件存在
- [ ] vite.config.ts 包含 unplugin-vue-i18n
- [ ] main.ts 在 router 之前注册 i18n
- [ ] App.vue 注入 Naive UI zhCN locale
- [ ] 所有 4 个组件使用 $t() 替换硬编码字符串
- [ ] 品牌名 "Madousho.ai" 保持英文
- [ ] LoginView.test.ts 和 BackendSwitcher.test.ts 断言使用中文
- [ ] i18n 冒烟测试存在并通过
- [ ] npm run build 通过
- [ ] npm run test:unit 全部通过
