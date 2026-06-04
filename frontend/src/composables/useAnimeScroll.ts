import { ref, onMounted, onUnmounted, type Ref } from 'vue'
import { animate } from '@/composables/animeAdapter'

export interface ScrollAnimationOptions {
  /** 触发阈值 (0-1), 默认 0.15 */
  threshold?: number
  /** 是否只触发一次 */
  once?: boolean
  /** 进入时的动画参数 */
  enterParams?: Record<string, any>
  /** 离开时的动画参数 (如果不想要反向动画则不传) */
  leaveParams?: Record<string, any>
}

export function useAnimeScroll(
  targetRef: Ref<HTMLElement | null>,
  options: ScrollAnimationOptions = {},
) {
  const isVisible = ref(false)
  const hasPlayed = ref(false)
  let observer: IntersectionObserver | null = null

  const {
    threshold = 0.15,
    once = true,
    enterParams = {},
    leaveParams,
  } = options

  const playEnter = () => {
    if (!targetRef.value) return
    animate({
      targets: targetRef.value,
      opacity: [0, 1],
      translateY: [30, 0],
      duration: 600,
      easing: 'easeOutCubic',
      ...enterParams,
    })
    isVisible.value = true
    hasPlayed.value = true
  }

  const playLeave = () => {
    if (!targetRef.value || !leaveParams) return
    animate({
      targets: targetRef.value,
      ...leaveParams,
    })
    isVisible.value = false
  }

  onMounted(() => {
    if (!targetRef.value) return

    observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          if (!once || !hasPlayed.value) {
            playEnter()
          }
        } else {
          playLeave()
        }
      },
      { threshold },
    )

    observer.observe(targetRef.value)
  })

  onUnmounted(() => {
    observer?.disconnect()
  })

  return { isVisible, hasPlayed, playEnter, playLeave }
}
