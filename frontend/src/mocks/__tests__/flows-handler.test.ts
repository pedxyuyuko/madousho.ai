import { describe, it, expect, beforeAll, afterAll, afterEach } from 'vitest'
import { setupServer } from 'msw/node'
import { handlers } from '../handlers'
import type { Flow } from '@/types/flow'

const server = setupServer(...handlers)

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }))
afterAll(() => server.close())
afterEach(() => server.resetHandlers())

describe('Flows MSW handler', () => {
  it('intercepts GET */api/v1/flows', async () => {
    const response = await fetch('/api/v1/flows')
    expect(response.ok).toBe(true)
  })

  it('returns FlowListResponse with correct structure', async () => {
    const response = await fetch('/api/v1/flows')
    const data = await response.json()

    expect(data).toHaveProperty('items')
    expect(data).toHaveProperty('total')
    expect(data).toHaveProperty('offset')
    expect(data).toHaveProperty('limit')
    expect(Array.isArray(data.items)).toBe(true)
  })

  it('returns items array with at least 2 flows', async () => {
    const response = await fetch('/api/v1/flows')
    const data = await response.json()

    expect(data.items.length).toBeGreaterThanOrEqual(2)
    expect(data.total).toBe(data.items.length)
  })

  it('each flow item has all required fields', async () => {
    const response = await fetch('/api/v1/flows')
    const data = await response.json()

    const requiredFields: (keyof Flow)[] = [
      'uuid',
      'name',
      'description',
      'plugin',
      'tasks',
      'status',
      'flow_template',
      'created_at',
    ]

    for (const flow of data.items as Flow[]) {
      for (const field of requiredFields) {
        expect(flow).toHaveProperty(field)
      }
      expect(typeof flow.uuid).toBe('string')
      expect(typeof flow.name).toBe('string')
      expect(typeof flow.plugin).toBe('string')
      expect(['created', 'processing', 'finished']).toContain(flow.status)
    }
  })
})
