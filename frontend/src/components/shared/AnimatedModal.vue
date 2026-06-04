<template>
  <Teleport to="body">
    <Transition name="modal" @before-enter="onBeforeEnter" @enter="onEnter" @leave="onLeave">
      <div v-if="visible" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <!-- 遮罩层 -->
        <div
          ref="overlayRef"
          class="absolute inset-0 bg-black/60 backdrop-blur-sm"
          @click="closeOnOverlay && $emit('close')"
        />
        <!-- 内容 -->
        <div
          ref="panelRef"
          class="relative z-10 bg-surface-800 border border-surface-600 rounded-2xl shadow-2xl
                 max-h-[85vh] overflow-auto"
          :class="sizeClasses[size]"
        >
          <!-- 标题栏 -->
          <div v-if="title || $slots.header" class="flex items-center justify-between px-6 py-4 border-b border-surface-700">
            <h3 class="text-lg font-semibold text-white">
              <slot name="header">{{ title }}</slot>
            </h3>
            <button
              class="p-1 rounded-lg hover:bg-surface-700 text-surface-400 hover:text-white transition-colors"
              @click="$emit('close')"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <!-- 内容 -->
          <div :class="['p-6', noPadding && '!p-0']">
            <slot />
          </div>
          <!-- 底部 -->
          <div v-if="$slots.footer" class="px-6 py-4 border-t border-surface-700 flex justify-end gap-3">
            <slot name="footer" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { animate } from '@/composables/animeAdapter'

withDefaults(defineProps<{
  visible?: boolean
  title?: string
  size?: 'sm' | 'md' | 'lg' | 'xl'
  closeOnOverlay?: boolean
  noPadding?: boolean
}>(), {
  visible: false,
  size: 'md',
  closeOnOverlay: true,
  noPadding: false,
})

defineEmits<{
  close: []
}>()

const overlayRef = ref<HTMLElement | null>(null)
const panelRef = ref<HTMLElement | null>(null)

const sizeClasses: Record<string, string> = {
  sm: 'w-[360px]',
  md: 'w-[480px]',
  lg: 'w-[640px]',
  xl: 'w-[860px]',
}

function onBeforeEnter() { /* Vue transition hook */ }

function onEnter(el: Element) {
  const panel = (el as HTMLElement).querySelector('.relative.z-10') as HTMLElement
  const overlay = (el as HTMLElement).querySelector('.absolute.inset-0') as HTMLElement

  // 遮罩淡入
  if (overlay) {
    animate({ targets: overlay, opacity: [0, 1], duration: 300, easing: 'easeOutQuad' })
  }
  // 面板弹簧弹入
  if (panel) {
    animate({
      targets: panel,
      scale: [0.88, 1],
      opacity: [0, 1],
      translateY: [20, 0],
      duration: 500,
      easing: 'easeOutBack(1.4)',
    })
  }
}

function onLeave(el: Element) {
  const panel = (el as HTMLElement).querySelector('.relative.z-10') as HTMLElement
  const overlay = (el as HTMLElement).querySelector('.absolute.inset-0') as HTMLElement

  if (panel) {
    animate({
      targets: panel,
      scale: [1, 0.92],
      opacity: [1, 0],
      translateY: [0, -10],
      duration: 200,
      easing: 'easeInCubic',
    })
  }
  if (overlay) {
    animate({ targets: overlay, opacity: [1, 0], duration: 200, easing: 'easeInCubic' })
  }
}
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: none; /* Anime.js 手动控制 */
}
</style>
