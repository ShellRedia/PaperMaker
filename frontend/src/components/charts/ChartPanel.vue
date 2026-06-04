<template>
  <div
    ref="panelRef"
    class="bg-surface-800 border border-surface-700 rounded-xl overflow-hidden"
  >
    <!-- 标题栏 -->
    <div class="flex items-center justify-between px-5 py-3 border-b border-surface-700/50">
      <h3 class="text-sm font-semibold text-white">{{ title }}</h3>
      <span class="text-xs text-surface-500">
        {{ subtitle }}
      </span>
    </div>
    <!-- 图表容器 -->
    <div ref="chartRef" class="w-full" :style="{ height: chartHeight + 'px' }" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import type { EChartsOption } from 'echarts'
import { useAnimeChart } from '@/composables/useAnimeChart'

const props = withDefaults(defineProps<{
  title?: string
  subtitle?: string
  option: EChartsOption
  chartHeight?: number
}>(), {
  title: '图表',
  chartHeight: 300,
})

const panelRef = ref<HTMLElement | null>(null)
const chartRef = ref<HTMLElement | null>(null)

// 使用 Anime.js + ECharts 桥接
const optionRef = ref(props.option)
const { setOption, resize } = useAnimeChart(chartRef, optionRef)

watch(() => props.option, (newVal) => {
  optionRef.value = newVal
  setOption(newVal)
}, { deep: true })
</script>
