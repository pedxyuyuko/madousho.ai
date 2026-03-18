import { describe, it, expect } from 'vitest'
import { createI18n } from 'vue-i18n'

import common from '@/locales/zh-CN/common.json'
import login from '@/locales/zh-CN/login.json'
import home from '@/locales/zh-CN/home.json'
import backend from '@/locales/zh-CN/backend.json'
import theme from '@/locales/zh-CN/theme.json'

const i18n = createI18n({
  legacy: false,
  locale: 'zh-CN',
  fallbackLocale: 'zh-CN',
  messages: { 'zh-CN': { common, login, home, backend, theme } },
})

const { t } = i18n.global

describe('i18n', () => {
  it('translates login.title to 连接', () => {
    expect(t('login.title')).toBe('连接')
  })

  it('translates backend.noBackend to 未连接后端', () => {
    expect(t('backend.noBackend')).toBe('未连接后端')
  })

  it('translates theme.switchToLight to 切换到浅色主题', () => {
    expect(t('theme.switchToLight')).toBe('切换到浅色主题')
  })

  it('returns key name for missing keys (fallback)', () => {
    expect(t('nonexistent.key')).toBe('nonexistent.key')
  })
})
