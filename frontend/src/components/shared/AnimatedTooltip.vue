<template>
  <div
    ref="tooltipRef"
    class="absolute z-50 px-3 py-1.5 rounded-lg text-xs font-medium
           bg-surface-700 text-white/90 border border-surface-600 shadow-xl
           whitespace-nowrap pointer-events-none"
    :style="{ top: y + 'px', left: x + 'px' }"
  >
    {{ text }}
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { animate } from '@/composables/animeAdapter'

defineProps<{
  text: string
  x: number
  y: number
}>()

const tooltipRef = ref<HTMLElement | null>(null)

onMounted(() => {
  if (tooltipRef.value) {
    animate({
      targets: tooltipRef.value,
      opacity: [0, 1],
      translateY: [4, 0],
      duration: 200,
      easing: 'easeOutQuad',
    })
  }
})
</script>
