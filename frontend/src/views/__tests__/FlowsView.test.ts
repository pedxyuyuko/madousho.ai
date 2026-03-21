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
import type { Flow, FlowListResponse } from '@/types/flow'

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
  emits: ['click'],
  template:
    '<div class="n-card-stub" data-testid="n-card" v-bind="$attrs" @click="$emit(\'click\')"><header><slot name="header" /></header><slot /></div>',
}

const NTagStub = {
  props: { type: String, size: String },
  template: '<span class="n-tag-stub" data-testid="n-tag" :data-type="type"><slot /></span>',
}

const NTimeStub = {
  props: { time: { type: [Date, Number], required: true }, format: String },
  template:
    '<time class="n-time-stub" data-testid="n-time">{{ time instanceof Date ? time.toISOString() : new Date(time).toISOString() }}</time>',
}

const i18n = createI18n({
  legacy: false,
  locale: 'zh-CN',
  fallbackLocale: 'zh-CN',
  messages: { 'zh-CN': { common, login, home, backend, theme, admin } },
})

function buildFlowsQuery(keyword: string, status: Flow['status'] | null) {
  const trimmedKeyword = keyword.trim()
  const params: Record<string, string> = {}

  if (trimmedKeyword) {
    params.name = trimmedKeyword
  }

  if (status) {
    params.status = status
  }

  return Object.keys(params).length === 0 ? undefined : { params }
}

function parseCreatedAt(value: string) {
  const timestamp = Date.parse(value)
  return Number.isNaN(timestamp) ? null : timestamp
}

function sortFlowsByCreatedAt(flows: Flow[], direction: 'asc' | 'desc') {
  return [...flows].sort((left, right) => {
    const leftTime = parseCreatedAt(left.created_at)
    const rightTime = parseCreatedAt(right.created_at)

    if (leftTime === null && rightTime === null) {
      return left.uuid.localeCompare(right.uuid)
    }

    if (leftTime === null) {
      return 1
    }

    if (rightTime === null) {
      return -1
    }

    if (leftTime === rightTime) {
      return left.uuid.localeCompare(right.uuid)
    }

    return direction === 'asc' ? leftTime - rightTime : rightTime - leftTime
  })
}

function filterFlowsByKeywordAndStatus(flows: Flow[], keyword: string, status: Flow['status'] | null) {
  const normalizedKeyword = keyword.trim().toLowerCase()

  return flows.filter((flow) => {
    const matchesKeyword =
      normalizedKeyword.length === 0 ||
      flow.name.toLowerCase().includes(normalizedKeyword) ||
      (flow.description ?? '').toLowerCase().includes(normalizedKeyword)

    const matchesStatus = status === null || flow.status === status

    return matchesKeyword && matchesStatus
  })
}

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
        'n-time': NTimeStub,
        transition: false,
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
      plugin: '',
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

  it('renders card-based flow rows with plugin and status tags', async () => {
    mockGet.mockResolvedValue({ data: mockFlowResponse })

    const wrapper = mountFlowsView()
    await flushPromises()

    const cards = wrapper.findAll('[data-testid="n-card"]')
    expect(cards).toHaveLength(3)

    expect(cards[0]!.text()).toContain('测试流程')
    expect(cards[0]!.text()).toContain('text-analyzer')
    expect(cards[0]!.text()).toContain('finished')

    expect(cards[1]!.text()).toContain('图像流程')
    expect(cards[1]!.text()).toContain('image-processor')
    expect(cards[1]!.text()).toContain('processing')

    expect(cards[2]!.text()).toContain('新建流程')
    expect(cards[2]!.text()).not.toContain('task-001')

    const tagTypes = wrapper
      .findAll('[data-testid="n-tag"]')
      .map((tag) => ({ text: tag.text(), type: tag.attributes('data-type') }))

    expect(tagTypes).toEqual([
      { text: 'text-analyzer', type: 'info' },
      { text: 'finished', type: 'success' },
      { text: 'image-processor', type: 'info' },
      { text: 'processing', type: 'warning' },
      { text: 'created', type: 'default' },
    ])
  })

  it('shows em dash for null description', async () => {
    mockGet.mockResolvedValue({ data: mockFlowResponse })

    const wrapper = mountFlowsView()
    await flushPromises()

    expect(wrapper.text()).toContain('—')
    expect(wrapper.text()).toContain('图像流程')
  })

  it('toggles card expansion and keeps visible card details on click', async () => {
    mockGet.mockResolvedValue({ data: mockFlowResponse })

    const wrapper = mountFlowsView()
    await flushPromises()

    const cards = wrapper.findAll('[data-testid="n-card"]')
    expect(wrapper.text()).not.toContain('Tasks: task-001')

    await cards[0]!.trigger('click')

    expect(wrapper.text()).toContain('Tasks:')
    expect(wrapper.text()).toContain('task-001')
    expect(wrapper.find('.flow-card--expanded').exists()).toBe(true)

    await cards[0]!.trigger('click')

    expect(wrapper.text()).not.toContain('Tasks: task-001')
    expect(wrapper.find('.flow-card--expanded').exists()).toBe(false)
  })

  it('shows template details only after a card is expanded', async () => {
    mockGet.mockResolvedValue({ data: mockFlowResponse })

    const wrapper = mountFlowsView()
    await flushPromises()

    const cards = wrapper.findAll('[data-testid="n-card"]')
    expect(wrapper.text()).not.toContain('default-template')

    await cards[1]!.trigger('click')

    expect(wrapper.text()).toContain('Template:')
    expect(wrapper.text()).toContain('default-template')
  })

  it('shows error state on 401 while interceptor handles redirect', async () => {
    mockGet.mockRejectedValue({ response: { status: 401 } })

    const wrapper = mountFlowsView()
    await flushPromises()

    expect(wrapper.find('[data-testid="n-result"]').exists()).toBe(true)
  })

  it('shows error state on 403', async () => {
    mockGet.mockRejectedValue({ response: { status: 403 } })

    const wrapper = mountFlowsView()
    await flushPromises()

    expect(wrapper.find('[data-testid="n-result"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="n-result"]').attributes('data-status')).toBe('error')
  })

  it('calls apiClient with the current unfiltered /flows endpoint', async () => {
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

  it('defines the toolbar query contract for keyword, status, reset, and supported backend params only', () => {
    expect(buildFlowsQuery('', null)).toBeUndefined()
    expect(buildFlowsQuery('   ', null)).toBeUndefined()
    expect(buildFlowsQuery('  流程  ', null)).toEqual({
      params: {
        name: '流程',
      },
    })
    expect(buildFlowsQuery('', 'processing')).toEqual({
      params: {
        status: 'processing',
      },
    })
    expect(buildFlowsQuery('  流程  ', 'processing')).toEqual({
      params: {
        name: '流程',
        status: 'processing',
      },
    })

    const resetQuery = buildFlowsQuery('', null)
    expect(resetQuery).toBeUndefined()
    expect(resetQuery).not.toEqual(
      expect.objectContaining({
        params: expect.objectContaining({
          sort: expect.anything(),
        }),
      }),
    )
    expect(buildFlowsQuery('流程', 'processing')).not.toEqual(
      expect.objectContaining({
        params: expect.objectContaining({
          sort_by: expect.anything(),
        }),
      }),
    )
    expect(buildFlowsQuery('流程', 'processing')).not.toEqual(
      expect.objectContaining({
        params: expect.objectContaining({
          order: expect.anything(),
        }),
      }),
    )
    expect(buildFlowsQuery('流程', 'processing')).not.toEqual(
      expect.objectContaining({
        params: expect.objectContaining({
          direction: expect.anything(),
        }),
      }),
    )
  })

  it('defines the future local keyword and status filter contract with filtered-empty behavior', () => {
    expect(filterFlowsByKeywordAndStatus(mockFlowResponse.items, '  测试  ', null).map((flow) => flow.uuid)).toEqual([
      '550e8400-e29b-41d4-a716-446655440000',
    ])

    expect(filterFlowsByKeywordAndStatus(mockFlowResponse.items, '刚创建', null).map((flow) => flow.uuid)).toEqual([
      '770e8400-e29b-41d4-a716-446655440002',
    ])

    expect(filterFlowsByKeywordAndStatus(mockFlowResponse.items, '流程', 'processing').map((flow) => flow.uuid)).toEqual([
      '660e8400-e29b-41d4-a716-446655440001',
    ])

    expect(filterFlowsByKeywordAndStatus(mockFlowResponse.items, 'missing keyword', 'finished')).toEqual([])
    expect(mockFlowResponse.items).toHaveLength(3)
  })

  it('defines the deterministic local created_at sort contract for desc, asc, tie-breaks, and invalid dates', () => {
    const fixture: Flow[] = [
      {
        uuid: 'b-flow',
        name: '第二个',
        description: 'same time',
        plugin: 'plugin-b',
        tasks: null,
        status: 'created',
        flow_template: null,
        created_at: '2026-03-19T10:00:00Z',
      },
      {
        uuid: 'a-flow',
        name: '第一个',
        description: 'same time',
        plugin: 'plugin-a',
        tasks: null,
        status: 'finished',
        flow_template: null,
        created_at: '2026-03-19T10:00:00Z',
      },
      {
        uuid: 'latest-flow',
        name: '最新',
        description: 'latest',
        plugin: 'plugin-latest',
        tasks: null,
        status: 'processing',
        flow_template: null,
        created_at: '2026-03-19T12:00:00Z',
      },
      {
        uuid: 'invalid-flow',
        name: '异常时间',
        description: null,
        plugin: 'plugin-invalid',
        tasks: null,
        status: 'processing',
        flow_template: null,
        created_at: 'not-a-date',
      },
    ]

    expect(sortFlowsByCreatedAt(fixture, 'desc').map((flow) => flow.uuid)).toEqual([
      'latest-flow',
      'a-flow',
      'b-flow',
      'invalid-flow',
    ])

    expect(sortFlowsByCreatedAt(fixture, 'asc').map((flow) => flow.uuid)).toEqual([
      'a-flow',
      'b-flow',
      'latest-flow',
      'invalid-flow',
    ])

    expect(fixture.map((flow) => flow.uuid)).toEqual(['b-flow', 'a-flow', 'latest-flow', 'invalid-flow'])
  })
})
