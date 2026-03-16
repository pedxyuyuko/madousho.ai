import { setupServer } from 'msw/node'
import { handlers } from './handlers'

/**
 * Node.js MSW setup using setupServer.
 *
 * Used for testing (Vitest) to intercept requests in Node.js environment.
 */
export const server = setupServer(...handlers)
