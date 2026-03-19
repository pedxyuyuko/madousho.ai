<script setup lang="ts">
import { computed, ref, h } from 'vue'
import type { Component } from 'vue'
import { RouterView, useRouter, useRoute } from 'vue-router'
import { NButton, NIcon } from 'naive-ui'
import {
  ChevronBackOutline,
  SparklesOutline,
  GridOutline,
  GitNetworkOutline,
} from '@vicons/ionicons5'
import { useI18n } from 'vue-i18n'
import BackendSwitcher from '@/components/BackendSwitcher.vue'
import ThemeSwitcher from '@/components/ThemeSwitcher.vue'
import LanguageSwitcher from '@/components/LanguageSwitcher.vue'
import { useAuthStore } from '@/stores/auth.store'
import type { MenuItem } from '@/types/menu'

const collapsed = ref(false)
const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const { t } = useI18n()

const renderIcon = (icon: Component) => () => h(NIcon, null, { default: () => h(icon) })

const menuItems = computed<MenuItem[]>(() => [
  {
    label: t('admin.sidebar.home'),
    key: 'home',
    icon: GridOutline,
  },
  {
    label: t('admin.sidebar.flows'),
    key: 'flows',
    icon: GitNetworkOutline,
  },
])

const naiveMenuOptions = computed(() =>
  menuItems.value.map((item) => ({
    key: item.key,
    label: item.label,
    icon: item.icon ? renderIcon(item.icon) : undefined,
  }))
)

function toggleSidebar() {
  collapsed.value = !collapsed.value
}

function handleMenuUpdate(key: string) {
  const resolved = router.resolve({ name: key })
  if (resolved.name) {
    router.push(resolved)
  }
}

async function handleLogout() {
  authStore.logout()
  await router.push(router.resolve({ name: 'login' }))
}
</script>

<template>
  <n-layout has-sider class="admin-layout" data-testid="admin-layout">
    <n-layout-sider
      bordered
      collapse-mode="width"
      :collapsed="collapsed"
      :collapsed-width="64"
      :width="240"
      content-style="display: flex; flex-direction: column;"
      class="admin-sidebar"
      data-testid="admin-sidebar"
      @collapse="collapsed = true"
      @expand="collapsed = false"
    >
      <div class="sidebar-brand" :class="{ collapsed }">
        <div class="brand-mark" aria-hidden="true">
          <n-icon size="20">
            <SparklesOutline />
          </n-icon>
        </div>
        <div v-if="!collapsed" class="brand-copy">
          <span class="brand-title">魔导书</span>
          <span class="brand-subtitle">AI Agent Atelier</span>
        </div>
      </div>

      <n-button
        quaternary
        circle
        class="sidebar-toggle"
        :class="{ collapsed }"
        data-testid="sidebar-toggle"
        :aria-label="t('admin.sidebar.toggle')"
        @click="toggleSidebar"
      >
        <template #icon>
          <n-icon :class="{ collapsed }">
            <ChevronBackOutline />
          </n-icon>
        </template>
      </n-button>

      <n-menu
        :collapsed="collapsed"
        :collapsed-width="64"
        :collapsed-icon-size="20"
        :root-indent="22"
        :options="naiveMenuOptions"
        :value="route.name"
        class="sidebar-menu"
        @update:value="handleMenuUpdate"
      />
    </n-layout-sider>

    <n-layout>
      <n-layout-header bordered class="admin-header" data-testid="admin-header">
        <div class="header-spacer" />
        <div class="header-actions">
          <ThemeSwitcher />
          <LanguageSwitcher />
          <BackendSwitcher />
          <n-button tertiary type="default" data-testid="logout-btn" @click="handleLogout">
            {{ t('admin.header.logout') }}
          </n-button>
        </div>
      </n-layout-header>

      <n-layout-content class="admin-content">
        <RouterView />
      </n-layout-content>
    </n-layout>
  </n-layout>
</template>

<style scoped>
.admin-layout {
  min-height: 100vh;
  color: inherit;
}

.admin-sidebar {
  border-right: 1px solid var(--color-border);
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 14px 12px;
  min-height: 76px;
}

.sidebar-brand.collapsed {
  justify-content: center;
  padding: 20px 0 12px;
}

.brand-mark {
  width: 36px;
  height: 36px;
  border: 1px solid var(--color-border);
  border-radius: 12px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--theme-hover);
  flex-shrink: 0;
}

.brand-copy {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.brand-title {
  font-size: 18px;
  line-height: 1.1;
  font-weight: 700;
  letter-spacing: 0.08em;
}

.brand-subtitle {
  font-size: 11px;
  line-height: 1.2;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--theme-text-muted);
}

.sidebar-toggle {
  margin: 0 15px 12px;
}

.sidebar-toggle.collapsed {
  margin: 0 15px 12px;
}

.sidebar-toggle :deep(.n-icon) {
  transition: transform 0.25s ease;
}

.sidebar-toggle :deep(.n-icon.collapsed) {
  transform: rotate(180deg);
}

.sidebar-menu {
  flex: 1;
  padding: 0 0 16px;
}

.admin-header {
  display: flex;
  align-items: center;
  min-height: 72px;
  padding: 0 24px;
  border-bottom: 1px solid var(--color-border);
  backdrop-filter: blur(12px);
}

.header-spacer {
  flex: 1;
}

.header-actions {
  display: inline-flex;
  align-items: center;
  gap: 12px;
}

.admin-content {
  min-height: calc(100vh - 72px);
  padding: 24px;
  background: transparent;
}

:global([data-theme='starry-night'] .admin-layout) {
  color: #e2dff0;
  background:
    radial-gradient(circle at top, rgba(124, 58, 237, 0.16) 0%, transparent 45%),
    linear-gradient(180deg, #0a0a14 0%, #12101f 100%);
}

:global([data-theme='starry-night'] .admin-sidebar) {
  background: linear-gradient(180deg, rgba(18, 16, 31, 0.96) 0%, rgba(12, 10, 20, 0.92) 100%);
  box-shadow: inset -1px 0 0 rgba(124, 58, 237, 0.1);
}

:global([data-theme='starry-night'] .admin-header) {
  background: rgba(18, 16, 31, 0.88);
}

:global([data-theme='starry-night'] .brand-mark) {
  color: #8b5cf6;
  box-shadow: 0 12px 24px -18px rgba(124, 58, 237, 0.8);
}

:global([data-theme='starry-night'] .brand-title),
:global([data-theme='starry-night'] .sidebar-toggle) {
  color: #e2dff0;
}

:global([data-theme='parchment'] .admin-layout) {
  color: #3d2b1f;
  background:
    radial-gradient(circle at top, rgba(139, 69, 19, 0.1) 0%, transparent 45%),
    linear-gradient(180deg, #f5e6c8 0%, #f0e2c4 100%);
}

:global([data-theme='parchment'] .admin-sidebar) {
  background: linear-gradient(180deg, rgba(237, 224, 204, 0.98) 0%, rgba(232, 213, 184, 0.92) 100%);
  box-shadow: inset -1px 0 0 rgba(139, 69, 19, 0.08);
}

:global([data-theme='parchment'] .admin-header) {
  background: rgba(237, 224, 204, 0.92);
}

:global([data-theme='parchment'] .brand-mark) {
  color: #8b4513;
  box-shadow: 0 12px 24px -18px rgba(139, 69, 19, 0.45);
}

:global([data-theme='parchment'] .brand-title),
:global([data-theme='parchment'] .sidebar-toggle) {
  color: #3d2b1f;
}
</style>
