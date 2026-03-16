import { setupWorker } from 'msw/browser'
import { handlers } from './handlers'

/**
 * Browser MSW setup using setupWorker.
 *
 * Used for development mode to intercept requests in the browser.
 */
export const worker = setupWorker(...handlers)
