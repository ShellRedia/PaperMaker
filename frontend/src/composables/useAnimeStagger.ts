import { ref, onMounted, type Ref } from 'vue'
import { animate, stagger } from '@/composables/animeAdapter'

export type StaggerFrom = 'bottom' | 'left' | 'right' | 'scale' | 'none'

export interface StaggerOptions {
  from?: StaggerFrom
  duration?: number
  staggerDelay?: number
  easing?: string
  triggerOnce?: boolean
}

export function useAnimeStagger(
  containerRef: Ref<HTMLElement | null>,
  itemSelector: string,
  options: StaggerOptions = {},
) {
  const hasPlayed = ref(false)
  const {
    from = 'bottom',
    duration = 500,
    staggerDelay = 60,
    easing = 'easeOutCubic',
  } = options

  const play = () => {
    const container = containerRef.value
    if (!container) return

    const items = container.querySelectorAll(itemSelector)
    if (items.length === 0) return

    const animParams: Record<string, any> = {
      duration,
      delay: stagger(staggerDelay),
      easing,
    }

    switch (from) {
      case 'bottom':
        animParams.translateY = [24, 0]
        animParams.opacity = [0, 1]
        break
      case 'left':
        animParams.translateX = [-20, 0]
        animParams.opacity = [0, 1]
        break
      case 'right':
        animParams.translateX = [20, 0]
        animParams.opacity = [0, 1]
        break
      case 'scale':
        animParams.scale = [0.85, 1]
        animParams.opacity = [0, 1]
        break
      case 'none':
        animParams.opacity = [0, 1]
        break
    }

    animate({
      targets: items,
      ...animParams,
    })

    hasPlayed.value = true
  }

  return { play, hasPlayed }
}
