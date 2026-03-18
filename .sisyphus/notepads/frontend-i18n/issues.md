# Frontend i18n Issues

## [2026-03-18] LoginView.test.ts Pre-existing Failures

**7 of 10 LoginView tests were already broken BEFORE i18n changes.**

Root cause: `NButtonStub` in test doesn't forward click events properly. The stub template:
```vue
<button :disabled="disabled || loading" v-bind="$attrs"><slot /></button>
```
In Vue 3, `$attrs` may not include event listeners depending on version/config. The stub's button never fires click events, so `mockLogin` is never called.

Verified by: `git stash` + running tests on original code → same 7 failures.

Affected tests (pre-existing):
- shows validation — button disabled when fields are empty
- calls authStore.login() on form submit
- shows loading state during login
- shows error alert on login failure
- shows default error message when error has no message
- redirects to / on successful login
- trims input values before calling login

Tests that pass (3/10):
- renders login form with Base URL input, Token input, and Login button
- has left panel (gradient) and right panel (form) structure
- enables button when both fields have values

**Impact**: Our i18n changes did NOT break any previously passing tests.
**i18n assertion update**: The test was updated to use Chinese assertions, but since the tests were already failing, the Chinese assertions are correct but untested via the stub mechanism.
