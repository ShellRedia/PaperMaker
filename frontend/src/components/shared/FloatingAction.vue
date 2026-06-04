<template>
  <button
    ref="fabRef"
    class="fixed z-40 flex items-center justify-center
           bg-primary-500 hover:bg-primary-600 active:bg-primary-500
           text-white rounded-2xl shadow-xl shadow-primary-500/30
           hover:shadow-primary-500/40 transition-shadow duration-200"
    :class="sizeClasses[size]"
    :style="{ bottom: offset + 'px', right: offset + 'px' }"
    @click="$emit('click')"
    v-anime:fadeInScale
  >
    <slot>
      <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
      </svg>
    </slot>
  </button>
</template>

<script setup lang="ts">
import { ref } from 'vue'

withDefaults(defineProps<{
  size?: 'md' | 'lg'
  offset?: number
}>(), {
  size: 'md',
  offset: 24,
})

defineEmits<{
  click: [e: MouseEvent]
}>()

const fabRef = ref<HTMLElement | null>(null)

const sizeClasses: Record<string, string> = {
  md: 'w-14 h-14',
  lg: 'w-16 h-16',
}
</script>
