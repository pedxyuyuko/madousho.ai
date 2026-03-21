import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createI18n } from 'vue-i18n'
import common from '@/locales/zh-CN/common.json'
import login from '@/locales/zh-CN/login.json'
import home from '@/locales/zh-CN/home.json'
import backend from '@/locales/zh-CN/backend.json'
import theme from '@/locales/zh-CN/theme.json'
import admin from '@/locales/zh-CN/admin.json'
import type { Flow, FlowListResponse } from '@/types/flow'
import FlowsView from '../FlowsView.vue'

const mockGet = vi.fn()

vi.mock('@/api/client', () => ({
  default: {
    get: (...args: unknown[]) => mockGet(...args),
  },
}))

const i18n = createI18n({
  legacy: false,
  locale: 'zh-CN',
  fallbackLocale: 'zh-CN',
  messages: { 'zh-CN': { common, login, home, backend, theme, admin } },
})

const NSpinStub = {
  props: { size: String },
  template: '<div class="n-spin-stub" data-testid="n-spin"><slot /></div>',
}

const NEmptyStub = {
  inheritAttrs: false,
  props: { description: String },
  template: '<div class="n-empty-stub" v-bind="$attrs">{{ description }}</div>',
}

const NResultStub = {
  props: { status: String, title: String },
  template: '<div class="n-result-stub" data-testid="n-result" :data-status="status">{{ title }}</div>',
}

const NCardStub = {
  inheritAttrs: false,
  emits: ['click'],
  template:
    '<div class="n-card-stub" v-bind="$attrs" @click="$emit(\'click\')"><header><slot name="header" /></header><slot /></div>',
}

const NTagStub = {
  props: { type: String, size: String },
  template: '<span class="n-tag-stub" :data-type="type"><slot /></span>',
}

const NTimeStub = {
  props: {
    time: {
      type: [Date, Number],
      required: true,
    },
    format: String,
  },
  template: `
    <time class="n-time-stub">
      {{ Number.isNaN(new Date(time).getTime()) ? 'Invalid Date' : new Date(time).toISOString() }}
    </time>
  `,
}

const NFormStub = {
  template: '<form class="n-form-stub"><slot /></form>',
}

const NSpaceStub = {
  template: '<div class="n-space-stub"><slot /></div>',
}

const NButtonStub = {
  inheritAttrs: false,
  emits: ['click'],
  template: '<button type="button" v-bind="$attrs" @click="$emit(\'click\')"><slot /></button>',
}

const NInputStub = {
  inheritAttrs: false,
  props: {
    value: {
      type: String,
      default: '',
    },
    placeholder: {
      type: String,
      default: '',
    },
    clearable: Boolean,
  },
  emits: ['update:value'],
  template: `
    <input
      v-bind="$attrs"
      :value="value"
      :placeholder="placeholder"
      @input="$emit('update:value', $event.target.value)"
    />
  `,
}

const NSelectStub = {
  inheritAttrs: false,
  props: {
    value: {
      type: [String, null],
      default: null,
    },
    options: {
      type: Array,
      default: () => [],
    },
    placeholder: {
      type: String,
      default: '',
    },
    clearable: Boolean,
  },
  emits: ['update:value'],
  template: `
    <select
      v-bind="$attrs"
      :value="value ?? ''"
      @change="$emit('update:value', $event.target.value || null)"
    >
      <option value="">{{ placeholder }}</option>
      <option v-for="option in options" :key="option.value" :value="option.value">
        {{ option.label }}
      </option>
    </select>
  `,
}

function createFlow(overrides: Partial<Flow>): Flow {
  return {
    uuid: 'flow-default',
    name: '默认流程',
    description: '默认描述',
    plugin: 'demo-plugin',
    tasks: null,
    status: 'created',
    flow_template: null,
    created_at: '2026-03-19T10:00:00Z',
    ...overrides,
  }
}

const baseFlows: Flow[] = [
  createFlow({
    uuid: 'flow-b',
    name: 'Beta Sorting Flow',
    description: 'sorting coverage',
    status: 'processing',
    created_at: '2026-03-19T11:00:00Z',
    flow_template: 'template-beta',
  }),
  createFlow({
    uuid: 'flow-a',
    name: 'Alpha Search Flow',
    description: 'Needle keyword target',
    status: 'created',
    created_at: '2026-03-19T11:00:00Z',
  }),
  createFlow({
    uuid: 'flow-c',
    name: 'Gamma Final Flow',
    description: null,
    status: 'finished',
    created_at: '2026-03-19T09:00:00Z',
  }),
  createFlow({
    uuid: 'flow-z',
    name: 'Invalid Date Flow',
    description: 'broken date fixture',
    status: 'processing',
    created_at: 'not-a-date',
  }),
]

const processingFlows = baseFlows.filter((flow) => flow.status === 'processing')
const betaFlow = baseFlows.find((flow) => flow.name === 'Beta Sorting Flow')

if (!betaFlow) {
  throw new Error('Expected Beta Sorting Flow fixture to exist')
}

function buildResponse(items: Flow[]): FlowListResponse {
  return {
    items,
    total: items.length,
    offset: 0,
    limit: 20,
  }
}

function deferred<T>() {
  let resolve!: (value: T) => void
  let reject!: (reason?: unknown) => void
  const promise = new Promise<T>((res, rej) => {
    resolve = res
    reject = rej
  })
  return { promise, resolve, reject }
}

async function settleComponent() {
  await flushPromises()
  await flushPromises()
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
        'n-input': NInputStub,
        'n-select': NSelectStub,
        'n-button': NButtonStub,
        'n-space': NSpaceStub,
        'n-form': NFormStub,
        transition: false,
      },
    },
  })
}

function cardNames(wrapper: ReturnType<typeof mountFlowsView>) {
  return wrapper.findAll('[data-testid="flows-card"] .flow-name').map((node) => node.text())
}

describe('FlowsView', () => {
  beforeEach(() => {
    mockGet.mockReset()
  })

  it('renders the toolbar with stable selectors', async () => {
    mockGet.mockResolvedValue({ data: buildResponse(baseFlows) })

    const wrapper = mountFlowsView()
    await settleComponent()

    expect(wrapper.find('[data-testid="flows-toolbar"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="flows-keyword-input"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="flows-status-select"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="flows-sort-select"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="flows-reset-button"]').exists()).toBe(true)
    expect(wrapper.findAll('[data-testid="flows-card"]')).toHaveLength(4)
  })

  it('sends trimmed keyword queries through the mounted input', async () => {
    mockGet
      .mockResolvedValueOnce({ data: buildResponse(baseFlows) })
      .mockResolvedValueOnce({ data: buildResponse([betaFlow]) })

    const wrapper = mountFlowsView()
    await settleComponent()

    await wrapper.find('[data-testid="flows-keyword-input"]').setValue('  Needle  ')
    await settleComponent()

    expect(mockGet).toHaveBeenNthCalledWith(1, '/flows', undefined)
    expect(mockGet).toHaveBeenNthCalledWith(2, '/flows', { params: { name: 'Needle' } })
  })

  it('sends status queries through the mounted select without synthetic all-status options', async () => {
    mockGet
      .mockResolvedValueOnce({ data: buildResponse(baseFlows) })
      .mockResolvedValueOnce({ data: buildResponse(processingFlows) })

    const wrapper = mountFlowsView()
    await settleComponent()

    const statusSelect = wrapper.find('[data-testid="flows-status-select"]')
    const optionValues = statusSelect.findAll('option').map((node) => node.element.getAttribute('value'))
    expect(optionValues).toEqual(['', 'created', 'processing', 'finished'])

    await statusSelect.setValue('processing')
    await settleComponent()

    expect(mockGet).toHaveBeenNthCalledWith(2, '/flows', { params: { status: 'processing' } })
  })

  it('keeps created_at sorting frontend-local with deterministic uuid tie-breaks', async () => {
    mockGet.mockResolvedValue({ data: buildResponse(baseFlows) })

    const wrapper = mountFlowsView()
    await settleComponent()

    expect(cardNames(wrapper)).toEqual([
      'Alpha Search Flow',
      'Beta Sorting Flow',
      'Gamma Final Flow',
      'Invalid Date Flow',
    ])

    await wrapper.find('[data-testid="flows-sort-select"]').setValue('asc')
    await settleComponent()

    expect(cardNames(wrapper)).toEqual([
      'Gamma Final Flow',
      'Alpha Search Flow',
      'Beta Sorting Flow',
      'Invalid Date Flow',
    ])
    expect(mockGet).toHaveBeenCalledTimes(1)
  })

  it('renders a processing indicator only before processing flow titles', async () => {
    mockGet.mockResolvedValue({ data: buildResponse(baseFlows) })

    const wrapper = mountFlowsView()
    await settleComponent()

    const processingBeacons = wrapper.findAll('.flow-title-group .flow-status-beacon')
    expect(processingBeacons).toHaveLength(processingFlows.length)

    const processingCards = wrapper
      .findAll('[data-testid="flows-card"]')
      .filter((node) => node.classes().includes('flow-card--status-processing'))
    expect(processingCards).toHaveLength(processingFlows.length)
    expect(processingCards.every((node) => node.find('.flow-title-group .flow-status-beacon').exists())).toBe(true)

    const nonProcessingCards = wrapper
      .findAll('[data-testid="flows-card"]')
      .filter((node) => !node.classes().includes('flow-card--status-processing'))
    expect(nonProcessingCards.every((node) => node.find('.flow-title-group .flow-status-beacon').exists() === false)).toBe(true)
  })

  it('reset restores keyword, status, sort defaults, and the full list', async () => {
    mockGet
      .mockResolvedValueOnce({ data: buildResponse(baseFlows) })
      .mockResolvedValueOnce({ data: buildResponse(processingFlows) })
      .mockResolvedValueOnce({ data: buildResponse(processingFlows) })
      .mockResolvedValueOnce({ data: buildResponse(baseFlows) })

    const wrapper = mountFlowsView()
    await settleComponent()

    await wrapper.find('[data-testid="flows-keyword-input"]').setValue('  beta  ')
    await settleComponent()
    await wrapper.find('[data-testid="flows-status-select"]').setValue('processing')
    await settleComponent()
    await wrapper.find('[data-testid="flows-sort-select"]').setValue('asc')
    await settleComponent()

    await wrapper.find('[data-testid="flows-reset-button"]').trigger('click')
    await settleComponent()

    const keywordInput = wrapper.find('[data-testid="flows-keyword-input"]').element as HTMLInputElement
    const statusSelect = wrapper.find('[data-testid="flows-status-select"]').element as HTMLSelectElement
    const sortSelect = wrapper.find('[data-testid="flows-sort-select"]').element as HTMLSelectElement

    expect(keywordInput.value).toBe('')
    expect(statusSelect.value).toBe('')
    expect(sortSelect.value).toBe('desc')
    expect(cardNames(wrapper)).toEqual([
      'Alpha Search Flow',
      'Beta Sorting Flow',
      'Gamma Final Flow',
      'Invalid Date Flow',
    ])
    expect(mockGet).toHaveBeenLastCalledWith('/flows', undefined)
  })

  it('shows filtered-empty only for active queries and keeps fetch-empty distinct', async () => {
    mockGet
      .mockResolvedValueOnce({ data: buildResponse(baseFlows) })
      .mockResolvedValueOnce({ data: buildResponse([]) })

    const wrapper = mountFlowsView()
    await settleComponent()

    await wrapper.find('[data-testid="flows-keyword-input"]').setValue('missing')
    await settleComponent()

    expect(wrapper.find('[data-testid="flows-filtered-empty"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="flows-filtered-empty"]').text()).toContain('没有匹配的工作流')
    expect(wrapper.find('[data-testid="flows-fetch-empty"]').exists()).toBe(false)
    expect(wrapper.find('[data-testid="n-result"]').exists()).toBe(false)
  })

  it('shows fetch-empty for an unfiltered empty response', async () => {
    mockGet.mockResolvedValue({ data: buildResponse([]) })

    const wrapper = mountFlowsView()
    await settleComponent()

    expect(wrapper.find('[data-testid="flows-fetch-empty"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="flows-filtered-empty"]').exists()).toBe(false)
  })

  it('shows the error state when the request fails', async () => {
    mockGet.mockRejectedValue(new Error('boom'))

    const wrapper = mountFlowsView()
    await settleComponent()

    expect(wrapper.find('[data-testid="n-result"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('加载失败')
  })

  it('preserves expansion state across local sort changes', async () => {
    mockGet.mockResolvedValue({ data: buildResponse(baseFlows) })

    const wrapper = mountFlowsView()
    await settleComponent()

    const betaCard = wrapper.findAll('[data-testid="flows-card"]').find((node) => node.text().includes('Beta Sorting Flow'))
    expect(betaCard).toBeDefined()

    await betaCard!.trigger('click')
    expect(wrapper.text()).toContain('template-beta')

    await wrapper.find('[data-testid="flows-sort-select"]').setValue('asc')
    await settleComponent()

    expect(wrapper.text()).toContain('template-beta')
  })

  it('ignores stale responses from older keyword/status requests', async () => {
    const initial = deferred<{ data: FlowListResponse }>()
    const oldQuery = deferred<{ data: FlowListResponse }>()
    const newQuery = deferred<{ data: FlowListResponse }>()

    mockGet
      .mockImplementationOnce(() => initial.promise)
      .mockImplementationOnce(() => oldQuery.promise)
      .mockImplementationOnce(() => newQuery.promise)

    const wrapper = mountFlowsView()

    initial.resolve({ data: buildResponse(baseFlows) })
    await settleComponent()

    await wrapper.find('[data-testid="flows-keyword-input"]').setValue('older')
    await flushPromises()
    await wrapper.find('[data-testid="flows-status-select"]').setValue('processing')
    await flushPromises()

    newQuery.resolve({
      data: buildResponse([
        createFlow({
          uuid: 'fresh-flow',
          name: 'Fresh Query Result',
          description: 'latest response wins',
          status: 'processing',
          created_at: '2026-03-20T10:00:00Z',
        }),
      ]),
    })
    await settleComponent()

    oldQuery.resolve({
      data: buildResponse([
        createFlow({
          uuid: 'stale-flow',
          name: 'Stale Query Result',
          description: 'should never replace fresh data',
          status: 'created',
          created_at: '2026-03-18T10:00:00Z',
        }),
      ]),
    })
    await settleComponent()

    expect(cardNames(wrapper)).toEqual(['Fresh Query Result'])
    expect(wrapper.text()).not.toContain('Stale Query Result')
    expect(mockGet).toHaveBeenNthCalledWith(2, '/flows', { params: { name: 'older' } })
    expect(mockGet).toHaveBeenNthCalledWith(3, '/flows', {
      params: { name: 'older', status: 'processing' },
    })
  })
})
