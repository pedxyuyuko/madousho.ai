# Issues
- Playwright + ESLint can race on transient `test-results/` scanning when run in parallel after failures; run lint sequentially after browser tests for stable verification.
