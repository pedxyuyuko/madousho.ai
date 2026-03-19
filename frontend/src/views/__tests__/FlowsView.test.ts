import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createI18n } from 'vue-i18n'
import common from '@/locales/zh-CN/common.json'
import login from '@/locales/zh-CN/login.json'
import home from '@/locales/zh-CN/home.json'
import backend from '@/locales/zh-CN/backend.json'
import theme from '@/locales/zh-CN/theme.json'
import admin from '@/locales/zh-CN/admin.json'
import FlowsView from '../FlowsView.vue'
import type { FlowListResponse } from '@/types/flow'

const mockGet = vi.fn()

vi.mock('@/api/client', () => ({
  default: {
    get: (...args: unknown[]) => mockGet(...args),
  },
}))

const NSpinStub = {
  props: { size: String },
  template: '<div class="n-spin-stub" data-testid="n-spin"><slot /></div>',
}

const NEmptyStub = {
  props: { description: String },
  template: '<div class="n-empty-stub" data-testid="n-empty">{{ description }}</div>',
}

const NResultStub = {
  props: { status: String, title: String },
  template: '<div class="n-result-stub" data-testid="n-result" :data-status="status">{{ title }}</div>',
}

const NCardStub = {
  template: '<div class="n-card-stub" data-testid="n-card"><header><slot name="header" /></header><slot /></div>',
}

const NTagStub = {
  props: { type: String, size: String },
  template: '<span class="n-tag-stub" data-testid="n-tag" :data-type="type"><slot /></span>',
}

const NCollapseStub = {
  template: '<div class="n-collapse-stub" data-testid="n-collapse"><slot /></div>',
}

const NCollapseItemStub = {
  props: { title: String, name: String },
  template: '<div class="n-collapse-item-stub" data-testid="n-collapse-item"><div>{{ title }}</div><slot /></div>',
}

const i18n = createI18n({
  legacy: false,
  locale: 'zh-CN',
  fallbackLocale: 'zh-CN',
  messages: { 'zh-CN': { common, login, home, backend, theme, admin } },
})

function mountFlowsView() {
  const pinia = createPinia()
  setActivePinia(pinia)
  return mount(FlowsView, {
    global: {
      plugins: [pinia, i18n],
      stubs: {
        'n-spin': NSpinStub,
        'n-empty': NEmptyStub,
        'n-result': NResultStub,
        'n-card': NCardStub,
        'n-tag': NTagStub,
        'n-collapse': NCollapseStub,
        'n-collapse-item': NCollapseItemStub,
      },
    },
  })
}

const mockFlowResponse: FlowListResponse = {
  items: [
    {
      uuid: '550e8400-e29b-41d4-a716-446655440000',
      name: '测试流程',
      description: '这是一个测试流程',
      plugin: 'text-analyzer',
      tasks: ['task-001'],
      status: 'finished',
      flow_template: null,
      created_at: '2026-03-19T10:00:00Z',
    },
    {
      uuid: '660e8400-e29b-41d4-a716-446655440001',
      name: '图像流程',
      description: null,
      plugin: 'image-processor',
      tasks: [],
      status: 'processing',
      flow_template: 'default-template',
      created_at: '2026-03-19T11:00:00Z',
    },
    {
      uuid: '770e8400-e29b-41d4-a716-446655440002',
      name: '新建流程',
      description: '刚创建的流程',
      plugin: 'new-plugin',
      tasks: null,
      status: 'created',
      flow_template: null,
      created_at: '2026-03-19T12:00:00Z',
    },
  ],
  total: 3,
  offset: 0,
  limit: 20,
}

describe('FlowsView', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders loading state with NSpin initially', () => {
    mockGet.mockReturnValue(new Promise(() => {}))

    const wrapper = mountFlowsView()

    expect(wrapper.find('[data-testid="n-spin"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="n-empty"]').exists()).toBe(false)
    expect(wrapper.find('[data-testid="n-result"]').exists()).toBe(false)
  })

  it('renders empty state when API returns no flows', async () => {
    mockGet.mockResolvedValue({ data: { items: [], total: 0, offset: 0, limit: 20 } })

    const wrapper = mountFlowsView()
    await flushPromises()

    expect(wrapper.find('[data-testid="n-spin"]').exists()).toBe(false)
    expect(wrapper.find('[data-testid="n-empty"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('暂无工作流')
  })

  it('renders error state on API failure', async () => {
    mockGet.mockRejectedValue(new Error('Network error'))

    const wrapper = mountFlowsView()
    await flushPromises()

    expect(wrapper.find('[data-testid="n-result"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="n-result"]').attributes('data-status')).toBe('error')
    expect(wrapper.text()).toContain('加载失败')
  })

  it('renders flow cards with correct status tags', async () => {
    mockGet.mockResolvedValue({ data: mockFlowResponse })

    const wrapper = mountFlowsView()
    await flushPromises()

    const cards = wrapper.findAll('[data-testid="n-card"]')
    expect(cards).toHaveLength(3)

    const tags = wrapper.findAll('[data-testid="n-tag"]')
    expect(tags).toHaveLength(3)
    expect(tags[0]!.attributes('data-type')).toBe('success')
    expect(tags[1]!.attributes('data-type')).toBe('warning')
    expect(tags[2]!.attributes('data-type')).toBe('default')
  })

  it('shows em dash for null description', async () => {
    mockGet.mockResolvedValue({ data: mockFlowResponse })

    const wrapper = mountFlowsView()
    await flushPromises()

    expect(wrapper.text()).toContain('—')
    expect(wrapper.text()).toContain('图像流程')
  })

  it('shows error state on 401 (interceptor handles redirect)', async () => {
    const error401 = { response: { status: 401 } }
    mockGet.mockRejectedValue(error401)

    const wrapper = mountFlowsView()
    await flushPromises()

    expect(wrapper.find('[data-testid="n-result"]').exists()).toBe(true)
  })

  it('shows error state on 403', async () => {
    const error403 = { response: { status: 403 } }
    mockGet.mockRejectedValue(error403)

    const wrapper = mountFlowsView()
    await flushPromises()

    expect(wrapper.find('[data-testid="n-result"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="n-result"]').attributes('data-status')).toBe('error')
  })

  it('calls apiClient with /flows endpoint', async () => {
    mockGet.mockResolvedValue({ data: mockFlowResponse })

    mountFlowsView()
    await flushPromises()

    expect(mockGet).toHaveBeenCalledWith('/flows')
  })

  it('renders page title from i18n', async () => {
    mockGet.mockResolvedValue({ data: mockFlowResponse })

    const wrapper = mountFlowsView()
    await flushPromises()

    expect(wrapper.find('.flows-title').text()).toBe('工作流列表')
  })

  it('renders expandable collapse for each flow', async () => {
    mockGet.mockResolvedValue({ data: mockFlowResponse })

    const wrapper = mountFlowsView()
    await flushPromises()

    const collapseItems = wrapper.findAll('[data-testid="n-collapse-item"]')
    expect(collapseItems).toHaveLength(3)
  })
})
