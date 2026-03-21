<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import apiClient from '@/api/client'
import type { Flow, FlowListResponse } from '@/types/flow'

const { t } = useI18n()

const loading = ref(true)
const error = ref(false)
const flows = ref<Flow[]>([])
const expandedFlows = ref<Set<string>>(new Set())
const currentRequestId = ref(0)

// Toolbar state
const keyword = ref('')
const selectedStatus = ref<Flow['status'] | null>(null)
const createdAtSort = ref<'asc' | 'desc'>('desc')

const statusTypeMap: Record<Flow['status'], 'success' | 'warning' | 'default'> = {
  finished: 'success',
  processing: 'warning',
  created: 'default',
}

// Status options for select (no synthetic "all" option; clearable handles that)
const statusOptions = computed(() => [
  { label: t('admin.flows.statusCreated'), value: 'created' },
  { label: t('admin.flows.statusProcessing'), value: 'processing' },
  { label: t('admin.flows.statusFinished'), value: 'finished' },
])

// Sort options for select
const sortOptions = computed(() => [
  { label: t('admin.flows.sortNewest'), value: 'desc' },
  { label: t('admin.flows.sortOldest'), value: 'asc' },
])

// Check if any backend query is active (for filtered-empty detection)
const isQueryActive = computed(() => {
  return keyword.value.trim() !== '' || selectedStatus.value !== null
})

// Build query params for backend request
function buildQueryParams() {
  const trimmedKeyword = keyword.value.trim()
  const params: Record<string, string> = {}

  if (trimmedKeyword) {
    params.name = trimmedKeyword
  }

  if (selectedStatus.value) {
    params.status = selectedStatus.value
  }

  return Object.keys(params).length === 0 ? undefined : { params }
}

// Parse created_at timestamp
function parseCreatedAt(value: string): number | null {
  const timestamp = Date.parse(value)
  return Number.isNaN(timestamp) ? null : timestamp
}

// Computed displayed flows with frontend-local sorting only
const displayedFlows = computed(() => {
  const direction = createdAtSort.value

  return [...flows.value].sort((left, right) => {
    const leftTime = parseCreatedAt(left.created_at)
    const rightTime = parseCreatedAt(right.created_at)

    if (leftTime === null && rightTime === null) {
      return left.uuid.localeCompare(right.uuid)
    }

    if (leftTime === null) {
      return 1
    }

    if (rightTime === null) {
      return -1
    }

    if (leftTime === rightTime) {
      return left.uuid.localeCompare(right.uuid)
    }

    return direction === 'asc' ? leftTime - rightTime : rightTime - leftTime
  })
})

// Query-active empty state must stay distinct from the default fetch-empty state.
const isFilteredEmpty = computed(() => {
  return isQueryActive.value && flows.value.length === 0
})

const toggleExpanded = (uuid: string) => {
  if (expandedFlows.value.has(uuid)) {
    expandedFlows.value.delete(uuid)
  } else {
    expandedFlows.value.add(uuid)
  }
}

// Reset all filters to defaults
function resetFilters() {
  keyword.value = ''
  selectedStatus.value = null
  createdAtSort.value = 'desc'
}

// Fetch flows with backend-supported query params only.
async function fetchFlows() {
  loading.value = true
  error.value = false

  const requestId = ++currentRequestId.value

  try {
    const queryParams = buildQueryParams()
    const response = await apiClient.get<FlowListResponse>('/flows', queryParams)

    // Only apply response if this is still the latest request
    if (requestId === currentRequestId.value) {
      flows.value = response.data.items
    }
  } catch {
    // Only apply error if this is still the latest request
    if (requestId === currentRequestId.value) {
      // 401 interceptor already redirects to /login
      // 403 and other errors show error state
      error.value = true
    }
  } finally {
    if (requestId === currentRequestId.value) {
      loading.value = false
    }
  }
}

// Watch for filter changes and refetch
watch([keyword, selectedStatus], () => {
  fetchFlows()
})

onMounted(() => {
  fetchFlows()
})
</script>

<template>
  <div class="flows-view">
    <h2 class="flows-title">{{ t('admin.flows.title') }}</h2>

    <div class="flows-toolbar" data-testid="flows-toolbar">
      <n-form :inline="true">
        <n-space :size="12" :wrap="true">
          <n-input
            v-model:value="keyword"
            :placeholder="t('admin.flows.keywordPlaceholder')"
            clearable
            data-testid="flows-keyword-input"
            class="toolbar-input"
          />
          <n-select
            v-model:value="selectedStatus"
            :options="statusOptions"
            :placeholder="t('admin.flows.statusPlaceholder')"
            clearable
            data-testid="flows-status-select"
            class="toolbar-select"
          />
          <n-select
            v-model:value="createdAtSort"
            :options="sortOptions"
            data-testid="flows-sort-select"
            class="toolbar-select toolbar-select--sort"
          />
          <n-button
            data-testid="flows-reset-button"
            @click="resetFilters"
            class="toolbar-reset"
          >
            {{ t('admin.flows.reset') }}
          </n-button>
        </n-space>
      </n-form>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flows-state">
      <n-spin size="large" />
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="flows-state">
      <n-result status="error" :title="t('admin.flows.error')" />
    </div>

    <!-- Filtered Empty State (query active but no results) -->
    <div v-else-if="isFilteredEmpty" class="flows-state">
      <n-empty :description="t('admin.flows.filteredEmpty')" data-testid="flows-filtered-empty" />
    </div>

    <!-- Fetch Empty State (no query, no results) -->
    <div v-else-if="flows.length === 0" class="flows-state">
      <n-empty :description="t('admin.flows.empty')" data-testid="flows-fetch-empty" />
    </div>

    <!-- Data State -->
    <div v-else class="flows-list">
      <n-card
        v-for="flow in displayedFlows"
        :key="flow.uuid"
        class="flow-card"
        data-testid="flows-card"
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

.flows-toolbar {
  margin-bottom: 1.5rem;
}

.toolbar-input {
  width: 200px;
}

.toolbar-select {
  width: 140px;
}

.toolbar-select--sort {
  width: 120px;
}

.toolbar-reset {
  min-width: 80px;
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
