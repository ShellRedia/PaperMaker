import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export type ThemeMode = 'dark' | 'light'
export type SidebarState = 'expanded' | 'collapsed'

export const useUIStore = defineStore('ui', () => {
  // ── 状态 ──
  const theme = ref<ThemeMode>(
    (localStorage.getItem('papermaker-theme') as ThemeMode) || 'dark'
  )
  const sidebar = ref<SidebarState>('expanded')
  const animEnabled = ref<boolean>(
    localStorage.getItem('papermaker-anim') !== 'false'
  )
  const toasts = ref<Array<{
    id: string
    message: string
    type: 'info' | 'success' | 'error' | 'warning'
    duration: number
  }>>([])

  // ── 持久化 ──
  watch(theme, (v) => localStorage.setItem('papermaker-theme', v))
  watch(animEnabled, (v) => localStorage.setItem('papermaker-anim', String(v)))

  // ── 操作 ──
  function toggleTheme() {
    theme.value = theme.value === 'dark' ? 'light' : 'dark'
    document.documentElement.classList.toggle('light', theme.value === 'light')
  }

  function toggleSidebar() {
    sidebar.value = sidebar.value === 'expanded' ? 'collapsed' : 'expanded'
  }

  function toggleAnim() {
    animEnabled.value = !animEnabled.value
  }

  function addToast(
    message: string,
    type: 'info' | 'success' | 'error' | 'warning' = 'info',
    duration = 3000
  ) {
    const id = `toast_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`
    toasts.value.push({ id, message, type, duration })
    if (duration > 0) {
      setTimeout(() => removeToast(id), duration)
    }
  }

  function removeToast(id: string) {
    toasts.value = toasts.value.filter(t => t.id !== id)
  }

  return {
    theme, sidebar, animEnabled, toasts,
    toggleTheme, toggleSidebar, toggleAnim, addToast, removeToast,
  }
})
