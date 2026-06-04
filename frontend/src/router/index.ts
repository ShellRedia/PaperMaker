import { createRouter, createWebHashHistory } from 'vue-router'

const router = createRouter({
  // 使用 Hash History — PyInstaller 环境下更稳定
  history: createWebHashHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomeView.vue'),
    },
    {
      path: '/document/:id?',
      name: 'document',
      component: () => import('@/views/DocumentView.vue'),
    },
    {
      path: '/annotation/:docId',
      name: 'annotation',
      component: () => import('@/views/AnnotationView.vue'),
    },
    {
      path: '/statistics/:docId',
      name: 'statistics',
      component: () => import('@/views/StatisticsView.vue'),
    },
    {
      path: '/polish/:docId',
      name: 'polish',
      component: () => import('@/views/PolishView.vue'),
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('@/views/SettingsView.vue'),
    },
  ],
})

export default router
