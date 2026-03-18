<script setup lang="ts">
import { computed } from 'vue'
import { RouterView } from 'vue-router'
import { NConfigProvider, NGlobalStyle } from 'naive-ui'
import { zhCN, dateZhCN } from 'naive-ui/es/locales'
import { useThemeStore } from '@/stores/theme.store'
import { starryNightOverrides } from '@/theme/starry-night'
import { parchmentOverrides } from '@/theme/parchment'

const themeStore = useThemeStore()

const naiveTheme = computed(() => themeStore.naiveTheme)
const themeOverrides = computed(() =>
  themeStore.isDark ? starryNightOverrides : parchmentOverrides
)
</script>

<template>
  <n-config-provider :theme="naiveTheme" :theme-overrides="themeOverrides" :locale="zhCN" :date-locale="dateZhCN">
    <n-global-style />
    <div class="app-layout" :data-theme="themeStore.resolvedTheme">
      <div
        class="theme-transition-overlay"
        :class="{ active: themeStore.isTransitioning }"
      />
      <RouterView />
    </div>
  </n-config-provider>
</template>

<style scoped>
.app-layout {
  min-height: 100vh;
}
</style>
