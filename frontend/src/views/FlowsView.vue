<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import apiClient from '@/api/client'
import type { Flow, FlowListResponse } from '@/types/flow'

const { t } = useI18n()

const loading = ref(true)
const error = ref(false)
const flows = ref<Flow[]>([])
const expandedFlows = ref<Set<string>>(new Set())

const statusTypeMap: Record<Flow['status'], 'success' | 'warning' | 'default'> = {
  finished: 'success',
  processing: 'warning',
  created: 'default',
}

const toggleExpanded = (uuid: string) => {
  if (expandedFlows.value.has(uuid)) {
    expandedFlows.value.delete(uuid)
  } else {
    expandedFlows.value.add(uuid)
  }
}

onMounted(async () => {
  try {
    const response = await apiClient.get<FlowListResponse>('/flows')
    flows.value = response.data.items
  } catch {
    // 401 interceptor already redirects to /login
    // 403 and other errors show error state
    error.value = true
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="flows-view">
    <h2 class="flows-title">{{ t('admin.flows.title') }}</h2>

    <!-- Loading State -->
    <div v-if="loading" class="flows-state">
      <n-spin size="large" />
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="flows-state">
      <n-result status="error" :title="t('admin.flows.error')" />
    </div>

    <!-- Empty State -->
    <div v-else-if="flows.length === 0" class="flows-state">
      <n-empty :description="t('admin.flows.empty')" />
    </div>

    <!-- Data State -->
    <div v-else class="flows-list">
      <n-card
        v-for="flow in flows"
        :key="flow.uuid"
        class="flow-card"
        :class="{ 'flow-card--expanded': expandedFlows.has(flow.uuid) }"
        hoverable
        @click="toggleExpanded(flow.uuid)"
      >
        <template #header>
          <div class="flow-header">
            <span class="flow-name">{{ flow.name }}</span>
            <n-tag size="small" class="uuid-tag">
              {{ flow.uuid }}
            </n-tag>
            <n-tag :type="statusTypeMap[flow.status]" size="small">
              {{ flow.status }}
            </n-tag>
            <span class="expand-icon" :class="{ 'expanded': expandedFlows.has(flow.uuid) }">
              ▶
            </span>
          </div>
        </template>

        <transition name="fade">
          <div v-if="expandedFlows.has(flow.uuid)" class="flow-description">
            {{ flow.description ?? '—' }}
          </div>
        </transition>
      </n-card>
    </div>
  </div>
</template>

<style scoped>
.flows-view {
  padding: 1.5rem;
}

.flows-title {
  margin: 0 0 1.5rem;
  font-size: 1.5rem;
  font-weight: 600;
}

.flows-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}

.flows-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.flow-card {
  width: 100%;
  cursor: pointer;
  transition: all 0.2s ease;
}

.flow-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.flow-card--expanded {
  border-left: 3px solid var(--n-primary-color);
}

.flow-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.flow-name {
  font-weight: 500;
}

.uuid-tag {
  font-family: monospace;
  font-size: 0.75rem;
}

.expand-icon {
  margin-left: auto;
  font-size: 0.75rem;
  color: var(--n-text-color-3);
  transition: transform 0.2s ease;
}

.expand-icon.expanded {
  transform: rotate(90deg);
}

.flow-description {
  color: var(--n-text-color-2);
  line-height: 1.6;
  padding-top: 0.5rem;
  border-top: 1px solid var(--n-border-color);
  margin-top: 0.5rem;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
