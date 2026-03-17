<script setup lang="ts">
import { computed } from 'vue'
import { RouterView } from 'vue-router'
import { NConfigProvider, NGlobalStyle } from 'naive-ui'
import BackendSwitcher from './components/BackendSwitcher.vue'
import { useAuthStore } from '@/stores/auth.store'
import { useThemeStore } from '@/stores/theme.store'
import { starryNightOverrides } from '@/theme/starry-night'
import { parchmentOverrides } from '@/theme/parchment'

const authStore = useAuthStore()
const themeStore = useThemeStore()

const naiveTheme = computed(() => themeStore.naiveTheme)
const themeOverrides = computed(() =>
  themeStore.isDark ? starryNightOverrides : parchmentOverrides
)
</script>

<template>
  <n-config-provider :theme="naiveTheme" :theme-overrides="themeOverrides">
    <n-global-style />
    <div class="app-layout" :data-theme="themeStore.resolvedTheme">
      <div
        class="theme-transition-overlay"
        :class="{ active: themeStore.isTransitioning }"
      />
      <header v-if="authStore.isAuthenticated" class="app-header">
        <div class="header-spacer" />
        <BackendSwitcher />
      </header>
      <RouterView />
    </div>
  </n-config-provider>
</template>

<style scoped>
.app-layout {
  min-height: 100vh;
}

.app-header {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 0.5rem 1rem;
  border-bottom: 1px solid var(--color-border);
}

.header-spacer {
  flex: 1;
}
</style>
