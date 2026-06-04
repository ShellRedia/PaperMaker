import { ref, onUnmounted } from 'vue'
import { createTimeline } from '@/composables/animeAdapter'
import type { AnimationParams, JSAnimation } from 'animejs'

export interface TimelineStep {
  targets: any
  params: AnimationParams
  offset?: string | number
}

export function useAnimeTimeline() {
  const timeline = ref<JSAnimation | null>(null)
  const isPlaying = ref(false)

  const create = (steps: TimelineStep[]) => {
    const tl = createTimeline({ autoplay: false })

    steps.forEach((step) => {
      tl.add(
        { targets: step.targets, ...step.params },
        step.offset ?? '+=0',
      )
    })

    timeline.value = tl as unknown as JSAnimation
  }

  const play = () => {
    timeline.value?.play()
    isPlaying.value = true
  }

  const reverse = () => {
    timeline.value?.reverse()
  }

  const pause = () => {
    timeline.value?.pause()
    isPlaying.value = false
  }

  onUnmounted(() => {
    timeline.value?.pause()
  })

  return { timeline, isPlaying, create, play, reverse, pause }
}
