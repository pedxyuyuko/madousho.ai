<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import apiClient from '@/api/client'
import type { Flow, FlowListResponse } from '@/types/flow'

const { t } = useI18n()

const loading = ref(true)
const error = ref(false)
const flows = ref<Flow[]>([])

const statusTypeMap: Record<Flow['status'], 'success' | 'warning' | 'default'> = {
  finished: 'success',
  processing: 'warning',
  created: 'default',
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
      <n-card v-for="flow in flows" :key="flow.uuid" class="flow-card">
        <template #header>
          <div class="flow-header">
            <span class="flow-name">{{ flow.name }}</span>
            <n-tag :type="statusTypeMap[flow.status]" size="small">
              {{ flow.status }}
            </n-tag>
          </div>
        </template>

        <n-collapse>
          <n-collapse-item :title="t('admin.flows.description')" name="details">
            <div class="flow-detail">
              <span class="detail-label">{{ t('admin.flows.description') }}:</span>
              <span class="detail-value">{{ flow.description ?? '—' }}</span>
            </div>
            <div class="flow-detail">
              <span class="detail-label">{{ t('admin.flows.uuid') }}:</span>
              <span class="detail-value uuid">{{ flow.uuid }}</span>
            </div>
          </n-collapse-item>
        </n-collapse>
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
}

.flow-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.flow-name {
  font-weight: 500;
}

.flow-detail {
  display: flex;
  gap: 0.5rem;
  padding: 0.25rem 0;
}

.detail-label {
  font-weight: 500;
  color: var(--n-text-color-3);
}

.detail-value {
  word-break: break-word;
}

.detail-value.uuid {
  font-family: monospace;
  font-size: 0.875rem;
}
</style>
