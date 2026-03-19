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
  })

  test('happy path: renders flow cards with expandable details', async ({ page }) => {
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

    await firstCard.locator('.n-collapse-item__header').click()

    const uuidSpan = firstCard.locator('.detail-value.uuid')
    await expect(uuidSpan).toBeVisible()
    await expect(uuidSpan).toHaveText('550e8400-e29b-41d4-a716-446655440000')
  })

  test('empty state: shows NEmpty when no flows exist', async ({ page }) => {
    await page.route('**/api/v1/flows', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [], total: 0, offset: 0, limit: 20 }),
      })
    })

    await page.goto('/flows')
    await expect(page).toHaveURL('/flows')

    await expect(page.locator('.n-empty')).toBeVisible()
    await expect(page.locator('.n-empty__description')).toHaveText('暂无工作流')
  })

  test('error state: shows error result when API fails', async ({ page }) => {
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

  test('menu highlighting: sidebar shows flows as active', async ({ page }) => {
    await page.goto('/flows')
    await expect(page).toHaveURL('/flows')

    const flowsMenuItem = page.locator('.n-menu-item-content--selected')
    await expect(flowsMenuItem).toBeVisible()
    await expect(flowsMenuItem).toContainText('工作流')
  })
})
