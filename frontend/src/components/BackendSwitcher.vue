<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.store'

const authStore = useAuthStore()
const router = useRouter()

const displayLabel = computed(() => {
  const backend = authStore.currentBackend
  return backend?.name || backend?.baseUrl || 'No backend'
})

interface DropdownOption {
  label: string
  key: string | number
}

const dropdownOptions = computed<DropdownOption[]>(() => {
  const items: DropdownOption[] = authStore.backendOptions.map((opt) => ({
    label: opt.value === authStore.currentBackendIndex ? `✓ ${opt.label}` : opt.label,
    key: opt.value,
  }))
  items.push({
    label: '+ Add new',
    key: 'add-new',
  })
  return items
})

function handleSelect(key: string | number) {
  if (key === 'add-new') {
    router.push('/login')
    return
  }
  const index = Number(key)
  if (!Number.isNaN(index) && index !== authStore.currentBackendIndex) {
    authStore.switchBackend(index)
  }
}
</script>

<template>
  <n-dropdown :options="dropdownOptions" trigger="click" @select="handleSelect">
    <button class="backend-switcher" type="button">
      <span class="backend-switcher__label">{{ displayLabel }}</span>
      <span class="backend-switcher__chevron">▾</span>
    </button>
  </n-dropdown>
</template>

<style scoped>
.backend-switcher {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: transparent;
  border: 1px solid var(--n-border-color, #e0e0e6);
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  color: inherit;
  transition: background 0.2s, border-color 0.2s;
}

.backend-switcher:hover {
  background: var(--theme-hover, rgba(0, 0, 0, 0.05));
  border-color: var(--n-primary-color, #18a058);
}

.backend-switcher__label {
  max-width: 160px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.backend-switcher__chevron {
  font-size: 10px;
  opacity: 0.6;
}
</style>
