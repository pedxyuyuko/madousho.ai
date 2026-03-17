import axios from 'axios'
import type { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse, AxiosError } from 'axios'

// Lazy import avoids circular dependency with Pinia auth store
async function getAuthStore() {
  const { useAuthStore } = await import('@/stores/auth.store')
  return useAuthStore()
}

const apiClient: AxiosInstance = axios.create({
  baseURL: '',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

apiClient.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    const authStore = await getAuthStore()

    const baseUrl = authStore.currentBaseUrl ?? ''
    if (baseUrl && config.url) {
      config.url = `${baseUrl}/api/v1${config.url}`
    } else if (config.url && !config.url.startsWith('http')) {
      config.url = `/api/v1${config.url}`
    }

    const token = authStore.currentToken
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)

apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  async (error: AxiosError) => {
    if (error.response?.status === 401) {
      const authStore = await getAuthStore()
      authStore.logout()
      window.location.href = '/login'
    } else if (error.response?.status === 403) {
      console.error('Forbidden access')
    } else if (error.response?.status === 500) {
      console.error('Internal server error')
    }

    return Promise.reject(error)
  }
)

export default apiClient
