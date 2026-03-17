<script setup lang="ts">
import { useAuthStore } from '@/stores/auth.store'

const authStore = useAuthStore()
</script>

<template>
  <main class="home">
    <div class="status-card">
      <span class="status-dot" />
      <span class="status-text">已连接</span>
    </div>
    <p class="backend-url">{{ authStore.currentBaseUrl ?? '—' }}</p>
  </main>
</template>

<style scoped>
.home {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 80vh;
  gap: 1rem;
}

.status-card {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: 999px;
  background: rgba(34, 197, 94, 0.1);
  border: 1px solid rgba(34, 197, 94, 0.3);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #22c55e;
}

.status-text {
  font-size: 1rem;
  font-weight: 500;
  color: #22c55e;
}

.backend-url {
  font-size: 0.875rem;
  color: #94a3b8;
  margin: 0;
}
</style>
