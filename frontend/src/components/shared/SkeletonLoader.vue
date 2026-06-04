<template>
  <div
    ref="skeletonRef"
    class="anim-skeleton rounded"
    :style="{ width, height }"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useUIStore } from '@/stores/ui'

withDefaults(defineProps<{
  width?: string
  height?: string
}>(), {
  width: '100%',
  height: '16px',
})

const skeletonRef = ref<HTMLElement | null>(null)
</script>
