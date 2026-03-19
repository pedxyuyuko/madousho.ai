import './assets/main.css'
import './assets/scss/main.scss'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import naive from 'naive-ui'

import App from './App.vue'
import router from './router'
import { useThemeStore } from '@/stores/theme.store'
import { i18n } from './i18n'

async function bootstrap() {
  const useMocks = import.meta.env.VITE_USE_MOCKS !== 'false'
  
  if (import.meta.env.DEV && useMocks) {
    const { worker } = await import('./mocks/browser')
    await worker.start({ onUnhandledRequest: 'bypass' })
  }

  const app = createApp(App)

  app.use(createPinia())
  
  const themeStore = useThemeStore()
  themeStore.loadFromStorage()
  themeStore.initSystemListener()
  
  app.use(i18n)
  app.use(router)
  app.use(naive)

  app.mount('#app')
}

bootstrap()
