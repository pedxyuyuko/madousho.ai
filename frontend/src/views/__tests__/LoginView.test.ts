import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
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
  props: ['value', 'disabled', 'type'],
  emits: ['update:value'],
  template: `<input
    :value="value"
    :disabled="disabled"
    :type="type || 'text'"
    v-bind="$attrs"
    @input="$emit('update:value', $event.target.value)"
  />`,
}

const NButtonStub = {
  props: ['disabled', 'loading'],
  template: `<button :disabled="disabled || loading" v-bind="$attrs"><slot /></button>`,
}

const NAlertStub = {
  template: `<div v-bind="$attrs"><slot /></div>`,
}

function mountLoginView() {
  const pinia = createPinia()
  setActivePinia(pinia)
  return mount(LoginView, {
    global: {
      plugins: [pinia],
      stubs: {
        'n-input': NInputStub,
        'n-button': NButtonStub,
        'n-alert': NAlertStub,
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

    expect(wrapper.find('button').exists()).toBe(true)
    expect(wrapper.text()).toContain('Connect')
  })

  it('has left panel (gradient) and right panel (form) structure', () => {
    const wrapper = mountLoginView()

    expect(wrapper.find('.login-gradient').exists()).toBe(true)
    expect(wrapper.find('.login-form-panel').exists()).toBe(true)
    expect(wrapper.find('.brand-title').text()).toBe('Madousho.ai')
  })

  it('shows validation — button disabled when fields are empty', async () => {
    const wrapper = mountLoginView()

    const button = wrapper.find('button')
    expect(button.attributes('disabled')).toBeDefined()

    await setFields(wrapper, 'http://localhost:8000', '')
    expect(button.attributes('disabled')).toBeDefined()

    await setFields(wrapper, '', 'test-token')
    expect(button.attributes('disabled')).toBeDefined()
  })

  it('enables button when both fields have values', async () => {
    const wrapper = mountLoginView()
    await setFields(wrapper, 'http://localhost:8000', 'test-token')

    const button = wrapper.find('button')
    expect(button.attributes('disabled')).toBeUndefined()
  })

  it('calls authStore.login() on form submit', async () => {
    mockLogin.mockResolvedValue(undefined)
    const wrapper = mountLoginView()
    await setFields(wrapper, 'http://localhost:8000', 'test-token')

    await wrapper.find('button').trigger('click')
    await flushPromises()

    expect(mockLogin).toHaveBeenCalledWith('http://localhost:8000', 'test-token')
  })

  it('shows loading state during login', async () => {
    let resolveLogin!: () => void
    mockLogin.mockReturnValue(new Promise<void>((r) => { resolveLogin = r }))

    const wrapper = mountLoginView()
    await setFields(wrapper, 'http://localhost:8000', 'test-token')

    await wrapper.find('button').trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('Connecting...')

    resolveLogin()
    await flushPromises()

    expect(wrapper.text()).toContain('Connect')
    expect(wrapper.text()).not.toContain('Connecting...')
  })

  it('shows error alert on login failure', async () => {
    mockLogin.mockRejectedValue(new Error('Invalid token'))
    const wrapper = mountLoginView()
    await setFields(wrapper, 'http://localhost:8000', 'bad-token')

    await wrapper.find('button').trigger('click')
    await flushPromises()

    expect(wrapper.find('.form-error').exists()).toBe(true)
    expect(wrapper.text()).toContain('Invalid token')
  })

  it('shows default error message when error has no message', async () => {
    mockLogin.mockRejectedValue(new Error())
    const wrapper = mountLoginView()
    await setFields(wrapper, 'http://localhost:8000', 'bad-token')

    await wrapper.find('button').trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('Connection failed. Check your credentials.')
  })

  it('redirects to / on successful login', async () => {
    mockLogin.mockResolvedValue(undefined)
    const wrapper = mountLoginView()
    await setFields(wrapper, 'http://localhost:8000', 'test-token')

    await wrapper.find('button').trigger('click')
    await flushPromises()

    expect(mockPush).toHaveBeenCalledWith('/')
  })

  it('trims input values before calling login', async () => {
    mockLogin.mockResolvedValue(undefined)
    const wrapper = mountLoginView()
    await setFields(wrapper, '  http://localhost:8000  ', '  test-token  ')

    await wrapper.find('button').trigger('click')
    await flushPromises()

    expect(mockLogin).toHaveBeenCalledWith('http://localhost:8000', 'test-token')
  })
})
