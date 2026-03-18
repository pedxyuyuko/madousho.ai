<script setup lang="ts">
import { useAuthStore } from '@/stores/auth.store'
import { useI18n } from 'vue-i18n'
import ThemeSwitcher from '@/components/ThemeSwitcher.vue'

const authStore = useAuthStore()
const { t } = useI18n()
</script>

<template>
  <main class="home">
    <div class="status-card">
      <span class="status-dot" />
      <span class="status-text">{{ t('home.status.connected') }}</span>
    </div>
    <p class="backend-url">{{ authStore.currentBaseUrl ?? '—' }}</p>
    <ThemeSwitcher />
  </main>
</template>

<style scoped>
.home {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 60px); /* Account for header height */
  gap: 1rem;
}

.status-card {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: 999px;
  background: var(--theme-success-bg);
  border: 1px solid var(--theme-success-border);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--theme-success);
}

.status-text {
  font-size: 1rem;
  font-weight: 500;
  color: var(--theme-success);
}

.backend-url {
  font-size: 0.875rem;
  color: var(--theme-text-muted);
  margin: 0;
}
</style>
