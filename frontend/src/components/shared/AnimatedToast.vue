<template>
  <Teleport to="body">
    <div class="fixed top-4 right-4 z-[100] flex flex-col gap-2 pointer-events-none">
      <TransitionGroup name="toast">
        <div
          v-for="toast in toasts"
          :key="toast.id"
          ref="toastRefs"
          class="pointer-events-auto flex items-center gap-3 px-4 py-3 rounded-xl
                 shadow-xl backdrop-blur-sm border text-sm min-w-[300px] max-w-[420px]"
          :class="toastStyles[toast.type]"
          @click="removeToast(toast.id)"
        >
          <!-- 图标 -->
          <span class="flex-shrink-0 text-lg">
            {{ toastIcons[toast.type] }}
          </span>
          <!-- 消息 -->
          <span class="flex-1 text-white/90">{{ toast.message }}</span>
          <!-- 关闭按钮 -->
          <button class="flex-shrink-0 text-white/40 hover:text-white/80 transition-colors" @click.stop="removeToast(toast.id)">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useUIStore } from '@/stores/ui'

const ui = useUIStore()
const toasts = computed(() => ui.toasts)

function removeToast(id: string) {
  ui.removeToast(id)
}

const toastStyles: Record<string, string> = {
  info:    'bg-surface-800/95 border-surface-600',
  success: 'bg-emerald-900/90 border-emerald-700/50',
  error:   'bg-red-900/90 border-red-700/50',
  warning: 'bg-amber-900/90 border-amber-700/50',
}

const toastIcons: Record<string, string> = {
  info:    'ℹ️',
  success: '✅',
  error:   '❌',
  warning: '⚠️',
}
</script>

<style scoped>
/* Vue Transition — Anime.js 手动接管 */
.toast-enter-active {
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}
.toast-enter-from {
  opacity: 0;
  transform: translateX(60px) scale(0.9);
}
.toast-leave-active {
  transition: all 0.2s cubic-bezier(0.55, 0, 1, 0.45);
}
.toast-leave-to {
  opacity: 0;
  transform: translateX(80px) scale(0.85);
}
</style>
