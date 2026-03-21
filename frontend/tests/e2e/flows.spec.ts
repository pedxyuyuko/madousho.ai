import { test, expect } from '@playwright/test'

const AUTH_STORAGE = {
  madousho_backends: JSON.stringify({
    backends: [
      {
        baseUrl: 'http://localhost:8000',
        token: 'test-token',
        name: 'Local Mock',
      },
    ],
    currentBackendIndex: 0,
  }),
  madousho_theme: JSON.stringify({
    userPreference: 'parchment',
  }),
}

test.describe('Flows page', () => {
  test.beforeEach(async ({ page }) => {
    await page.addInitScript((storage) => {
      for (const [key, value] of Object.entries(storage)) {
        window.localStorage.setItem(key, value)
      }
    }, AUTH_STORAGE)
    await page.route('**/src/mocks/browser.ts*', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/javascript',
        body: 'export const worker = { start: async () => undefined }',
      })
    })
  })

  test('renders flow cards and expands the current card details on click', async ({ page }) => {
    await page.route('**/api/v1/flows', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [
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
          ],
          total: 2,
          offset: 0,
          limit: 20,
        }),
      })
    })

    await page.goto('/flows')
    await expect(page).toHaveURL('/flows')
    await expect(page.locator('.flows-title')).toHaveText('工作流列表')

    const cards = page.locator('.flow-card')
    await expect(cards).toHaveCount(2)

    const firstCard = cards.first()
    await expect(firstCard.locator('.flow-name')).toHaveText('文本分析流程')
    await expect(firstCard).toContainText('text-analyzer')
    await expect(firstCard).toContainText('created')
    await expect(firstCard).not.toContainText('task-001')

    await firstCard.click()

    await expect(firstCard).toContainText('Tasks:')
    await expect(firstCard).toContainText('task-001, task-002')
    await expect(firstCard.locator('.expand-icon')).toHaveClass(/expanded/)
  })

  test('shows fetch-empty state when no flows exist', async ({ page }) => {
    await page.route('**/api/v1/flows', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [], total: 0, offset: 0, limit: 20 }),
      })
    })

    await page.goto('/flows')
    await expect(page).toHaveURL('/flows')

    await expect(page.getByText('暂无工作流')).toBeVisible()
  })

  test('shows error state when the flows request fails', async ({ page }) => {
    await page.route('**/api/v1/flows', (route) => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'internal_error' }),
      })
    })

    await page.goto('/flows')
    await expect(page).toHaveURL('/flows')

    await expect(page.getByText('加载失败')).toBeVisible()
  })

  test('keeps the sidebar menu highlighting on the flows route', async ({ page }) => {
    await page.goto('/flows')
    await expect(page).toHaveURL('/flows')

    const flowsMenuItem = page.locator('.n-menu-item-content--selected')
    await expect(flowsMenuItem).toBeVisible()
    await expect(flowsMenuItem).toContainText('工作流')
  })

  test('keeps the current request contract limited to the bare /flows fetch without unsupported params', async ({ page }) => {
    const requests: string[] = []

    await page.route('**/api/v1/flows**', (route) => {
      requests.push(route.request().url())

      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [
            {
              uuid: 'flow-z',
              name: 'Zeta 流程',
              description: 'latest',
              plugin: 'plugin-z',
              tasks: null,
              status: 'processing',
              flow_template: null,
              created_at: '2026-03-19T12:00:00Z',
            },
            {
              uuid: 'flow-a',
              name: 'Alpha 流程',
              description: 'earliest',
              plugin: 'plugin-a',
              tasks: null,
              status: 'processing',
              flow_template: null,
              created_at: '2026-03-19T09:00:00Z',
            },
          ],
          total: 2,
          offset: 0,
          limit: 20,
        }),
      })
    })

    await page.goto('/flows')

    await expect.poll(() => requests.length).toBe(1)
    await expect.poll(() => requests[0] ?? '').toContain('/api/v1/flows')
    expect(requests.some((url) => url.includes('sort='))).toBeFalsy()
    expect(requests.some((url) => url.includes('sort_by='))).toBeFalsy()
    expect(requests.some((url) => url.includes('order='))).toBeFalsy()
    expect(requests.some((url) => url.includes('direction='))).toBeFalsy()

    const requestUrl = new URL(requests[0]!)
    expect(requestUrl.searchParams.get('name')).toBeNull()
    expect(requestUrl.searchParams.get('status')).toBeNull()
    expect(requestUrl.searchParams.get('sort')).toBeNull()
    expect(requestUrl.searchParams.get('sort_by')).toBeNull()
    expect(requestUrl.searchParams.get('order')).toBeNull()
    expect(requestUrl.searchParams.get('direction')).toBeNull()

    await expect(page.getByText('Zeta 流程')).toBeVisible()
    await expect(page.getByText('Alpha 流程')).toBeVisible()
  })
})
