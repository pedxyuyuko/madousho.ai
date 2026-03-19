import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'

export interface Backend {
  baseUrl: string
  token: string
  name?: string
}

const STORAGE_KEY = 'madousho_backends'

export const useAuthStore = defineStore('auth', () => {
  const backends = ref<Backend[]>([])
  const currentBackendIndex = ref(-1)
  const isAuthenticated = ref(false)
  const loading = ref(false)
  const currentBackend = computed<Backend | null>(() => {
    const idx = currentBackendIndex.value
    return idx >= 0 && idx < backends.value.length
      ? backends.value[idx] ?? null
      : null
  })

  const currentBaseUrl = computed(() => currentBackend.value?.baseUrl ?? null)

  const currentToken = computed(() => currentBackend.value?.token ?? null)

  const backendOptions = computed(() =>
    backends.value.map((backend, index) => ({
      label: backend.name || backend.baseUrl,
      value: index,
    }))
  )

  async function login(baseUrl: string, token: string) {
    loading.value = true
    try {
      const normalizedUrl = baseUrl.replace(/\/+$/, '')
      await axios.get(`${normalizedUrl}/api/v1/protected`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      const existingIndex = backends.value.findIndex(
        (b) => b.baseUrl === normalizedUrl
      )
      if (existingIndex >= 0) {
        const existing = backends.value[existingIndex]
        if (existing) {
          existing.token = token
        }
        currentBackendIndex.value = existingIndex
      } else {
        backends.value.push({ baseUrl: normalizedUrl, token })
        currentBackendIndex.value = backends.value.length - 1
      }

      isAuthenticated.value = true
      persist()
    } finally {
      loading.value = false
    }
  }

  function logout() {
    const idx = currentBackendIndex.value
    if (idx >= 0 && idx < backends.value.length) {
      backends.value.splice(idx, 1)
      if (backends.value.length > 0) {
        currentBackendIndex.value = 0
      } else {
        currentBackendIndex.value = -1
        isAuthenticated.value = false
      }
      persist()
    }
  }

  function switchBackend(index: number) {
    if (index >= 0 && index < backends.value.length) {
      currentBackendIndex.value = index
      persist()
    }
  }

  function removeBackend(index: number) {
    if (index >= 0 && index < backends.value.length) {
      backends.value.splice(index, 1)
      if (currentBackendIndex.value === index) {
        currentBackendIndex.value = backends.value.length > 0 ? 0 : -1
        isAuthenticated.value = backends.value.length > 0
      } else if (currentBackendIndex.value > index) {
        currentBackendIndex.value--
      }
      persist()
    }
  }

  function loadFromStorage() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY)
      if (raw) {
        const data = JSON.parse(raw)
        backends.value = data.backends ?? []
        currentBackendIndex.value = data.currentBackendIndex ?? -1
        isAuthenticated.value = currentBackendIndex.value >= 0
      }
    } catch {}
  }

  function persist() {
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        backends: backends.value,
        currentBackendIndex: currentBackendIndex.value,
      })
    )
  }

  loadFromStorage()

  return {
    backends,
    currentBackendIndex,
    isAuthenticated,
    loading,
    currentBackend,
    currentBaseUrl,
    currentToken,
    backendOptions,
    login,
    logout,
    switchBackend,
    removeBackend,
    loadFromStorage,
    persist,
  }
})
