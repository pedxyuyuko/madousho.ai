import { http, HttpResponse } from 'msw'

/**
 * MSW request handlers array.
 *
 * Add mock handlers here to intercept API requests during development and testing.
 * Example:
 *   http.get('/api/users', () => {
 *     return HttpResponse.json([{ id: 1, name: 'John' }])
 *   })
 */
export const handlers = [
  http.get('*/api/v1/protected', ({ request }) => {
    const authHeader = request.headers.get('Authorization')
    const token = authHeader?.replace('Bearer ', '')?.trim()

    if (token) {
      return HttpResponse.json({ message: 'authenticated' })
    }

    return HttpResponse.json(
      { error: 'invalid_token', message: 'Authentication required' },
      { status: 401 }
    )
  }),
]
