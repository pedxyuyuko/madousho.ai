import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  // Proxy API requests to FastAPI backend
  server: {
    proxy: {
      '/api/v1': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  },
  // Build output to public/ directory (served by FastAPI)
  build: {
    outDir: '../public',
    emptyOutDir: true,
  },
  // SCSS configuration
  css: {
    preprocessorOptions: {
      scss: {
        // Global SCSS variables will be imported automatically
        additionalData: `@use "@/assets/scss/_variables" as *;`
      }
    }
  }
})
