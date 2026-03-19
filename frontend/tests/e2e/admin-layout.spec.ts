import { test, expect } from '@playwright/test'

async function seedAuthenticatedSession(page: import('@playwright/test').Page) {
  await page.addInitScript(() => {
    window.localStorage.setItem(
      'madousho_backends',
      JSON.stringify({
        backends: [
          {
            baseUrl: 'http://localhost:8000',
            token: 'test-token',
            name: 'Local Mock',
          },
        ],
        currentBackendIndex: 0,
      }),
    )

    window.localStorage.setItem(
      'madousho_theme',
      JSON.stringify({
        userPreference: 'parchment',
      }),
    )
  })
}

test.describe('Admin layout integration', () => {
  test.beforeEach(async ({ page }) => {
    await seedAuthenticatedSession(page)
    await page.goto('/')
    await expect(page).toHaveURL('/')
    await expect(page.getByTestId('admin-layout')).toBeVisible()
  })

  test('renders header actions in order and shows expected menu items', async ({ page }) => {
    await expect(page.locator('.brand-title')).toHaveText('魔导书')

    const headerChildren = page.locator('[data-testid="admin-header"] .header-actions > *')
    await expect(headerChildren).toHaveCount(4)
    await expect(headerChildren.nth(0)).toContainText('☀️')
    await expect(headerChildren.nth(1)).toContainText('中文')
    await expect(headerChildren.nth(2)).toContainText('Local Mock')
    await expect(headerChildren.nth(3)).toHaveText('退出登录')

    await expect(page.locator('.sidebar-menu')).toContainText('仪表盘')
    await expect(page.locator('.sidebar-menu')).toContainText('工作流')
  })

  test('supports full sidebar expand and collapse flow', async ({ page }) => {
    const toggle = page.getByTestId('sidebar-toggle')
    const brandTitle = page.locator('.brand-title')

    await expect(brandTitle).toBeVisible()

    await toggle.click()
    await expect(brandTitle).toHaveCount(0)

    await toggle.click()
    await expect(brandTitle).toBeVisible()
  })

  test('switches theme while layout stays visible', async ({ page }) => {
    await expect(page.locator('html')).toHaveAttribute('data-theme', 'parchment')

    const themeButton = page.getByRole('button', { name: '切换到深色主题' }).first()
    await expect(themeButton).toContainText('☀️')

    await themeButton.click()

    await expect(page.locator('html')).toHaveAttribute('data-theme', 'starry-night')
    await expect(page.getByTestId('admin-layout')).toBeVisible()
    await expect(page.getByRole('button', { name: '切换到浅色主题' }).first()).toContainText('🌙')
    await expect(page.evaluate(() => window.localStorage.getItem('madousho_theme'))).resolves.toContain('starry-night')
  })

  test('opens language dropdown and switches between 中文 and English labels', async ({ page }) => {
    const languageSwitcher = page.getByTestId('language-switcher')

    await expect(languageSwitcher).toContainText('中文')
    await languageSwitcher.click()

    const dropdown = page.locator('.n-dropdown-option-body').filter({ hasText: 'English' })
    await expect(page.getByText('✓ 中文')).toBeVisible()
    await expect(dropdown).toBeVisible()

    await dropdown.click()
    await expect(languageSwitcher).toContainText('English')

    await languageSwitcher.click()
    const chineseOption = page.locator('.n-dropdown-option-body').filter({ hasText: '中文' })
    await expect(page.getByText('✓ English')).toBeVisible()
    await chineseOption.click()
    await expect(languageSwitcher).toContainText('中文')
  })

  test('logs out and redirects to /login', async ({ page }) => {
    await page.getByTestId('logout-btn').click()

    await expect(page).toHaveURL(/\/login$/)
    await expect(page.evaluate(() => window.localStorage.getItem('madousho_backends'))).resolves.not.toBeNull()
  })
})
