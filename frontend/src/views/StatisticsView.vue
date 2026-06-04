<template>
  <div ref="pageRef" class="h-full overflow-auto p-6">
    <div class="max-w-5xl mx-auto space-y-6">
      <h1 class="text-2xl font-bold text-white">统计图表</h1>

      <div v-if="!docId || docId === 'statistics'" class="text-center py-20">
        <div class="text-5xl mb-4">📊</div>
        <p class="text-surface-400 mb-4">请从文档页面打开统计功能</p>
        <AnimatedButton variant="primary" @click="router.push('/document')">
          前往文档
        </AnimatedButton>
      </div>

      <template v-else>
        <!-- 数字指标卡片 -->
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div
            v-for="(metric, i) in metricCards"
            :key="metric.label"
            v-anime:fadeInScale
            class="bg-surface-800 border border-surface-700 rounded-xl p-5 text-center"
            :style="{ animationDelay: i * 80 + 'ms' }"
          >
            <div class="text-3xl font-bold text-white mb-1">
              <span ref="countRefs">{{ metric.value }}</span>
            </div>
            <div class="text-sm text-surface-400">{{ metric.label }}</div>
          </div>
        </div>

        <!-- 图表面板 -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- 词频柱状图 -->
          <ChartPanel
            title="术语频率 Top 10"
            :option="barChartOption"
          />

          <!-- 可读性仪表盘 -->
          <ChartPanel
            title="可读性评分"
            :option="gaugeChartOption"
          />
        </div>

        <!-- 术语列表 -->
        <div class="bg-surface-800 border border-surface-700 rounded-xl p-5">
          <h3 class="text-white font-semibold mb-4">高频术语</h3>
          <div class="flex flex-wrap gap-2">
            <span
              v-for="term in terms"
              :key="term.term"
              class="px-3 py-1.5 rounded-lg text-sm
                     bg-surface-700 text-surface-300
                     hover:bg-primary-500/20 hover:text-primary-400
                     transition-colors duration-200 cursor-default"
            >
              {{ term.term }}
              <span class="text-xs text-surface-500 ml-1">{{ term.count }}</span>
            </span>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { statisticsApi, type DocumentStats, type TermFrequency, type ReadabilityScore } from '@/services/endpoints/statistics'
import AnimatedButton from '@/components/shared/AnimatedButton.vue'
import ChartPanel from '@/components/charts/ChartPanel.vue'
import type { EChartsOption } from 'echarts'

const route = useRoute()
const router = useRouter()

const pageRef = ref<HTMLElement | null>(null)
const countRefs = ref<HTMLElement[]>([])
const stats = ref<DocumentStats | null>(null)
const readability = ref<ReadabilityScore | null>(null)
const terms = ref<TermFrequency[]>([])

const docId = computed(() => route.params.docId as string | undefined)

const metricCards = computed(() => {
  if (!stats.value) return []
  return [
    { label: '总词数', value: stats.value.word_count },
    { label: '句子数', value: stats.value.sentence_count },
    { label: '段落数', value: stats.value.paragraph_count },
    { label: '平均句长', value: stats.value.avg_sentence_length },
  ]
})

const barChartOption = computed<EChartsOption>(() => ({
  tooltip: { trigger: 'axis' },
  xAxis: {
    type: 'category',
    data: terms.value.slice(0, 10).map(t => t.term),
    axisLabel: { color: '#94a3b8', fontSize: 11 },
  },
  yAxis: { type: 'value', axisLabel: { color: '#94a3b8' } },
  series: [{
    type: 'bar',
    data: terms.value.slice(0, 10).map(t => t.count),
    itemStyle: {
      color: {
        type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
        colorStops: [
          { offset: 0, color: '#3b82f6' },
          { offset: 1, color: '#1d4ed8' },
        ],
      },
      borderRadius: [6, 6, 0, 0],
    },
    animationDuration: 800,
    animationEasing: 'cubicOut' as any,
  }],
}))

const gaugeChartOption = computed<EChartsOption>(() => ({
  series: [{
    type: 'gauge',
    startAngle: 210,
    endAngle: -30,
    min: 0,
    max: 100,
    progress: {
      show: true,
      width: 12,
      itemStyle: { color: '#3b82f6' },
      roundCap: true,
    },
    axisLine: { lineStyle: { width: 12, color: [[1, '#1e293b']] } },
    axisTick: { show: false },
    splitLine: { show: false },
    axisLabel: { show: false },
    detail: {
      valueAnimation: true,
      formatter: '{value}',
      color: '#fff',
      fontSize: 28,
      offsetCenter: [0, '60%'],
    },
    title: {
      offsetCenter: [0, '85%'],
      color: '#94a3b8',
      fontSize: 13,
    },
    data: [{
      value: readability.value?.flesch_reading_ease ?? 0,
      name: 'Flesch 可读性',
    }],
  }],
}))

onMounted(async () => {
  const id = docId.value
  if (id && id !== 'statistics') {
    try {
      stats.value = await statisticsApi.getStats(id)
      readability.value = await statisticsApi.getReadability(id)
      terms.value = await statisticsApi.getTerms(id, 30)
    } catch (e) {
      console.error('Failed to load statistics:', e)
    }
  }
})
</script>
