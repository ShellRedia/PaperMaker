<template>
  <button
    ref="btnRef"
    class="relative overflow-hidden inline-flex items-center justify-center gap-2
           px-4 py-2 rounded-lg font-medium text-sm
           transition-colors duration-200 select-none
           focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500/50
           disabled:opacity-50 disabled:cursor-not-allowed disabled:pointer-events-none"
    :class="variantClasses[variant]"
    @click="handleClick"
    @mousedown="handleMouseDown"
  >
    <!-- Ripple 波纹元素 -->
    <span
      v-for="ripple in ripples"
      :key="ripple.id"
      class="absolute rounded-full bg-white/30 pointer-events-none"
      :style="{
        width: ripple.size + 'px',
        height: ripple.size + 'px',
        left: ripple.x + 'px',
        top: ripple.y + 'px',
      }"
    />
    <!-- 图标 -->
    <span v-if="$slots.icon" class="flex-shrink-0">
      <slot name="icon" />
    </span>
    <!-- 文本 -->
    <slot />
  </button>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { animate } from '@/composables/animeAdapter'

const props = withDefaults(defineProps<{
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger'
  disabled?: boolean
}>(), {
  variant: 'primary',
  disabled: false,
})

const emit = defineEmits<{
  click: [e: MouseEvent]
}>()

const btnRef = ref<HTMLElement | null>(null)

interface Ripple {
  id: number
  x: number
  y: number
  size: number
}

const ripples = reactive<Ripple[]>([])
let rippleId = 0

const variantClasses: Record<string, string> = {
  primary:
    'bg-primary-500 text-white hover:bg-primary-600 active:bg-primary-500 ' +
    'shadow-lg shadow-primary-500/25 hover:shadow-primary-500/40',
  secondary:
    'bg-surface-700 text-surface-100 hover:bg-surface-600 active:bg-surface-700 ' +
    'border border-surface-600',
  ghost:
    'bg-transparent text-surface-300 hover:text-white hover:bg-surface-700/50 ' +
    'active:bg-surface-700',
  danger:
    'bg-red-500/20 text-red-400 hover:bg-red-500/30 active:bg-red-500/20 ' +
    'border border-red-500/30',
}

function createRipple(event: MouseEvent) {
  const btn = btnRef.value
  if (!btn) return

  const rect = btn.getBoundingClientRect()
  const size = Math.max(rect.width, rect.height)
  const x = event.clientX - rect.left - size / 2
  const y = event.clientY - rect.top - size / 2

  const id = ++rippleId
  const ripple: Ripple = { id, x, y, size }
  ripples.push(ripple)

  // Anime.js ripple 动画
  const rippleEl = btn.querySelectorAll('.rounded-full.bg-white\\/30')
  const target = rippleEl[rippleEl.length - 1]
  if (target) {
    animate({
      targets: target,
      scale: [0, 1],
      opacity: [0.4, 0],
      duration: 600,
      easing: 'easeOutExpo',
      complete: () => {
        const idx = ripples.findIndex(r => r.id === id)
        if (idx !== -1) ripples.splice(idx, 1)
      },
    })
  }
}

function handleClick(e: MouseEvent) {
  if (props.disabled) return
  emit('click', e)
}

function handleMouseDown(e: MouseEvent) {
  if (props.disabled) return
  createRipple(e)
}
</script>
