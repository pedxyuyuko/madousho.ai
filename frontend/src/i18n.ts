import { createI18n } from 'vue-i18n'

import common from './locales/zh-CN/common.json'
import login from './locales/zh-CN/login.json'
import home from './locales/zh-CN/home.json'
import backend from './locales/zh-CN/backend.json'
import theme from './locales/zh-CN/theme.json'

const messages = {
  'zh-CN': {
    common,
    login,
    home,
    backend,
    theme,
  },
}

export const i18n = createI18n({
  legacy: false,
  locale: 'zh-CN',
  fallbackLocale: 'zh-CN',
  messages,
  missingWarn: false,
  fallbackWarn: false,
})