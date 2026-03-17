import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useThemeStore } from '../theme.store'

// ── localStorage mock ────────────────────────────────────────────────────────
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

// ── document.documentElement mock ────────────────────────────────────────────
const setAttributeMock = vi.fn()
Object.defineProperty(document, 'documentElement', {
  value: {
    setAttribute: setAttributeMock,
  },
  writable: true,
})

// ── window.matchMedia mock ───────────────────────────────────────────────────
interface MatchMediaMock {
  matches: boolean
  media: string
  onchange: null
  addListener: ReturnType<typeof vi.fn>
  removeListener: ReturnType<typeof vi.fn>
  addEventListener: ReturnType<typeof vi.fn>
  removeEventListener: ReturnType<typeof vi.fn>
  dispatchEvent: ReturnType<typeof vi.fn>
  __triggerChange: (newMatches: boolean) => void
}

function createMatchMediaMock(matches: boolean): MatchMediaMock {
  const listeners: Array<(e: MediaQueryListEvent) => void> = []
  return {
    matches,
    media: '(prefers-color-scheme: dark)',
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn((_event: string, cb: (e: MediaQueryListEvent) => void) => {
      listeners.push(cb)
    }),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(() => true),
    // helper to simulate system preference change
    __triggerChange(newMatches: boolean) {
      listeners.forEach((cb) => cb({ matches: newMatches } as MediaQueryListEvent))
    },
  }
}

let matchMediaMock = createMatchMediaMock(true) // default: dark mode
Object.defineProperty(window, 'matchMedia', {
  value: vi.fn(() => matchMediaMock) as unknown as Window['matchMedia'],
  writable: true,
})

// ── darkTheme mock (naive-ui) ────────────────────────────────────────────────
vi.mock('naive-ui', () => ({
  darkTheme: { name: 'dark' },
}))

// ── Tests ────────────────────────────────────────────────────────────────────
describe('theme.store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorageMock.clear()
    setAttributeMock.mockClear()
    vi.clearAllMocks()
    // reset matchMedia to dark by default
    matchMediaMock = createMatchMediaMock(true)
    window.matchMedia = vi.fn(() => matchMediaMock) as unknown as Window['matchMedia']
  })

  // ── Initialization from localStorage ───────────────────────────────────────
  describe('loadFromStorage()', () => {
    it('loads userPreference from localStorage when valid', () => {
      localStorageMock.getItem.mockReturnValueOnce(
        JSON.stringify({ userPreference: 'parchment' })
      )

      const store = useThemeStore()
      store.loadFromStorage()

      expect(store.userPreference).toBe('parchment')
      expect(store.resolvedTheme).toBe('parchment')
      expect(store.isDark).toBe(false)
      expect(setAttributeMock).toHaveBeenCalledWith('data-theme', 'parchment')
    })

    it('loads null userPreference from localStorage', () => {
      localStorageMock.getItem.mockReturnValueOnce(
        JSON.stringify({ userPreference: null })
      )

      const store = useThemeStore()
      store.loadFromStorage()

      expect(store.userPreference).toBeNull()
      // falls back to systemPreference (default: starry-night)
      expect(store.resolvedTheme).toBe('starry-night')
    })

    it('handles empty localStorage gracefully', () => {
      localStorageMock.getItem.mockReturnValueOnce(null)

      const store = useThemeStore()
      store.loadFromStorage()

      expect(store.userPreference).toBeNull()
      expect(store.resolvedTheme).toBe('starry-night')
      expect(setAttributeMock).toHaveBeenCalledWith('data-theme', 'starry-night')
    })

    it('handles corrupt JSON in localStorage gracefully', () => {
      localStorageMock.getItem.mockReturnValueOnce('not-json{{{')

      const store = useThemeStore()
      store.loadFromStorage()

      expect(store.userPreference).toBeNull()
      expect(store.resolvedTheme).toBe('starry-night')
    })

    it('ignores invalid userPreference type in localStorage', () => {
      localStorageMock.getItem.mockReturnValueOnce(
        JSON.stringify({ userPreference: 42 })
      )

      const store = useThemeStore()
      store.loadFromStorage()

      // number is not a valid string | null, should be ignored
      expect(store.userPreference).toBeNull()
    })
  })

  // ── Theme toggling ─────────────────────────────────────────────────────────
  describe('toggle()', () => {
    it('switches from starry-night to parchment', () => {
      const store = useThemeStore()
      // default: resolvedTheme = systemPreference = starry-night
      expect(store.resolvedTheme).toBe('starry-night')

      store.toggle()

      expect(store.userPreference).toBe('parchment')
      expect(store.resolvedTheme).toBe('parchment')
      expect(store.isDark).toBe(false)
    })

    it('switches from parchment back to starry-night', () => {
      const store = useThemeStore()
      store.setTheme('parchment')

      store.toggle()

      expect(store.userPreference).toBe('starry-night')
      expect(store.resolvedTheme).toBe('starry-night')
      expect(store.isDark).toBe(true)
    })

    it('alternates correctly over multiple toggles', () => {
      const store = useThemeStore()

      store.toggle() // → parchment
      expect(store.resolvedTheme).toBe('parchment')

      store.toggle() // → starry-night
      expect(store.resolvedTheme).toBe('starry-night')

      store.toggle() // → parchment
      expect(store.resolvedTheme).toBe('parchment')
    })
  })

  // ── setTheme ───────────────────────────────────────────────────────────────
  describe('setTheme()', () => {
    it('sets userPreference and updates document attribute', () => {
      const store = useThemeStore()
      store.setTheme('parchment')

      expect(store.userPreference).toBe('parchment')
      expect(setAttributeMock).toHaveBeenCalledWith('data-theme', 'parchment')
    })

    it('persists to localStorage', () => {
      const store = useThemeStore()
      store.setTheme('starry-night')

      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'madousho_theme',
        JSON.stringify({ userPreference: 'starry-night' })
      )
    })

    it('overwrites previous preference', () => {
      const store = useThemeStore()
      store.setTheme('parchment')
      store.setTheme('starry-night')

      expect(store.userPreference).toBe('starry-night')
      expect(store.resolvedTheme).toBe('starry-night')
    })
  })

  // ── localStorage persistence ───────────────────────────────────────────────
  describe('persistence', () => {
    it('saves userPreference to localStorage key "madousho_theme"', () => {
      const store = useThemeStore()
      store.setTheme('parchment')

      const calls = localStorageMock.setItem.mock.calls
      expect(calls.length).toBeGreaterThan(0)
      const lastCall = calls[calls.length - 1]
      expect(lastCall).toBeDefined()
      expect(lastCall![0]).toBe('madousho_theme')

      const parsed = JSON.parse(lastCall![1])
      expect(parsed).toEqual({ userPreference: 'parchment' })
    })

    it('saves null userPreference on resetToSystem', () => {
      const store = useThemeStore()
      store.setTheme('parchment')
      store.resetToSystem()

      const calls = localStorageMock.setItem.mock.calls
      const lastCall = calls[calls.length - 1]
      expect(lastCall).toBeDefined()
      const parsed = JSON.parse(lastCall![1])
      expect(parsed).toEqual({ userPreference: null })
    })
  })

  // ── resetToSystem ──────────────────────────────────────────────────────────
  describe('resetToSystem()', () => {
    it('clears userPreference back to null', () => {
      const store = useThemeStore()
      store.setTheme('parchment')
      expect(store.userPreference).toBe('parchment')

      store.resetToSystem()

      expect(store.userPreference).toBeNull()
    })

    it('resolvedTheme falls back to systemPreference', () => {
      const store = useThemeStore()
      store.setTheme('parchment')

      store.resetToSystem()

      expect(store.resolvedTheme).toBe('starry-night') // default systemPreference
      expect(store.isDark).toBe(true)
    })

    it('updates document data-theme to system preference', () => {
      const store = useThemeStore()
      store.setTheme('parchment')
      setAttributeMock.mockClear()

      store.resetToSystem()

      expect(setAttributeMock).toHaveBeenCalledWith('data-theme', 'starry-night')
    })
  })

  // ── systemPreference / matchMedia ──────────────────────────────────────────
  describe('initSystemListener()', () => {
    it('reads initial system preference from matchMedia', () => {
      matchMediaMock = createMatchMediaMock(false) // light mode
      window.matchMedia = vi.fn(() => matchMediaMock) as unknown as Window['matchMedia']

      const store = useThemeStore()
      store.initSystemListener()

      expect(store.systemPreference).toBe('parchment')
    })

    it('sets systemPreference to starry-night when prefers dark', () => {
      matchMediaMock = createMatchMediaMock(true)
      window.matchMedia = vi.fn(() => matchMediaMock) as unknown as Window['matchMedia']

      const store = useThemeStore()
      store.initSystemListener()

      expect(store.systemPreference).toBe('starry-night')
    })

    it('updates document data-theme when no user preference', () => {
      const store = useThemeStore()
      store.initSystemListener()

      expect(setAttributeMock).toHaveBeenCalledWith('data-theme', 'starry-night')
    })

    it('does NOT update document when userPreference is set', () => {
      const store = useThemeStore()
      store.setTheme('parchment')
      setAttributeMock.mockClear()

      store.initSystemListener()

      // userPreference is set, should not override
      expect(setAttributeMock).not.toHaveBeenCalled()
    })

    it('registers change listener on matchMedia', () => {
      const store = useThemeStore()
      store.initSystemListener()

      expect(matchMediaMock.addEventListener).toHaveBeenCalledWith(
        'change',
        expect.any(Function)
      )
    })

    it('updates systemPreference on media query change (no user preference)', () => {
      const store = useThemeStore()
      store.initSystemListener()

      // simulate user switching to light mode
      matchMediaMock.__triggerChange(false)

      expect(store.systemPreference).toBe('parchment')
      expect(store.resolvedTheme).toBe('parchment')
      expect(setAttributeMock).toHaveBeenCalledWith('data-theme', 'parchment')
    })

    it('ignores media query change when userPreference is set', () => {
      const store = useThemeStore()
      store.setTheme('starry-night')
      store.initSystemListener()
      setAttributeMock.mockClear()

      matchMediaMock.__triggerChange(false)

      // listener skips update entirely when userPreference is set
      // systemPreference stays at initial value from initSystemListener()
      // (starry-night because default mock is dark mode)
      expect(store.systemPreference).toBe('starry-night')
      expect(store.resolvedTheme).toBe('starry-night') // userPreference wins
      expect(setAttributeMock).not.toHaveBeenCalled()
    })
  })

  // ── Computed properties ────────────────────────────────────────────────────
  describe('computed properties', () => {
    it('resolvedTheme returns userPreference when set', () => {
      const store = useThemeStore()
      store.setTheme('parchment')

      expect(store.resolvedTheme).toBe('parchment')
    })

    it('resolvedTheme returns systemPreference when userPreference is null', () => {
      const store = useThemeStore()

      expect(store.userPreference).toBeNull()
      expect(store.resolvedTheme).toBe('starry-night')
    })

    it('isDark is true for starry-night', () => {
      const store = useThemeStore()
      store.setTheme('starry-night')

      expect(store.isDark).toBe(true)
    })

    it('isDark is false for parchment', () => {
      const store = useThemeStore()
      store.setTheme('parchment')

      expect(store.isDark).toBe(false)
    })

    it('naiveTheme returns darkTheme object when dark', () => {
      const store = useThemeStore()
      store.setTheme('starry-night')

      expect(store.naiveTheme).toEqual({ name: 'dark' })
    })

    it('naiveTheme returns null when light', () => {
      const store = useThemeStore()
      store.setTheme('parchment')

      expect(store.naiveTheme).toBeNull()
    })
  })

  // ── Edge cases ─────────────────────────────────────────────────────────────
  describe('edge cases', () => {
    it('store starts with null userPreference', () => {
      const store = useThemeStore()

      expect(store.userPreference).toBeNull()
    })

    it('store starts with starry-night systemPreference', () => {
      const store = useThemeStore()

      expect(store.systemPreference).toBe('starry-night')
    })

    it('toggle works when userPreference is null (uses system default)', () => {
      const store = useThemeStore()
      // systemPreference = starry-night, so toggle → parchment
      store.toggle()

      expect(store.userPreference).toBe('parchment')
    })

    it('handles localStorage.setItem throwing (e.g. quota exceeded)', () => {
      localStorageMock.setItem.mockImplementationOnce(() => {
        throw new Error('QuotaExceededError')
      })
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

      const store = useThemeStore()
      store.setTheme('parchment')

      // should not throw, just log
      expect(consoleSpy).toHaveBeenCalledWith(
        'Failed to persist theme to storage:',
        expect.any(Error)
      )
      consoleSpy.mockRestore()
    })

    it('handles localStorage.getItem throwing', () => {
      localStorageMock.getItem.mockImplementationOnce(() => {
        throw new Error('SecurityError')
      })
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

      const store = useThemeStore()
      store.loadFromStorage()

      expect(consoleSpy).toHaveBeenCalledWith(
        'Failed to load theme from storage:',
        expect.any(Error)
      )
      expect(store.userPreference).toBeNull()
      consoleSpy.mockRestore()
    })
  })
})
