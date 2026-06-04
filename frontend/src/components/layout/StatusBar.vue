<template>
  <footer
    class="flex items-center justify-between h-7 px-3
           bg-surface-900 border-t border-surface-700/50 text-xs
           text-surface-500 select-none shrink-0"
  >
    <!-- 左侧: 状态消息 -->
    <div class="flex items-center gap-2">
      <span
        class="inline-block w-2 h-2 rounded-full"
        :class="statusColor"
      />
      <span>{{ statusText }}</span>
    </div>

    <!-- 右侧: 快捷信息 -->
    <div class="flex items-center gap-4">
      <!-- 模型推理状态 -->
      <span v-if="modelStore.isStreaming" class="flex items-center gap-1 text-primary-400 anim-breathe">
        <svg class="w-3 h-3 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
        推理中 {{ Math.round(modelStore.streamProgress * 100) }}%
      </span>

      <!-- 动画状态 -->
      <button
        class="hover:text-surface-300 transition-colors"
        :class="{ 'text-primary-400': ui.animEnabled }"
        title="切换动画"
        @click="ui.toggleAnim()"
      >
        {{ ui.animEnabled ? '🎬 动画' : '⏸ 动画' }}
      </button>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useUIStore } from '@/stores/ui'
import { useModelStore } from '@/stores/model'

const ui = useUIStore()
const modelStore = useModelStore()

const statusText = computed(() => {
  if (modelStore.isStreaming) return '模型推理中...'
  return '就绪'
})

const statusColor = computed(() => {
  if (modelStore.isStreaming) return 'bg-primary-400 anim-pulse-glow'
  return 'bg-emerald-400'
})
</script>
