import { http, HttpResponse } from 'msw'
import type { Flow, FlowListResponse } from '@/types/flow'

const mockFlows: Flow[] = [
  {
    uuid: '550e8400-e29b-41d4-a716-446655440000',
    name: '文本分析流程',
    description: '用于测试的示例流程',
    plugin: 'text-analyzer',
    tasks: ['task-001', 'task-002'],
    status: 'created',
    flow_template: null,
    created_at: '2026-03-19T10:00:00Z',
  },
  {
    uuid: '660e8400-e29b-41d4-a716-446655440001',
    name: '图像处理流程',
    description: null,
    plugin: 'image-processor',
    tasks: [],
    status: 'processing',
    flow_template: 'default-template',
    created_at: '2026-03-19T11:00:00Z',
  },
]

/**
 * MSW request handlers array.
 *
 * Add mock handlers here to intercept API requests during development and testing.
 * Example:
 *   http.get('/api/users', () => {
 *     return HttpResponse.json([{ id: 1, name: 'John' }])
 *   })
 */
export const handlers = [
  http.get('*/api/v1/flows', () => {
    const response: FlowListResponse = {
      items: mockFlows,
      total: mockFlows.length,
      offset: 0,
      limit: 20,
    }
    return HttpResponse.json(response)
  }),

  http.get('*/api/v1/protected', ({ request }) => {
    const authHeader = request.headers.get('Authorization')
    const token = authHeader?.replace('Bearer ', '')?.trim()

    if (token) {
      return HttpResponse.json({ message: 'authenticated' })
    }

    return HttpResponse.json(
      { error: 'invalid_token', message: 'Authentication required' },
      { status: 401 }
    )
  }),
]
