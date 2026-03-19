<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

type SupportedLocale = 'zh-CN' | 'en-US'

interface DropdownOption {
  label: string
  key: SupportedLocale
}

const { locale } = useI18n()

const localeLabels: Record<SupportedLocale, string> = {
  'zh-CN': '中文',
  'en-US': 'English',
}

const supportedLocales: SupportedLocale[] = ['zh-CN', 'en-US']

const currentLocale = computed<SupportedLocale>(() =>
  locale.value === 'en-US' ? 'en-US' : 'zh-CN',
)

const currentLocaleLabel = computed(() => localeLabels[currentLocale.value])

const dropdownOptions = computed<DropdownOption[]>(() =>
  supportedLocales.map((item) => ({
    label: item === currentLocale.value ? `✓ ${localeLabels[item]}` : localeLabels[item],
    key: item,
  })),
)

function handleSelect(key: string | number) {
  if (key === currentLocale.value) {
    return
  }

  locale.value = key as SupportedLocale
}
</script>

<template>
  <n-dropdown :options="dropdownOptions" trigger="click" @select="handleSelect">
    <button class="language-switcher" data-testid="language-switcher" type="button">
      <span class="language-switcher__label">{{ currentLocaleLabel }}</span>
      <span class="language-switcher__chevron">▾</span>
    </button>
  </n-dropdown>
</template>

<style scoped>
.language-switcher {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: transparent;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  color: inherit;
  transition: background 0.35s ease, border-color 0.35s ease;
}

.language-switcher:hover {
  background: var(--theme-hover);
  border-color: var(--color-border-hover);
}

.language-switcher__label {
  white-space: nowrap;
}

.language-switcher__chevron {
  font-size: 10px;
  color: var(--theme-text-muted);
}
</style>
