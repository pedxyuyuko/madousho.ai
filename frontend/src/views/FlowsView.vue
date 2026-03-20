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
        :class="[
          `flow-card--status-${flow.status}`,
          { 'flow-card--expanded': expandedFlows.has(flow.uuid) }
        ]"
        hoverable
        @click="toggleExpanded(flow.uuid)"
      >
        <template #header>
          <div class="flow-header">
            <span class="flow-name">{{ flow.name }}</span>
            <n-tag v-if="flow.plugin" size="small" type="info">
              {{ flow.plugin }}
            </n-tag>
            <n-tag :type="statusTypeMap[flow.status]" size="small">
              {{ flow.status }}
            </n-tag>
            <span class="expand-icon" :class="{ 'expanded': expandedFlows.has(flow.uuid) }">
              ▶
            </span>
          </div>
          <div class="flow-meta">
            <span class="meta-uuid">{{ flow.uuid }}</span>
            <span class="meta-separator">@</span>
            <n-time :time="new Date(flow.created_at)" format="yyyy-MM-dd HH:mm" />
          </div>
        </template>

        <div class="flow-body">
          <div class="flow-description">
            {{ flow.description ?? '—' }}
          </div>

          <transition name="fade">
            <div v-if="expandedFlows.has(flow.uuid)" class="flow-details">
              <div class="detail-row" v-if="flow.flow_template">
                <span class="detail-label">Template:</span>
                <span class="detail-value">{{ flow.flow_template }}</span>
              </div>
              <div class="detail-row" v-if="flow.tasks?.length">
                <span class="detail-label">Tasks:</span>
                <span class="detail-value">{{ flow.tasks.join(', ') }}</span>
              </div>
            </div>
          </transition>
        </div>
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
  color: var(--n-text-color-1);
}

[data-theme="starry-night"] .flows-title {
  color: #f5f3ff;
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

:deep(.flow-card) {
  width: 100%;
  cursor: pointer;
  transition: all 0.2s ease;
  border-left: 4px solid transparent !important;
}

:deep(.flow-card--status-finished) {
  border-left-color: var(--theme-success) !important;
}

:deep(.flow-card--status-processing) {
  border-left-color: var(--theme-warning) !important;
}

:deep(.flow-card--status-created) {
  border-left-color: var(--theme-text-muted) !important;
}

:deep(.flow-card:hover) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.flow-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.flow-meta {
  font-size: 0.75rem;
  color: var(--n-text-color-3);
  margin-top: 0.25rem;
}

.meta-uuid {
  font-family: monospace;
}

.meta-separator {
  margin: 0 0.25rem;
}

.flow-body {
  padding-top: 0.5rem;
  border-top: 1px solid var(--n-border-color);
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
  margin-bottom: 0.5rem;
}

.flow-details {
  padding-top: 0.5rem;
  border-top: 1px dashed var(--n-border-color);
}

.detail-row {
  display: flex;
  gap: 0.5rem;
  padding: 0.25rem 0;
  font-size: 0.875rem;
}

.detail-label {
  color: var(--n-text-color-3);
  font-weight: 500;
}

.detail-value {
  color: var(--n-text-color-2);
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
