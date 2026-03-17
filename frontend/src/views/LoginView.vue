<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.store'

const router = useRouter()
const authStore = useAuthStore()

const baseUrl = ref(window.location.origin)
const token = ref('')
const isLoading = ref(false)
const error = ref('')

const canSubmit = computed(() => baseUrl.value.trim() !== '' && token.value.trim() !== '')

async function handleLogin() {
  if (!canSubmit.value) return

  isLoading.value = true
  error.value = ''

  try {
    await authStore.login(baseUrl.value.trim(), token.value.trim())
    router.push('/')
  } catch (err: any) {
    error.value = err?.message || 'Connection failed. Check your credentials.'
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <!-- Left gradient panel -->
    <div class="login-gradient">
      <div class="gradient-content">
        <div class="glow-orb glow-orb--primary"></div>
        <div class="glow-orb glow-orb--secondary"></div>
        <div class="glow-orb glow-orb--tertiary"></div>
        <div class="brand">
          <h1 class="brand-title">Madousho.ai</h1>
          <p class="brand-subtitle">Systematic AI Agent Framework</p>
          <p class="brand-tagline">-</p>
        </div>
      </div>
    </div>

    <!-- Right form panel -->
    <div class="login-form-panel">
      <div class="form-container">
        <h2 class="form-title">Connect</h2>
        <p class="form-description">Enter your backend credentials to get started.</p>

        <n-alert
          v-if="error"
          type="error"
          :bordered="false"
          :show-icon="true"
          class="form-error"
        >
          {{ error }}
        </n-alert>

        <form @submit.prevent="handleLogin" class="form-fields">
          <!-- Loading shimmer overlay -->
          <div v-if="isLoading" class="loading-overlay">
            <div class="shimmer-bar"></div>
            <div class="shimmer-bar shimmer-bar--delayed"></div>
            <div class="shimmer-bar shimmer-bar--short"></div>
          </div>

          <div class="field-group">
            <label class="field-label" for="base-url">Base URL</label>
            <n-input
              id="base-url"
              v-model:value="baseUrl"
              :disabled="isLoading"
              size="large"
              class="field-input"
            />
          </div>

          <div class="field-group">
            <label class="field-label" for="token">API Token</label>
            <n-input
              id="token"
              v-model:value="token"
              type="password"
              show-password-on="click"
              placeholder="Enter your API token"
              :disabled="isLoading"
              size="large"
              class="field-input"
            />
          </div>

          <n-button
            type="primary"
            size="large"
            block
            :loading="isLoading"
            :disabled="!canSubmit"
            @click="handleLogin"
            class="submit-btn"
          >
            {{ isLoading ? 'Connecting...' : 'Connect' }}
          </n-button>
        </form>

        <p class="form-footer">
          Your credentials are stored locally and never shared.
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.login-page {
  display: flex;
  min-height: 100vh;
  width: 100%;
  background: #0a0a0f;
}

// Left gradient panel
.login-gradient {
  flex: 0 0 70%;
  position: relative;
  overflow: hidden;
  background: linear-gradient(
    135deg,
    #0d0d1a 0%,
    #1a1035 25%,
    #2d1b4e 50%,
    #1a1035 75%,
    #0d0d1a 100%
  );
  display: flex;
  align-items: center;
  justify-content: center;
}

.gradient-content {
  position: relative;
  z-index: 2;
  text-align: center;
}

.glow-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.4;
  pointer-events: none;
}

.glow-orb--primary {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, #7c3aed 0%, transparent 70%);
  top: 20%;
  left: 30%;
  animation: pulse-slow 8s ease-in-out infinite;
}

.glow-orb--secondary {
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, #2563eb 0%, transparent 70%);
  bottom: 20%;
  right: 20%;
  animation: pulse-slow 10s ease-in-out infinite reverse;
}

.glow-orb--tertiary {
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, #4f46e5 0%, transparent 70%);
  top: 60%;
  left: 15%;
  animation: pulse-slow 6s ease-in-out infinite;
}

@keyframes pulse-slow {
  0%,
  100% {
    transform: scale(1);
    opacity: 0.3;
  }
  50% {
    transform: scale(1.15);
    opacity: 0.5;
  }
}

.brand {
  position: relative;
  z-index: 3;
}

.brand-title {
  font-size: 5rem;
  font-weight: 300;
  color: #e8e0f0;
  letter-spacing: 0.2em;
  margin-bottom: $spacing-sm;
  text-shadow: 0 0 60px rgba(124, 58, 237, 0.4);
  font-family: 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', serif;
}

.brand-subtitle {
  font-size: 1.25rem;
  color: rgba(232, 224, 240, 0.6);
  letter-spacing: 0.35em;
  text-transform: uppercase;
  font-family: 'JetBrains Mono', monospace;
}

.brand-tagline {
  margin-top: $spacing-lg;
  font-size: 0.875rem;
  color: rgba(232, 224, 240, 0.35);
  letter-spacing: 0.15em;
}

// Right form panel - Enhancement 2: Glowing gradient divider
.login-form-panel {
  flex: 0 0 30%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  position: relative;
  padding: $spacing-xl;

  &::before {
    content: '';
    position: absolute;
    left: 0;
    top: 10%;
    height: 80%;
    width: 1px;
    background: linear-gradient(
      to bottom,
      transparent,
      rgba(124, 58, 237, 0.15) 20%,
      rgba(124, 58, 237, 0.5) 50%,
      rgba(79, 70, 229, 0.5) 70%,
      rgba(124, 58, 237, 0.15) 80%,
      transparent
    );
    box-shadow:
      0 0 8px rgba(124, 58, 237, 0.3),
      0 0 24px rgba(124, 58, 237, 0.1);
  }
}

// Enhancement 4: Glass-morphism on form container
.form-container {
  width: 100%;
  max-width: 360px;
  background: rgba(15, 15, 24, 0.7);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 16px;
  padding: $spacing-xl;
  position: relative;
}

.form-title {
  font-size: 1.75rem;
  font-weight: 600;
  color: #e8e0f0;
  margin-bottom: $spacing-sm;
}

.form-description {
  font-size: 0.875rem;
  color: rgba(232, 224, 240, 0.45);
  margin-bottom: $spacing-xl;
  line-height: 1.5;
}

.form-error {
  margin-bottom: $spacing-lg;
}

.field-group {
  margin-bottom: $spacing-lg;
}

.field-label {
  display: block;
  font-size: 0.75rem;
  font-weight: 500;
  color: rgba(232, 224, 240, 0.55);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: $spacing-sm;
}

.field-input {
  width: 100%;
}

.submit-btn {
  margin-top: $spacing-xl;
  height: 48px;
  font-size: 1rem;
  font-weight: 500;
  letter-spacing: 0.05em;
}

.form-footer {
  margin-top: $spacing-xl;
  font-size: 0.75rem;
  color: rgba(232, 224, 240, 0.25);
  text-align: center;
  line-height: 1.5;
}

// Enhancement 1: Input Focus Glow Effect
.field-input {
  width: 100%;
  transition: box-shadow 0.2s ease;

  &:focus-within {
    box-shadow: 0 0 0 2px rgba(124, 58, 237, 0.3);
  }
}

// Enhancement 3: Loading Skeleton Shimmer
.form-fields {
  position: relative;
}

.loading-overlay {
  position: absolute;
  inset: 0;
  z-index: 10;
  background: rgba(15, 15, 24, 0.5);
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 0 16px;
  justify-content: center;
}

.shimmer-bar {
  height: 48px;
  border-radius: 6px;
  background: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0.02) 0%,
    rgba(255, 255, 255, 0.06) 40%,
    rgba(255, 255, 255, 0.02) 100%
  );
  background-size: 200% 100%;
  animation: shimmer 1.8s ease-in-out infinite;

  &--delayed {
    animation-delay: 0.2s;
  }

  &--short {
    height: 48px;
    width: 100%;
    animation-delay: 0.4s;
  }
}

@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

// Responsive: stack vertically on mobile
@media (max-width: $breakpoint-md) {
  .login-page {
    flex-direction: column-reverse;
  }

  .login-gradient {
    flex: 0 0 40vh;
    min-height: 40vh;
  }

  .login-form-panel {
    flex: 1;
    padding: $spacing-lg;

    &::before {
      display: none;
    }
  }

  .form-container {
    border-radius: 12px;
    padding: $spacing-lg;
  }

  .brand-title {
    font-size: 3rem;
  }

  .brand-subtitle {
    font-size: 1rem;
  }
}
</style>
