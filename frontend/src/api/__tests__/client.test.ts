import { describe, it, expect, vi, beforeEach } from 'vitest'
import type { AxiosError, InternalAxiosRequestConfig } from 'axios'

const mockAuthStore = {
  currentBaseUrl: null as string | null,
  currentToken: null as string | null,
  logout: vi.fn(),
}

vi.mock('@/stores/auth.store', () => ({
  useAuthStore: () => mockAuthStore,
}))

let requestOnFulfilled: (config: InternalAxiosRequestConfig) => Promise<InternalAxiosRequestConfig>
let responseOnRejected: (error: AxiosError) => Promise<never>

vi.mock('axios', async () => {
  const actual = await vi.importActual<typeof import('axios')>('axios')
  const instance = actual.default.create({})

  // Wrap interceptors.use to capture handlers
  const origReqUse = instance.interceptors.request.use.bind(instance.interceptors.request)
  type ReqFulfilled = (config: InternalAxiosRequestConfig) => InternalAxiosRequestConfig | Promise<InternalAxiosRequestConfig>
  type ReqRejected = (error: unknown) => unknown
  type ResFulfilled = (value: unknown) => unknown
  type ResRejected = (error: unknown) => unknown

  instance.interceptors.request.use = ((onFulfilled: ReqFulfilled | null, onRejected: ReqRejected | null) => {
    if (onFulfilled) requestOnFulfilled = onFulfilled as (config: InternalAxiosRequestConfig) => Promise<InternalAxiosRequestConfig>
    return origReqUse(onFulfilled, onRejected)
  }) as typeof instance.interceptors.request.use

  const origResUse = instance.interceptors.response.use.bind(instance.interceptors.response)
  instance.interceptors.response.use = ((onFulfilled: ResFulfilled | null, onRejected: ResRejected | null) => {
    if (onRejected) responseOnRejected = onRejected as (error: AxiosError) => Promise<never>
    return origResUse(onFulfilled, onRejected)
  }) as typeof instance.interceptors.response.use

  return {
    ...actual,
    default: {
      ...actual.default,
      create: () => instance,
    },
  }
})

// Import triggers interceptor registration (captured above)
await import('../client')

function makeConfig(url: string, headers?: Record<string, string>): InternalAxiosRequestConfig {
  return {
    url,
    headers: { ...headers } as InternalAxiosRequestConfig['headers'],
    method: 'get',
  } as InternalAxiosRequestConfig
}

function makeError(status: number): AxiosError {
  return {
    response: { status } as AxiosError['response'],
  } as AxiosError
}

describe('apiClient', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockAuthStore.currentBaseUrl = null
    mockAuthStore.currentToken = null
  })

  describe('request interceptor', () => {
    it('uses auth store baseURL for URL construction', async () => {
      mockAuthStore.currentBaseUrl = 'https://api.example.com'
      mockAuthStore.currentToken = null

      const result = await requestOnFulfilled(makeConfig('/flows'))

      expect(result.url).toBe('https://api.example.com/api/v1/flows')
    })

    it('adds Bearer token from auth store', async () => {
      mockAuthStore.currentBaseUrl = null
      mockAuthStore.currentToken = 'my-secret-token'

      const result = await requestOnFulfilled(makeConfig('/flows'))

      expect(result.headers.Authorization).toBe('Bearer my-secret-token')
    })

    it('falls back to /api/v1 prefix when no store baseUrl', async () => {
      mockAuthStore.currentBaseUrl = null
      mockAuthStore.currentToken = null

      const result = await requestOnFulfilled(makeConfig('/tasks'))

      expect(result.url).toBe('/api/v1/tasks')
    })

    it('does not add Authorization header when no token', async () => {
      mockAuthStore.currentBaseUrl = 'https://api.example.com'
      mockAuthStore.currentToken = null

      const result = await requestOnFulfilled(makeConfig('/flows'))

      expect(result.headers.Authorization).toBeUndefined()
    })
  })

  describe('response interceptor', () => {
    it('401 response triggers auth store logout', async () => {
      await expect(responseOnRejected(makeError(401))).rejects.toBeDefined()

      expect(mockAuthStore.logout).toHaveBeenCalledTimes(1)
    })

    it('403 response does NOT trigger logout (still rejects)', async () => {
      await expect(responseOnRejected(makeError(403))).rejects.toBeDefined()

      expect(mockAuthStore.logout).not.toHaveBeenCalled()
    })
  })
})
