import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createI18n } from 'vue-i18n'
import BackendSwitcher from '../BackendSwitcher.vue'
import common from '@/locales/zh-CN/common.json'
import login from '@/locales/zh-CN/login.json'
import home from '@/locales/zh-CN/home.json'
import backend from '@/locales/zh-CN/backend.json'
import theme from '@/locales/zh-CN/theme.json'

const mockSwitchBackend = vi.fn()
const mockPush = vi.fn()

let mockCurrentBackend: { name?: string; baseUrl: string } | null = null
let mockCurrentBackendIndex = -1
let mockBackendOptions: { label: string; value: number }[] = []

vi.mock('@/stores/auth.store', () => ({
  useAuthStore: () => ({
    currentBackend: mockCurrentBackend,
    currentBackendIndex: mockCurrentBackendIndex,
    backendOptions: mockBackendOptions,
    switchBackend: mockSwitchBackend,
  }),
}))

vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: mockPush,
  }),
}))

const i18n = createI18n({
  legacy: false,
  locale: 'zh-CN',
  fallbackLocale: 'zh-CN',
  messages: { 'zh-CN': { common, login, home, backend, theme } },
})

const NDropdownStub = {
  props: ['options', 'trigger'],
  emits: ['select'],
  data() {
    return { visible: false }
  },
  template: `
    <div class="n-dropdown-stub">
      <div class="n-dropdown-trigger" @click="visible = !visible">
        <slot />
      </div>
      <ul v-if="visible" class="n-dropdown-options">
        <li
          v-for="opt in options"
          :key="opt.key"
          class="n-dropdown-option"
          @click="$emit('select', opt.key); visible = false"
        >
          {{ opt.label }}
        </li>
      </ul>
    </div>
  `,
}

function mountBackendSwitcher() {
  return mount(BackendSwitcher, {
    global: {
      plugins: [i18n],
      stubs: {
        'n-dropdown': NDropdownStub,
      },
    },
  })
}

describe('BackendSwitcher', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockCurrentBackend = null
    mockCurrentBackendIndex = -1
    mockBackendOptions = []
  })

  describe('trigger button', () => {
    it('renders trigger showing backend name when available', () => {
      mockCurrentBackend = { name: 'Production', baseUrl: 'https://prod.example.com' }
      mockCurrentBackendIndex = 0
      mockBackendOptions = [{ label: 'Production', value: 0 }]

      const wrapper = mountBackendSwitcher()

      expect(wrapper.find('.backend-switcher__label').text()).toBe('Production')
    })

    it('renders trigger showing baseUrl when name is not set', () => {
      mockCurrentBackend = { baseUrl: 'https://api.example.com' }
      mockCurrentBackendIndex = 0
      mockBackendOptions = [{ label: 'https://api.example.com', value: 0 }]

      const wrapper = mountBackendSwitcher()

      expect(wrapper.find('.backend-switcher__label').text()).toBe('https://api.example.com')
    })

    it('renders "No backend" when no backend is selected', () => {
      mockCurrentBackend = null
      mockCurrentBackendIndex = -1
      mockBackendOptions = []

      const wrapper = mountBackendSwitcher()

      expect(wrapper.find('.backend-switcher__label').text()).toBe('未连接后端')
    })

    it('renders chevron indicator', () => {
      const wrapper = mountBackendSwitcher()

      expect(wrapper.find('.backend-switcher__chevron').text()).toBe('▾')
    })
  })

  describe('dropdown options', () => {
    it('shows backend options in dropdown when clicked', async () => {
      mockCurrentBackend = { name: 'Backend A', baseUrl: 'https://a.example.com' }
      mockCurrentBackendIndex = 0
      mockBackendOptions = [
        { label: 'Backend A', value: 0 },
        { label: 'Backend B', value: 1 },
      ]

      const wrapper = mountBackendSwitcher()

      expect(wrapper.find('.n-dropdown-options').exists()).toBe(false)

      await wrapper.find('.n-dropdown-trigger').trigger('click')

      const options = wrapper.findAll('.n-dropdown-option')
      expect(options).toHaveLength(3)
      expect(options[0]!.text()).toBe('✓ Backend A')
      expect(options[1]!.text()).toBe('Backend B')
      expect(options[2]!.text()).toBe('添加新后端')
    })

    it('shows ✓ prefix on current backend option', async () => {
      mockCurrentBackend = { baseUrl: 'https://x.com' }
      mockCurrentBackendIndex = 1
      mockBackendOptions = [
        { label: 'First', value: 0 },
        { label: 'Second', value: 1 },
        { label: 'Third', value: 2 },
      ]

      const wrapper = mountBackendSwitcher()
      await wrapper.find('.n-dropdown-trigger').trigger('click')

      const options = wrapper.findAll('.n-dropdown-option')
      expect(options[0]!.text()).toBe('First')
      expect(options[1]!.text()).toBe('✓ Second')
      expect(options[2]!.text()).toBe('Third')
    })

    it('always includes "Add new" option', async () => {
      mockCurrentBackend = { baseUrl: 'https://x.com' }
      mockCurrentBackendIndex = 0
      mockBackendOptions = [{ label: 'Only', value: 0 }]

      const wrapper = mountBackendSwitcher()
      await wrapper.find('.n-dropdown-trigger').trigger('click')

      const options = wrapper.findAll('.n-dropdown-option')
      expect(options).toHaveLength(2)
      expect(options[1]!.text()).toBe('添加新后端')
    })
  })

  describe('switchBackend', () => {
    it('calls switchBackend when selecting a different backend', async () => {
      mockCurrentBackend = { name: 'Backend A', baseUrl: 'https://a.example.com' }
      mockCurrentBackendIndex = 0
      mockBackendOptions = [
        { label: 'Backend A', value: 0 },
        { label: 'Backend B', value: 1 },
      ]

      const wrapper = mountBackendSwitcher()
      await wrapper.find('.n-dropdown-trigger').trigger('click')

      const options = wrapper.findAll('.n-dropdown-option')
      await options[1]!.trigger('click')

      expect(mockSwitchBackend).toHaveBeenCalledWith(1)
    })

    it('does NOT call switchBackend when selecting current backend', async () => {
      mockCurrentBackend = { name: 'Backend A', baseUrl: 'https://a.example.com' }
      mockCurrentBackendIndex = 0
      mockBackendOptions = [
        { label: 'Backend A', value: 0 },
        { label: 'Backend B', value: 1 },
      ]

      const wrapper = mountBackendSwitcher()
      await wrapper.find('.n-dropdown-trigger').trigger('click')

      const options = wrapper.findAll('.n-dropdown-option')
      await options[0]!.trigger('click')

      expect(mockSwitchBackend).not.toHaveBeenCalled()
    })
  })

  describe('add new backend', () => {
    it('shows "+ Add new" option in dropdown', async () => {
      mockCurrentBackend = { baseUrl: 'https://x.com' }
      mockCurrentBackendIndex = 0
      mockBackendOptions = [{ label: 'X', value: 0 }]

      const wrapper = mountBackendSwitcher()
      await wrapper.find('.n-dropdown-trigger').trigger('click')

      const options = wrapper.findAll('.n-dropdown-option')
      const addOption = options[options.length - 1]
      expect(addOption?.text()).toBe('添加新后端')
    })

    it('calls router.push("/login") when "Add new" is selected', async () => {
      mockCurrentBackend = { baseUrl: 'https://x.com' }
      mockCurrentBackendIndex = 0
      mockBackendOptions = [{ label: 'X', value: 0 }]

      const wrapper = mountBackendSwitcher()
      await wrapper.find('.n-dropdown-trigger').trigger('click')

      const options = wrapper.findAll('.n-dropdown-option')
      const addOption = options[options.length - 1]
      await addOption!.trigger('click')

      expect(mockPush).toHaveBeenCalledWith('/login')
    })

    it('does NOT call switchBackend when "Add new" is selected', async () => {
      mockCurrentBackend = { baseUrl: 'https://x.com' }
      mockCurrentBackendIndex = 0
      mockBackendOptions = [{ label: 'X', value: 0 }]

      const wrapper = mountBackendSwitcher()
      await wrapper.find('.n-dropdown-trigger').trigger('click')

      const options = wrapper.findAll('.n-dropdown-option')
      const addOption = options[options.length - 1]
      await addOption!.trigger('click')

      expect(mockSwitchBackend).not.toHaveBeenCalled()
    })
  })
})
