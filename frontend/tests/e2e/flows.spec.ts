import { expect, test, type Page } from '@playwright/test'
import type { Flow } from '../../src/types/flow'

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

const allFlows: Flow[] = [
  createFlow({
    uuid: 'flow-b',
    name: 'Beta Runner',
    description: 'keyword target beta',
    plugin: 'beta-plugin',
    status: 'processing',
    flow_template: 'beta-template',
    created_at: '2026-03-19T11:00:00Z',
  }),
  createFlow({
    uuid: 'flow-a',
    name: 'Alpha Runner',
    description: 'keyword target alpha',
    plugin: 'alpha-plugin',
    status: 'created',
    created_at: '2026-03-19T11:00:00Z',
  }),
  createFlow({
    uuid: 'flow-c',
    name: 'Gamma Completed',
    description: null,
    plugin: 'gamma-plugin',
    status: 'finished',
    created_at: '2026-03-19T09:00:00Z',
  }),
]

function buildResponse(items: Flow[]) {
  return {
    items,
    total: items.length,
    offset: 0,
    limit: 20,
  }
}

async function chooseSelectOption(page: Page, testId: string, optionLabel: string) {
  await page.getByTestId(testId).click()
  await page.locator('body').getByText(optionLabel, { exact: true }).last().click()
}

async function clearSelect(page: Page, testId: string) {
  if (testId === 'flows-status-select') {
    const select = page.getByTestId(testId)
    await select.click()
    await page.keyboard.press('Backspace')
    return
  }

  throw new Error(`No stable clear interaction is defined for ${testId}`)
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
    await page.route('**/api/v1/flows**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(buildResponse(allFlows)),
      })
    })

    await page.goto('/flows')
    await expect(page).toHaveURL('/flows')
    await expect(page.locator('.flows-title')).toHaveText('工作流列表')
    await expect(page.getByTestId('flows-toolbar')).toBeVisible()

    const cards = page.getByTestId('flows-card')
    await expect(cards).toHaveCount(3)
    await expect(cards.nth(0).locator('.flow-name')).toHaveText('Alpha Runner')
    await expect(cards.nth(1).locator('.flow-name')).toHaveText('Beta Runner')

    const betaCard = cards.filter({ hasText: 'Beta Runner' }).first()
    await betaCard.click()
    await expect(betaCard).toContainText('Template:')
    await expect(betaCard).toContainText('beta-template')
    await expect(betaCard.locator('.expand-icon')).toHaveClass(/expanded/)
  })

  test('uses backend name and status params, keeps sort local, resets correctly, and shows filtered-empty', async ({
    page,
  }) => {
    const requests: string[] = []

    await page.route('**/api/v1/flows**', async (route) => {
      const url = new URL(route.request().url())
      requests.push(url.toString())

      const keyword = url.searchParams.get('name')?.toLowerCase().trim() ?? ''
      const status = url.searchParams.get('status')
      const sort = url.searchParams.get('sort')
      const sortBy = url.searchParams.get('sort_by')
      const order = url.searchParams.get('order')
      const direction = url.searchParams.get('direction')

      expect(sort).toBeNull()
      expect(sortBy).toBeNull()
      expect(order).toBeNull()
      expect(direction).toBeNull()

      const items = allFlows.filter((flow) => {
        const matchesKeyword =
          keyword === '' ||
          flow.name.toLowerCase().includes(keyword) ||
          (flow.description ?? '').toLowerCase().includes(keyword)
        const matchesStatus = status === null || flow.status === status
        return matchesKeyword && matchesStatus
      })

      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(buildResponse(items)),
      })
    })

    await page.goto('/flows')

    const keywordInput = page.getByTestId('flows-keyword-input').locator('input')
    const resetButton = page.getByTestId('flows-reset-button')

    await expect(page.getByTestId('flows-card')).toHaveCount(3)
    await expect(page.getByTestId('flows-card').nth(0).locator('.flow-name')).toHaveText('Alpha Runner')

    await keywordInput.fill(' beta ')
    await expect.poll(() => requests.length).toBe(2)
    expect(new URL(requests[1]!).searchParams.get('name')).toBe('beta')
    expect(new URL(requests[1]!).searchParams.get('status')).toBeNull()
    await expect(page.getByTestId('flows-card')).toHaveCount(1)
    await expect(page.getByTestId('flows-card').nth(0).locator('.flow-name')).toHaveText('Beta Runner')

    await chooseSelectOption(page, 'flows-status-select', '处理中')
    await expect.poll(() => requests.length).toBe(3)
    const thirdRequest = new URL(requests[2]!)
    expect(thirdRequest.searchParams.get('name')).toBe('beta')
    expect(thirdRequest.searchParams.get('status')).toBe('processing')

    await keywordInput.fill(' runner ')
    await expect.poll(() => requests.length).toBe(4)
    const fourthRequest = new URL(requests[3]!)
    expect(fourthRequest.searchParams.get('name')).toBe('runner')
    expect(fourthRequest.searchParams.get('status')).toBe('processing')

    await expect(page.getByTestId('flows-card')).toHaveCount(1)
    await expect(page.getByTestId('flows-card').nth(0).locator('.flow-name')).toHaveText('Beta Runner')

    await clearSelect(page, 'flows-status-select')
    await expect.poll(() => requests.length).toBe(5)
    const fifthRequest = new URL(requests[4]!)
    expect(fifthRequest.searchParams.get('name')).toBe('runner')
    expect(fifthRequest.searchParams.get('status')).toBeNull()

    await expect(page.getByTestId('flows-card')).toHaveCount(2)
    await expect(page.getByTestId('flows-card').nth(0).locator('.flow-name')).toHaveText('Alpha Runner')
    await expect(page.getByTestId('flows-card').nth(1).locator('.flow-name')).toHaveText('Beta Runner')

    await keywordInput.fill('')
    await expect.poll(() => requests.length).toBe(6)
    const sixthRequest = new URL(requests[5]!)
    expect(sixthRequest.searchParams.get('name')).toBeNull()
    expect(sixthRequest.searchParams.get('status')).toBeNull()

    await expect(page.getByTestId('flows-card')).toHaveCount(3)
    await expect(page.getByTestId('flows-card').nth(0).locator('.flow-name')).toHaveText('Alpha Runner')
    await expect(page.getByTestId('flows-card').nth(1).locator('.flow-name')).toHaveText('Beta Runner')
    await expect(page.getByTestId('flows-card').nth(2).locator('.flow-name')).toHaveText('Gamma Completed')

    await chooseSelectOption(page, 'flows-sort-select', '最早优先')
    await expect(page.getByTestId('flows-card').nth(0).locator('.flow-name')).toHaveText('Gamma Completed')
    await expect(page.getByTestId('flows-card').nth(1).locator('.flow-name')).toHaveText('Alpha Runner')
    await expect(page.getByTestId('flows-card').nth(2).locator('.flow-name')).toHaveText('Beta Runner')
    await expect.poll(() => requests.length).toBe(6)

    await keywordInput.fill('missing')
    await expect.poll(() => requests.length).toBe(7)
    const seventhRequest = new URL(requests[6]!)
    expect(seventhRequest.searchParams.get('name')).toBe('missing')
    expect(seventhRequest.searchParams.get('status')).toBeNull()
    await expect(page.getByTestId('flows-filtered-empty')).toBeVisible()
    await expect(page.getByTestId('flows-filtered-empty')).toContainText('没有匹配的工作流')
    await expect(page.getByTestId('flows-fetch-empty')).toHaveCount(0)

    await resetButton.click()
    await expect.poll(() => requests.length).toBe(8)
    const eighthRequest = new URL(requests[7]!)
    expect(eighthRequest.searchParams.get('name')).toBeNull()
    expect(eighthRequest.searchParams.get('status')).toBeNull()

    await expect(keywordInput).toHaveValue('')
    await expect(page.getByTestId('flows-status-select')).toContainText('选择状态')
    await expect(page.getByTestId('flows-sort-select')).toContainText('最新优先')
    await expect(page.getByTestId('flows-card')).toHaveCount(3)
    await expect(page.getByTestId('flows-card').nth(0).locator('.flow-name')).toHaveText('Alpha Runner')
    await expect(page.getByTestId('flows-card').nth(1).locator('.flow-name')).toHaveText('Beta Runner')
    await expect(page.getByTestId('flows-card').nth(2).locator('.flow-name')).toHaveText('Gamma Completed')
  })

  test('shows fetch-empty state when the default request returns no flows', async ({ page }) => {
    await page.route('**/api/v1/flows**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(buildResponse([])),
      })
    })

    await page.goto('/flows')
    await expect(page.getByTestId('flows-fetch-empty')).toBeVisible()
    await expect(page.getByTestId('flows-fetch-empty')).toContainText('暂无工作流')
    await expect(page.getByTestId('flows-filtered-empty')).toHaveCount(0)
  })

  test('shows error state when the flows request fails', async ({ page }) => {
    await page.route('**/api/v1/flows**', async (route) => {
      await route.fulfill({
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
    await page.route('**/api/v1/flows**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(buildResponse(allFlows)),
      })
    })

    await page.goto('/flows')
    await expect(page).toHaveURL('/flows')

    const flowsMenuItem = page.locator('.n-menu-item-content--selected')
    await expect(flowsMenuItem).toBeVisible()
    await expect(flowsMenuItem).toContainText('工作流')
  })
})
