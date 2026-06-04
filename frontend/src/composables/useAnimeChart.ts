import { ref, shallowRef, onMounted, onUnmounted, watch, type Ref } from 'vue'
import * as echarts from 'echarts'
import type { EChartsOption } from 'echarts'
import { animate } from '@/composables/animeAdapter'

export function useAnimeChart(
  containerRef: Ref<HTMLElement | null>,
  option: Ref<EChartsOption>,
) {
  const chartInstance = shallowRef<echarts.ECharts | null>(null)
  const isReady = ref(false)

  /** 图表面板 Mount 动画: scale + opacity 弹入 */
  const mountAnimation = () => {
    if (!containerRef.value) return
    animate({
      targets: containerRef.value,
      scale: [0.92, 1],
      opacity: [0, 1],
      duration: 600,
      easing: 'easeOutCubic',
    })
    isReady.value = true
  }

  /** 数据更新时容器闪烁指示 */
  const flashUpdate = () => {
    if (!containerRef.value) return
    animate({
      targets: containerRef.value,
      boxShadow: [
        '0 0 0 0 rgba(59, 130, 246, 0)',
        '0 0 20px 4px rgba(59, 130, 246, 0.3)',
        '0 0 0 0 rgba(59, 130, 246, 0)',
      ],
      duration: 1200,
      easing: 'easeOutQuad',
    })
  }

  /** 设置/更新图表配置 */
  const setOption = (newOption: EChartsOption, flash = true) => {
    if (!chartInstance.value) return
    chartInstance.value.setOption(newOption, { notMerge: false })
    if (flash) flashUpdate()
  }

  /** 调整图表大小 */
  const resize = () => {
    chartInstance.value?.resize()
  }

  onMounted(() => {
    if (!containerRef.value) return

    chartInstance.value = echarts.init(containerRef.value, undefined, {
      renderer: 'canvas',
    })

    chartInstance.value.setOption(option.value)
    mountAnimation()

    // 监听容器大小变化
    const ro = new ResizeObserver(() => {
      chartInstance.value?.resize()
    })
    ro.observe(containerRef.value)

    onUnmounted(() => {
      ro.disconnect()
      chartInstance.value?.dispose()
    })
  })

  // 监听 option 变化
  watch(option, (newVal) => {
    if (newVal) setOption(newVal)
  }, { deep: true })

  return {
    chartInstance,
    isReady,
    setOption,
    resize,
    mountAnimation,
    flashUpdate,
  }
}
