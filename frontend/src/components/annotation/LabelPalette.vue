<template>
  <div ref="paletteRef" class="flex items-center gap-2">
    <span class="text-sm text-surface-500">标签:</span>

    <!-- 预设标签按钮组 -->
    <div class="flex items-center gap-1">
      <button
        v-for="label in presetLabels"
        :key="label.name"
        class="px-2.5 py-1 rounded-lg text-xs font-medium
               transition-all duration-200 border"
        :style="labelStyle(label)"
        :class="modelValue === label.name
          ? 'ring-2 ring-offset-1 ring-offset-surface-800 border-transparent'
          : 'border-transparent hover:scale-105'"
        @click="$emit('update:modelValue', label.name); $emit('update:color', label.color)"
      >
        {{ label.label }}
      </button>
    </div>

    <!-- 自定义颜色选择器 -->
    <input
      type="color"
      :value="color"
      class="w-7 h-7 rounded cursor-pointer border-0 bg-transparent"
      @input="$emit('update:color', ($event.target as HTMLInputElement).value)"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAnimeStagger } from '@/composables/useAnimeStagger'
import type { StaggerFrom } from '@/composables/useAnimeStagger'

const props = defineProps<{
  modelValue: string
  color: string
}>()

defineEmits<{
  'update:modelValue': [value: string]
  'update:color': [value: string]
}>()

const paletteRef = ref<HTMLElement | null>(null)

const presetLabels = [
  { name: 'default', label: '默认', color: '#3B82F6' },
  { name: 'important', label: '重点', color: '#EF4444' },
  { name: 'method', label: '方法', color: '#22C55E' },
  { name: 'result', label: '结果', color: '#F59E0B' },
  { name: 'reference', label: '引用', color: '#8B5CF6' },
  { name: 'note', label: '笔记', color: '#EC4899' },
]

function labelStyle(label: { name: string; color: string }) {
  if (props.modelValue === label.name) {
    return {
      backgroundColor: label.color + '25',
      color: label.color,
      borderColor: label.color,
      boxShadow: `0 0 8px ${label.color}40`,
    }
  }
  return {
    backgroundColor: label.color + '10',
    color: label.color,
    borderColor: 'transparent',
  }
}

// Anime.js Stagger 动画
const { play } = useAnimeStagger(paletteRef, 'button', {
  from: 'scale',
  duration: 350,
  staggerDelay: 40,
})

onMounted(() => play())
</script>
