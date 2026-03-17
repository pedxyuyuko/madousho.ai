<script setup lang="ts">
import { RouterView } from 'vue-router'
import BackendSwitcher from './components/BackendSwitcher.vue'
import { useAuthStore } from '@/stores/auth.store'

const authStore = useAuthStore()
</script>

<template>
  <div class="app-layout">
    <header v-if="authStore.isAuthenticated" class="app-header">
      <div class="header-spacer" />
      <BackendSwitcher />
    </header>
    <RouterView />
  </div>
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
