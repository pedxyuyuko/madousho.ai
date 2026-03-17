import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import axios from 'axios'
import { useAuthStore } from '../auth.store'

vi.mock('axios')
const mockedAxios = vi.mocked(axios, true)

const localStorageMock = (() => {
  let store: Record<string, string> = {}
  return {
    getItem: vi.fn((key: string) => store[key] ?? null),
    setItem: vi.fn((key: string, value: string) => {
      store[key] = value
    }),
    removeItem: vi.fn((key: string) => {
      delete store[key]
    }),
    clear: vi.fn(() => {
      store = {}
    }),
  }
})()

Object.defineProperty(globalThis, 'localStorage', {
  value: localStorageMock,
  writable: true,
})

describe('auth.store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorageMock.clear()
    vi.clearAllMocks()
  })

  describe('login() with valid credentials', () => {
    it('sets isAuthenticated=true and persists backend', async () => {
      mockedAxios.get.mockResolvedValueOnce({ data: { ok: true } })

      const store = useAuthStore()
      await store.login('https://api.example.com', 'test-token-123')

      expect(store.isAuthenticated).toBe(true)
      expect(store.currentBackendIndex).toBe(0)
      expect(store.backends).toHaveLength(1)
      expect(store.backends[0]).toEqual({
        baseUrl: 'https://api.example.com',
        token: 'test-token-123',
      })
      expect(mockedAxios.get).toHaveBeenCalledWith(
        'https://api.example.com/api/v1/protected',
        { headers: { Authorization: 'Bearer test-token-123' } }
      )
      expect(localStorageMock.setItem).toHaveBeenCalled()
    })

    it('normalizes trailing slashes in baseUrl', async () => {
      mockedAxios.get.mockResolvedValueOnce({ data: { ok: true } })

      const store = useAuthStore()
      await store.login('https://api.example.com///', 'tok')

      expect(store.backends[0]?.baseUrl).toBe('https://api.example.com')
    })

    it('updates existing backend token when baseUrl matches', async () => {
      mockedAxios.get.mockResolvedValueOnce({ data: { ok: true } })

      const store = useAuthStore()
      await store.login('https://api.example.com', 'old-token')

      mockedAxios.get.mockResolvedValueOnce({ data: { ok: true } })
      await store.login('https://api.example.com', 'new-token')

      expect(store.backends).toHaveLength(1)
      expect(store.backends[0]?.token).toBe('new-token')
      expect(store.currentBackendIndex).toBe(0)
    })

    it('sets loading during login call', async () => {
      let resolveLogin: (value: unknown) => void
      mockedAxios.get.mockImplementation(
        () => new Promise((resolve) => { resolveLogin = resolve })
      )

      const store = useAuthStore()
      const loginPromise = store.login('https://api.example.com', 'tok')

      expect(store.loading).toBe(true)

      resolveLogin!({ data: { ok: true } })
      await loginPromise

      expect(store.loading).toBe(false)
    })
  })

  describe('login() with invalid credentials', () => {
    it('throws error and leaves state unchanged', async () => {
      mockedAxios.get.mockRejectedValueOnce(new Error('Unauthorized'))

      const store = useAuthStore()
      await expect(
        store.login('https://api.example.com', 'bad-token')
      ).rejects.toThrow('Unauthorized')

      expect(store.isAuthenticated).toBe(false)
      expect(store.backends).toHaveLength(0)
      expect(store.currentBackendIndex).toBe(-1)
    })

    it('resets loading after failed login', async () => {
      mockedAxios.get.mockRejectedValueOnce(new Error('fail'))

      const store = useAuthStore()
      try {
        await store.login('https://api.example.com', 'bad')
      } catch {}

      expect(store.loading).toBe(false)
    })
  })

  describe('logout()', () => {
    it('clears isAuthenticated and resets currentBackendIndex', async () => {
      mockedAxios.get.mockResolvedValueOnce({ data: {} })
      const store = useAuthStore()
      await store.login('https://api.example.com', 'tok')

      store.logout()

      expect(store.isAuthenticated).toBe(false)
      expect(store.currentBackendIndex).toBe(-1)
    })

    it('keeps saved backends after logout', async () => {
      mockedAxios.get.mockResolvedValueOnce({ data: {} })
      const store = useAuthStore()
      await store.login('https://api.example.com', 'tok')

      store.logout()

      expect(store.backends).toHaveLength(1)
      expect(store.backends[0]?.baseUrl).toBe('https://api.example.com')
    })
  })

  describe('switchBackend(index)', () => {
    it('updates currentBackendIndex and persists', async () => {
      mockedAxios.get.mockResolvedValueOnce({ data: {} })
      const store = useAuthStore()
      await store.login('https://a.example.com', 'tok-a')

      mockedAxios.get.mockResolvedValueOnce({ data: {} })
      await store.login('https://b.example.com', 'tok-b')

      expect(store.currentBackendIndex).toBe(1)

      store.switchBackend(0)

      expect(store.currentBackendIndex).toBe(0)
      expect(store.currentBackend?.baseUrl).toBe('https://a.example.com')
    })

    it('ignores invalid index (negative)', () => {
      const store = useAuthStore()
      store.switchBackend(-1)
      expect(store.currentBackendIndex).toBe(-1)
    })

    it('ignores invalid index (out of bounds)', async () => {
      mockedAxios.get.mockResolvedValueOnce({ data: {} })
      const store = useAuthStore()
      await store.login('https://a.example.com', 'tok')

      store.switchBackend(99)
      expect(store.currentBackendIndex).toBe(0)
    })
  })

  describe('removeBackend(index)', () => {
    it('removes backend and adjusts index when removing before current', async () => {
      mockedAxios.get.mockResolvedValueOnce({ data: {} })
      const store = useAuthStore()
      await store.login('https://a.example.com', 'tok-a')

      mockedAxios.get.mockResolvedValueOnce({ data: {} })
      await store.login('https://b.example.com', 'tok-b')

      mockedAxios.get.mockResolvedValueOnce({ data: {} })
      await store.login('https://c.example.com', 'tok-c')

      store.switchBackend(2)
      expect(store.currentBackendIndex).toBe(2)

      store.removeBackend(0)

      expect(store.backends).toHaveLength(2)
      expect(store.currentBackendIndex).toBe(1)
      expect(store.currentBackend?.baseUrl).toBe('https://c.example.com')
    })

    it('clears auth when removing current backend', async () => {
      mockedAxios.get.mockResolvedValueOnce({ data: {} })
      const store = useAuthStore()
      await store.login('https://a.example.com', 'tok-a')

      mockedAxios.get.mockResolvedValueOnce({ data: {} })
      await store.login('https://b.example.com', 'tok-b')

      store.switchBackend(0)
      store.removeBackend(0)

      expect(store.isAuthenticated).toBe(false)
      expect(store.currentBackendIndex).toBe(0)
    })

    it('sets index to -1 when removing last backend', async () => {
      mockedAxios.get.mockResolvedValueOnce({ data: {} })
      const store = useAuthStore()
      await store.login('https://a.example.com', 'tok')

      store.removeBackend(0)

      expect(store.backends).toHaveLength(0)
      expect(store.currentBackendIndex).toBe(-1)
      expect(store.isAuthenticated).toBe(false)
    })

    it('ignores invalid index', async () => {
      mockedAxios.get.mockResolvedValueOnce({ data: {} })
      const store = useAuthStore()
      await store.login('https://a.example.com', 'tok')

      store.removeBackend(99)
      expect(store.backends).toHaveLength(1)
    })
  })

  describe('loadFromStorage()', () => {
    it('hydrates state from localStorage', () => {
      const saved = {
        backends: [
          { baseUrl: 'https://saved.example.com', token: 'saved-token' },
        ],
        currentBackendIndex: 0,
      }
      localStorageMock.getItem.mockReturnValueOnce(JSON.stringify(saved))

      const store = useAuthStore()

      expect(store.backends).toHaveLength(1)
      expect(store.backends[0]?.baseUrl).toBe('https://saved.example.com')
      expect(store.currentBackendIndex).toBe(0)
      expect(store.isAuthenticated).toBe(true)
    })

    it('sets isAuthenticated=false when currentBackendIndex is -1', () => {
      const saved = {
        backends: [{ baseUrl: 'https://x.com', token: 't' }],
        currentBackendIndex: -1,
      }
      localStorageMock.getItem.mockReturnValueOnce(JSON.stringify(saved))

      const store = useAuthStore()

      expect(store.isAuthenticated).toBe(false)
    })

    it('handles missing/corrupt localStorage gracefully', () => {
      localStorageMock.getItem.mockReturnValueOnce('not-json{{{')

      const store = useAuthStore()

      expect(store.backends).toHaveLength(0)
      expect(store.currentBackendIndex).toBe(-1)
      expect(store.isAuthenticated).toBe(false)
    })

    it('handles empty localStorage', () => {
      localStorageMock.getItem.mockReturnValueOnce(null)

      const store = useAuthStore()

      expect(store.backends).toHaveLength(0)
      expect(store.isAuthenticated).toBe(false)
    })
  })

  describe('persist()', () => {
    it('saves correct JSON to localStorage key "madousho_backends"', async () => {
      mockedAxios.get.mockResolvedValueOnce({ data: {} })
      const store = useAuthStore()
      await store.login('https://persist.example.com', 'persist-token')

      store.persist()

      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'madousho_backends',
        JSON.stringify({
          backends: store.backends,
          currentBackendIndex: store.currentBackendIndex,
        })
      )
    })

    it('includes backends array and currentBackendIndex', () => {
      const store = useAuthStore()
      store.persist()

      const calls = localStorageMock.setItem.mock.calls
      const lastCall = calls[calls.length - 1]
      expect(lastCall).toBeDefined()
      const parsed = JSON.parse(lastCall![1])
      expect(parsed).toHaveProperty('backends')
      expect(parsed).toHaveProperty('currentBackendIndex')
      expect(Array.isArray(parsed.backends)).toBe(true)
    })
  })

  describe('currentBackend getter', () => {
    it('returns null when no backend selected', () => {
      const store = useAuthStore()
      expect(store.currentBackend).toBeNull()
    })

    it('returns correct backend by index', async () => {
      mockedAxios.get.mockResolvedValueOnce({ data: {} })
      const store = useAuthStore()
      await store.login('https://getter.example.com', 'tok')

      expect(store.currentBackend).toEqual({
        baseUrl: 'https://getter.example.com',
        token: 'tok',
      })
    })

    it('returns null for out-of-bounds index', async () => {
      mockedAxios.get.mockResolvedValueOnce({ data: {} })
      const store = useAuthStore()
      await store.login('https://x.com', 'tok')

      store.currentBackendIndex = 99
      expect(store.currentBackend).toBeNull()
    })

    it('currentBaseUrl returns baseUrl or null', async () => {
      const store = useAuthStore()
      expect(store.currentBaseUrl).toBeNull()

      mockedAxios.get.mockResolvedValueOnce({ data: {} })
      await store.login('https://url.example.com', 'tok')
      expect(store.currentBaseUrl).toBe('https://url.example.com')
    })

    it('currentToken returns token or null', async () => {
      const store = useAuthStore()
      expect(store.currentToken).toBeNull()

      mockedAxios.get.mockResolvedValueOnce({ data: {} })
      await store.login('https://tok.example.com', 'secret')
      expect(store.currentToken).toBe('secret')
    })
  })

  describe('multiple backends', () => {
    it('can add and switch between multiple backends', async () => {
      const store = useAuthStore()

      mockedAxios.get.mockResolvedValueOnce({ data: {} })
      await store.login('https://alpha.com', 'alpha-tok')

      mockedAxios.get.mockResolvedValueOnce({ data: {} })
      await store.login('https://beta.com', 'beta-tok')

      mockedAxios.get.mockResolvedValueOnce({ data: {} })
      await store.login('https://gamma.com', 'gamma-tok')

      expect(store.backends).toHaveLength(3)
      expect(store.currentBackendIndex).toBe(2)

      store.switchBackend(0)
      expect(store.currentBackend?.baseUrl).toBe('https://alpha.com')
      expect(store.currentToken).toBe('alpha-tok')

      store.switchBackend(1)
      expect(store.currentBackend?.baseUrl).toBe('https://beta.com')
      expect(store.currentToken).toBe('beta-tok')
    })

    it('backendOptions returns correct labels', async () => {
      mockedAxios.get.mockResolvedValueOnce({ data: {} })
      const store = useAuthStore()
      await store.login('https://a.com', 'tok')

      mockedAxios.get.mockResolvedValueOnce({ data: {} })
      await store.login('https://b.com', 'tok')

      const options = store.backendOptions
      expect(options).toHaveLength(2)
      expect(options[0]).toEqual({ label: 'https://a.com', value: 0 })
      expect(options[1]).toEqual({ label: 'https://b.com', value: 1 })
    })

    it('backendOptions uses name if provided', async () => {
      mockedAxios.get.mockResolvedValueOnce({ data: {} })
      const store = useAuthStore()
      await store.login('https://named.com', 'tok')

      store.backends[0]!.name = 'Production'
      const options = store.backendOptions
      expect(options[0]!.label).toBe('Production')
    })
  })
})
