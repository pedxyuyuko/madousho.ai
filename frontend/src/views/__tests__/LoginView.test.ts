import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createI18n } from 'vue-i18n'
import common from '@/locales/zh-CN/common.json'
import login from '@/locales/zh-CN/login.json'
import home from '@/locales/zh-CN/home.json'
import backend from '@/locales/zh-CN/backend.json'
import theme from '@/locales/zh-CN/theme.json'
import LoginView from '../LoginView.vue'

const mockLogin = vi.fn()
const mockPush = vi.fn()

vi.mock('@/stores/auth.store', () => ({
  useAuthStore: () => ({
    login: mockLogin,
    logout: vi.fn(),
  }),
}))

vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: mockPush,
  }),
}))

const NInputStub = {
  props: {
    value: { type: String, default: '' },
    disabled: Boolean,
    type: { type: String, default: 'text' },
  },
  emits: ['update:value'],
  template: `<input
    :value="value"
    :disabled="disabled"
    :type="type || 'text'"
    :id="$attrs.id"
    :placeholder="$attrs.placeholder"
    :class="$attrs.class"
    @input="$emit('update:value', $event.target.value)"
  />`,
}

const NButtonStub = {
  props: {
    disabled: Boolean,
    loading: Boolean,
  },
  emits: ['click'],
  template: `<button
    type="button"
    :disabled="disabled || loading"
    :class="$attrs.class"
    @click="$emit('click', $event)"
  ><slot /></button>`,
}

const NAlertStub = {
  props: { type: String },
  template: `<div :class="$attrs.class"><slot /></div>`,
}

const ThemeSwitcherStub = {
  template: '<div class="theme-switcher-stub" />',
}

const i18n = createI18n({
  legacy: false,
  locale: 'zh-CN',
  fallbackLocale: 'zh-CN',
  messages: { 'zh-CN': { common, login, home, backend, theme } },
})

function mountLoginView() {
  const pinia = createPinia()
  setActivePinia(pinia)
  return mount(LoginView, {
    global: {
      plugins: [pinia, i18n],
      stubs: {
        'n-input': NInputStub,
        'n-button': NButtonStub,
        'n-alert': NAlertStub,
        'ThemeSwitcher': ThemeSwitcherStub,
      },
    },
  })
}

async function setFields(
  wrapper: ReturnType<typeof mountLoginView>,
  baseUrl: string,
  token: string,
) {
  const inputs = wrapper.findAll('input')
  await inputs[0]!.setValue(baseUrl)
  await inputs[1]!.setValue(token)
}

describe('LoginView', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders login form with Base URL input, Token input, and Login button', () => {
    const wrapper = mountLoginView()

    const inputs = wrapper.findAll('input')
    expect(inputs).toHaveLength(2)
    expect(inputs[0]!.attributes('id')).toBe('base-url')
    expect(inputs[1]!.attributes('id')).toBe('token')

    expect(wrapper.find('.submit-btn').exists()).toBe(true)
    expect(wrapper.text()).toContain('连接')
  })

  it('has left panel (gradient) and right panel (form) structure', () => {
    const wrapper = mountLoginView()

    expect(wrapper.find('.login-gradient').exists()).toBe(true)
    expect(wrapper.find('.login-form-panel').exists()).toBe(true)
    expect(wrapper.find('.brand-title').text()).toBe('Madousho.ai')
  })

  it('shows validation — button disabled when fields are empty', async () => {
    const wrapper = mountLoginView()

    const button = wrapper.find('.submit-btn')
    expect(button.attributes('disabled')).toBeDefined()

    await setFields(wrapper, 'http://localhost:8000', '')
    expect(button.attributes('disabled')).toBeDefined()

    await setFields(wrapper, '', 'test-token')
    expect(button.attributes('disabled')).toBeDefined()
  })

  it('enables button when both fields have values', async () => {
    const wrapper = mountLoginView()
    await setFields(wrapper, 'http://localhost:8000', 'test-token')

    const button = wrapper.find('.submit-btn')
    expect(button.attributes('disabled')).toBeUndefined()
  })

  it('calls authStore.login() on form submit', async () => {
    mockLogin.mockResolvedValue(undefined)
    const wrapper = mountLoginView()
    await setFields(wrapper, 'http://localhost:8000', 'test-token')

    await wrapper.find('.submit-btn').trigger('click')
    await flushPromises()

    expect(mockLogin).toHaveBeenCalledWith('http://localhost:8000', 'test-token')
  })

  it('shows loading state during login', async () => {
    let resolveLogin!: () => void
    mockLogin.mockReturnValue(new Promise<void>((r) => { resolveLogin = r }))

    const wrapper = mountLoginView()
    await setFields(wrapper, 'http://localhost:8000', 'test-token')

    await wrapper.find('.submit-btn').trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('连接中...')

    resolveLogin()
    await flushPromises()

    expect(wrapper.text()).toContain('连接')
    expect(wrapper.text()).not.toContain('连接中...')
  })

  it('shows error alert on login failure', async () => {
    mockLogin.mockRejectedValue(new Error('Invalid token'))
    const wrapper = mountLoginView()
    await setFields(wrapper, 'http://localhost:8000', 'bad-token')

    await wrapper.find('.submit-btn').trigger('click')
    await flushPromises()

    expect(wrapper.find('.form-error').exists()).toBe(true)
    expect(wrapper.text()).toContain('Invalid token')
  })

  it('shows default error message when error has no message', async () => {
    mockLogin.mockRejectedValue(new Error())
    const wrapper = mountLoginView()
    await setFields(wrapper, 'http://localhost:8000', 'bad-token')

    await wrapper.find('.submit-btn').trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('连接失败，请检查你的凭据')
  })

  it('redirects to / on successful login', async () => {
    mockLogin.mockResolvedValue(undefined)
    const wrapper = mountLoginView()
    await setFields(wrapper, 'http://localhost:8000', 'test-token')

    await wrapper.find('.submit-btn').trigger('click')
    await flushPromises()

    expect(mockPush).toHaveBeenCalledWith('/')
  })

  it('trims input values before calling login', async () => {
    mockLogin.mockResolvedValue(undefined)
    const wrapper = mountLoginView()
    await setFields(wrapper, '  http://localhost:8000  ', '  test-token  ')

    await wrapper.find('.submit-btn').trigger('click')
    await flushPromises()

    expect(mockLogin).toHaveBeenCalledWith('http://localhost:8000', 'test-token')
  })
})
