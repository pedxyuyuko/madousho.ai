import { createRouter, createWebHistory } from 'vue-router'
import type { RouteLocationNormalized } from 'vue-router'

// Lazy imports to avoid circular deps
const LoginView = () => import('@/views/LoginView.vue')
const AdminLayout = () => import('@/layouts/AdminLayout.vue')
const HomeView = () => import('@/views/HomeView.vue')

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/login', name: 'login', component: LoginView },
    {
      path: '/',
      component: AdminLayout,
      children: [
        { path: '', name: 'home', component: HomeView },
      ],
    },
  ],
})

router.beforeEach(async (to: RouteLocationNormalized) => {
  const { useAuthStore } = await import('@/stores/auth.store')
  const authStore = useAuthStore()

  if (to.path === '/login' && authStore.isAuthenticated) {
    return { path: '/' }
  }

  if (to.path !== '/login' && !authStore.isAuthenticated) {
    return { path: '/login' }
  }

  return true
})

export default router
