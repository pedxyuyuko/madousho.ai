# Learnings
- `filtered-empty` stays reachable only when query state is tracked separately from backend results; with backend `name`/`status` filtering, `flows.length === 0` must branch on active query vs default fetch.
- Naive UI `n-select` needs real trigger/overlay interaction in Playwright; browser tests should not fake native `<select>` behavior for mounted app coverage.
- When a toolbar test needs to clear a Naive UI select reliably, prefer an explicit app-owned test hook over `.n-base-clear` or other library-private classes.
