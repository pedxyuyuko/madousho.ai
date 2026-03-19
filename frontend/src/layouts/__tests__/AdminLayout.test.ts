import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createI18n } from 'vue-i18n'
import AdminLayout from '@/layouts/AdminLayout.vue'
import common from '@/locales/zh-CN/common.json'
import login from '@/locales/zh-CN/login.json'
import home from '@/locales/zh-CN/home.json'
import backend from '@/locales/zh-CN/backend.json'
import theme from '@/locales/zh-CN/theme.json'
import admin from '@/locales/zh-CN/admin.json'

const mockLogout = vi.fn()
const mockPush = vi.fn()

vi.mock('@/stores/auth.store', () => ({
  useAuthStore: () => ({
    logout: mockLogout,
  }),
}))

vi.mock('vue-router', async () => {
  const actual = await vi.importActual<typeof import('vue-router')>('vue-router')
  return {
    ...actual,
    useRouter: () => ({
      push: mockPush,
      resolve: ({ name }: { name: string }) => {
        const routes: Record<string, string> = { home: '/', flows: '/flows', login: '/login' }
        return { name, path: routes[name] ?? `/${name}` }
      },
    }),
    useRoute: () => ({
      name: 'home',
    }),
  }
})

const i18n = createI18n({
  legacy: false,
  locale: 'zh-CN',
  fallbackLocale: 'zh-CN',
  messages: { 'zh-CN': { common, login, home, backend, theme, admin } },
})

const LayoutStub = {
  props: ['hasSider', 'position', 'bordered'],
  template: '<div class="n-layout-stub" :data-has-sider="hasSider"><slot /></div>',
}

const LayoutSiderStub = {
  props: ['collapsed', 'collapsedWidth', 'width', 'collapseMode', 'showTrigger', 'contentStyle', 'bordered'],
  emits: ['collapse', 'expand'],
  template: '<aside class="n-layout-sider-stub" :data-collapsed="String(collapsed)"><slot /></aside>',
}

const LayoutHeaderStub = {
  props: ['bordered'],
  template: '<header class="n-layout-header-stub"><slot /></header>',
}

const LayoutContentStub = {
  template: '<main class="n-layout-content-stub"><slot /></main>',
}

const NButtonStub = {
  props: ['quaternary', 'circle', 'tertiary', 'type', 'ariaLabel'],
  emits: ['click'],
  template: `
    <button
      type="button"
      :aria-label="ariaLabel || $attrs['aria-label']"
      :data-testid="$attrs['data-testid']"
      :class="$attrs.class"
      @click="$emit('click', $event)"
    >
      <slot name="icon" />
      <slot />
    </button>
  `,
}

const NMenuStub = {
  props: ['options', 'collapsed', 'collapsedWidth', 'collapsedIconSize', 'value'],
  template: `
    <nav class="n-menu-stub" :data-collapsed="String(collapsed)">
      <span v-for="item in options" :key="item.key" class="menu-label">{{ item.label }}</span>
    </nav>
  `,
}

const NIconStub = {
  template: '<span class="n-icon-stub" :class="$attrs.class"><slot /></span>',
}

const ThemeSwitcherStub = { template: '<div data-testid="theme-switcher-stub">Theme</div>' }
const LanguageSwitcherStub = { template: '<div data-testid="language-switcher-stub">Lang</div>' }
const BackendSwitcherStub = { template: '<div data-testid="backend-switcher-stub">Backend</div>' }
const ChevronBackOutlineStub = { template: '<svg class="chevron-back-outline" />' }
const SparklesOutlineStub = { template: '<svg class="sparkles-outline" />' }
const RouterViewStub = { template: '<div class="router-view-stub" />' }

function mountAdminLayout() {
  return mount(AdminLayout, {
    global: {
      plugins: [i18n],
      stubs: {
        RouterView: RouterViewStub,
        'n-layout': LayoutStub,
        'n-layout-sider': LayoutSiderStub,
        'n-layout-header': LayoutHeaderStub,
        'n-layout-content': LayoutContentStub,
        'n-button': NButtonStub,
        'n-menu': NMenuStub,
        'n-icon': NIconStub,
        ThemeSwitcher: ThemeSwitcherStub,
        LanguageSwitcher: LanguageSwitcherStub,
        BackendSwitcher: BackendSwitcherStub,
        ChevronBackOutline: ChevronBackOutlineStub,
        SparklesOutline: SparklesOutlineStub,
      },
    },
  })
}

describe('AdminLayout', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders the Naive UI admin shell structure with required test ids', () => {
    const wrapper = mountAdminLayout()

    expect(wrapper.find('[data-testid="admin-layout"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="admin-sidebar"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="admin-header"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="sidebar-toggle"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="logout-btn"]').exists()).toBe(true)
    expect(wrapper.findComponent(RouterViewStub).exists()).toBe(true)
  })

  it('renders localized Dashboard and Flows menu items', () => {
    const wrapper = mountAdminLayout()

    const labels = wrapper.findAll('.menu-label').map((node) => node.text())
    expect(labels).toEqual(['仪表盘', '工作流'])
    expect(wrapper.find('.menu-outline').exists()).toBe(false)
    expect(wrapper.find('.git-branch-outline').exists()).toBe(false)
  })

  it('shows full logo copy when expanded and icon-only state when collapsed', async () => {
    const wrapper = mountAdminLayout()

    expect(wrapper.find('.brand-title').text()).toBe('魔导书')
    expect(wrapper.find('.brand-subtitle').text()).toBe('AI Agent Atelier')

    await wrapper.get('[data-testid="sidebar-toggle"]').trigger('click')

    expect(wrapper.find('.brand-title').exists()).toBe(false)
    expect(wrapper.find('.brand-subtitle').exists()).toBe(false)
    expect(wrapper.find('.brand-mark').exists()).toBe(true)
  })

  it('toggles the sidebar collapsed state from false to true and back', async () => {
    const wrapper = mountAdminLayout()
    const sidebar = wrapper.get('[data-testid="admin-sidebar"]')

    expect(sidebar.attributes('data-collapsed')).toBe('false')

    await wrapper.get('[data-testid="sidebar-toggle"]').trigger('click')
    expect(sidebar.attributes('data-collapsed')).toBe('true')

    await wrapper.get('[data-testid="sidebar-toggle"]').trigger('click')
    expect(sidebar.attributes('data-collapsed')).toBe('false')
  })

  it('renders header actions in the required order', () => {
    const wrapper = mountAdminLayout()
    const actionChildren = wrapper.get('.header-actions').element.children
    const actionTexts = Array.from(actionChildren).map((element) => element.textContent?.trim())

    expect(actionTexts).toEqual(['Theme', 'Lang', 'Backend', '退出登录'])
  })

  it('calls auth logout then redirects to /login when logout is clicked', async () => {
    mockPush.mockResolvedValue(undefined)
    const wrapper = mountAdminLayout()

    await wrapper.get('[data-testid="logout-btn"]').trigger('click')

    expect(mockLogout).toHaveBeenCalledTimes(1)
    expect(mockPush).toHaveBeenCalledWith({ name: 'login', path: '/login' })
    const logoutOrder = mockLogout.mock.invocationCallOrder[0]
    const pushOrder = mockPush.mock.invocationCallOrder[0]

    expect(logoutOrder).toBeDefined()
    expect(pushOrder).toBeDefined()
    expect(logoutOrder!).toBeLessThan(pushOrder!)
  })
})
