<template>
  <div class="h-full overflow-auto p-4">
    <SectionOutline :sections="sections" />
  </div>
</template>

<script setup lang="ts">
import SectionOutline from '@/components/editor/SectionOutline.vue'

defineProps<{
  sections: any[]
}>()
</script>
