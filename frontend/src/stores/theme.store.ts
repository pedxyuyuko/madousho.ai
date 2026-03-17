import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { darkTheme } from 'naive-ui'

const STORAGE_KEY = 'madousho_theme'

export const useThemeStore = defineStore('theme', () => {
  const userPreference = ref<'starry-night' | 'parchment' | null>(null)
  const systemPreference = ref<'starry-night' | 'parchment'>('starry-night')
  const isTransitioning = ref(false)

  const resolvedTheme = computed(() => 
    userPreference.value ?? systemPreference.value
  )

  const isDark = computed(() => 
    resolvedTheme.value === 'starry-night'
  )

  const naiveTheme = computed(() => 
    isDark.value ? darkTheme : null
  )

  function setTheme(name: 'starry-night' | 'parchment') {
    // Apply theme immediately (synchronous)
    userPreference.value = name
    persistToStorage()
    document.documentElement.setAttribute('data-theme', name)

    // Trigger overlay transition (visual only, async)
    isTransitioning.value = true
    setTimeout(() => {
      isTransitioning.value = false
    }, 100)
  }

  function resetToSystem() {
    userPreference.value = null
    persistToStorage()
    document.documentElement.setAttribute('data-theme', systemPreference.value)
  }

  function toggle() {
    if (resolvedTheme.value === 'starry-night') {
      setTheme('parchment')
    } else {
      setTheme('starry-night')
    }
  }

  function loadFromStorage() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY)
      if (raw) {
        const data = JSON.parse(raw)
        if (typeof data.userPreference === 'string' || data.userPreference === null) {
          userPreference.value = data.userPreference
        }
      }
    } catch (error) {
      console.error('Failed to load theme from storage:', error)
    }
    
    document.documentElement.setAttribute('data-theme', resolvedTheme.value)
  }

  function persistToStorage() {
    try {
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({
          userPreference: userPreference.value
        })
      )
    } catch (error) {
      console.error('Failed to persist theme to storage:', error)
    }
  }

  function initSystemListener() {
    const darkModeMediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    systemPreference.value = darkModeMediaQuery.matches ? 'starry-night' : 'parchment'
    
    if (userPreference.value === null) {
      document.documentElement.setAttribute('data-theme', systemPreference.value)
    }
    
    darkModeMediaQuery.addEventListener('change', (event) => {
      if (userPreference.value === null) {
        systemPreference.value = event.matches ? 'starry-night' : 'parchment'
        document.documentElement.setAttribute('data-theme', systemPreference.value)
      }
    })
  }

  return {
    userPreference,
    systemPreference,
    resolvedTheme,
    isDark,
    naiveTheme,
    isTransitioning,
    setTheme,
    resetToSystem,
    toggle,
    loadFromStorage,
    initSystemListener
  }
})