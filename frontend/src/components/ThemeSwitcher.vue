<script setup lang="ts">
import { computed } from 'vue'
import { NButton } from 'naive-ui';
import { useThemeStore } from '@/stores/theme.store';

const themeStore = useThemeStore();
const isDark = computed(() => themeStore.isDark);

const handleToggle = () => {
  themeStore.toggle();
};
</script>

<template>
  <NButton
    :aria-label="isDark ? 'Switch to light theme' : 'Switch to dark theme'"
    @click="handleToggle"
    quaternary
    circle
    size="small"
    class="theme-switcher"
  >
    <span class="theme-icon" :class="{ 'dark-theme': isDark }">
      {{ isDark ? '🌙' : '☀️' }}
    </span>
  </NButton>
</template>

<style scoped>
.theme-switcher {
  transition: all 0.3s ease;
}

.theme-icon {
  display: inline-block;
  transition: opacity 0.3s ease, transform 0.3s ease;
  font-size: 16px;
}

.theme-icon.dark-theme {
  transform: rotateY(180deg);
}
</style>