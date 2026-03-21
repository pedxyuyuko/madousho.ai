<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
</script>

<template>
  <section class="create-flow-placeholder" data-testid="create-flow-placeholder">
    <div class="create-flow-placeholder__card">
      <h2 class="create-flow-placeholder__title">{{ t('admin.createFlow.title') }}</h2>
      <p class="create-flow-placeholder__description">{{ t('admin.createFlow.description') }}</p>
    </div>
  </section>
</template>

<style scoped>
.create-flow-placeholder {
  display: flex;
  align-items: flex-start;
  justify-content: center;
  min-height: calc(100vh - 120px);
  padding: 24px;
}

.create-flow-placeholder__card {
  width: min(100%, 640px);
  padding: 24px;
  border: 1px solid var(--color-border);
  border-radius: 16px;
  background: var(--theme-hover);
  box-shadow: 0 18px 40px -32px rgba(15, 23, 42, 0.35);
}

.create-flow-placeholder__title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--n-text-color-1);
}

.create-flow-placeholder__description {
  margin: 12px 0 0;
  font-size: 0.95rem;
  line-height: 1.6;
  color: var(--theme-text-muted);
}
</style>
