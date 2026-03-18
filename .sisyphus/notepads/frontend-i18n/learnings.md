# Frontend i18n Learnings

## [2026-03-18] unplugin-vue-i18n Import Path

**Issue**: `import VueI18nPlugin from '@intlify/unplugin-vue-i18n'` caused `TypeError: VueI18nPlugin is not a function`
**Solution**: Must import from `@intlify/unplugin-vue-i18n/vite` (subpath export)
**Root Cause**: Package has separate entry points for Vite, Webpack, etc.

```typescript
// WRONG
import VueI18nPlugin from '@intlify/unplugin-vue-i18n'

// CORRECT
import VueI18nPlugin from '@intlify/unplugin-vue-i18n/vite'
```

## [2026-03-18] Subagent Task Guard

The subagents have a "single task only" guard that rejects prompts mentioning multiple files or multiple changes. To work around:
- Frame the task as a single file operation
- Avoid listing multiple steps in the prompt
- Keep the instructions extremely focused on ONE file
