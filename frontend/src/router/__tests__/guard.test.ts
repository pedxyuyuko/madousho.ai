import { describe, it, expect, vi, beforeEach } from 'vitest'
import { createRouter, createMemoryHistory } from 'vue-router'

const mockAuthStore = vi.hoisted(() => ({
  isAuthenticated: false,
}))

vi.mock('@/stores/auth.store', () => ({
  useAuthStore: () => mockAuthStore,
}))

const localStorageMock = (() => {
  const store: Record<string, string> = {}
  return {
    getItem: vi.fn((key: string) => store[key] ?? null),
    setItem: vi.fn((key: string, value: string) => {
      store[key] = value
    }),
    removeItem: vi.fn((key: string) => {
      delete store[key]
    }),
    clear: vi.fn(() => {
      for (const key of Object.keys(store)) delete store[key]
    }),
  }
})()

Object.defineProperty(globalThis, 'localStorage', {
  value: localStorageMock,
  writable: true,
})

const routes = [
  { path: '/login', name: 'login', component: { template: '<div>Login</div>' } },
  { path: '/', name: 'home', component: { template: '<div>Home</div>' } },
]

const router = createRouter({
  history: createMemoryHistory(),
  routes,
})

router.beforeEach(async (to) => {
  const { useAuthStore } = await import('@/stores/auth.store')
  const authStore = useAuthStore()

  if (to.path === '/login' && authStore.isAuthenticated) {
    return { path: '/' }
  }

  if (to.path !== '/login' && !authStore.isAuthenticated) {
    return { path: '/login' }
  }

  return true
})

describe('router beforeEach auth guard', () => {
  beforeEach(() => {
    localStorageMock.clear()
    vi.clearAllMocks()
    mockAuthStore.isAuthenticated = false
  })

  it('unauthenticated user accessing / redirects to /login', async () => {
    mockAuthStore.isAuthenticated = false

    await router.push('/')

    expect(router.currentRoute.value.path).toBe('/login')
  })

  it('authenticated user accessing / allows navigation', async () => {
    mockAuthStore.isAuthenticated = true

    await router.push('/')

    expect(router.currentRoute.value.path).toBe('/')
  })

  it('authenticated user accessing /login redirects to /', async () => {
    mockAuthStore.isAuthenticated = true

    await router.push('/login')

    expect(router.currentRoute.value.path).toBe('/')
  })

  it('unauthenticated user accessing /login allows navigation', async () => {
    mockAuthStore.isAuthenticated = false

    await router.push('/login')

    expect(router.currentRoute.value.path).toBe('/login')
  })
})
