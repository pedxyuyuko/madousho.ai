<script setup lang="ts">
import { RouterView } from 'vue-router'
import BackendSwitcher from '@/components/BackendSwitcher.vue'
</script>

<template>
  <div class="admin-layout">
    <header class="admin-header">
      <div class="header-spacer" />
      <BackendSwitcher />
    </header>
    <main class="admin-content">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.admin-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.admin-header {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 0.5rem 1rem;
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}

.header-spacer {
  flex: 1;
}

.admin-content {
  flex: 1;
}
</style>
