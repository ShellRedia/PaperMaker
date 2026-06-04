import { ref, onMounted, onUnmounted, watch, type Ref } from 'vue'
import { animate } from '@/composables/animeAdapter'
import type { AnimationParams, JSAnimation } from 'animejs'

export interface UseAnimeOptions {
  /** 是否创建后立即播放，默认 true */
  immediate?: boolean
  /** 响应式依赖数组，变化时重创建动画 */
  watchDeps?: Ref<any>[]
}

export function useAnime(
  targetRef: Ref<HTMLElement | SVGElement | null>,
  paramsFn: () => AnimationParams,
  options: UseAnimeOptions = {},
) {
  const instance = ref<JSAnimation | null>(null)
  let cleanup: (() => void) | null = null

  const create = () => {
    const el = targetRef.value
    if (!el) return

    instance.value?.pause()
    const params = paramsFn()
    instance.value = animate({
      targets: el,
      autoplay: false,
      ...params,
    })
  }

  const play = () => { instance.value?.play() }
  const pause = () => { instance.value?.pause() }
  const restart = () => { instance.value?.restart(); instance.value?.play() }
  const reverse = () => { instance.value?.reverse() }
  const seek = (t: number) => { instance.value?.seek(t) }
  const finish = () => { instance.value?.finish() }
  const isPlaying = () => instance.value?.began && !instance.value?.completed

  onMounted(() => {
    create()
    if (options.immediate !== false) play()
  })

  // 响应式依赖监听
  if (options.watchDeps?.length) {
    const stop = watch(options.watchDeps, () => {
      create()
      play()
    })
    cleanup = stop
  }

  onUnmounted(() => {
    instance.value?.pause()
    cleanup?.()
  })

  return {
    instance,
    play, pause, restart, reverse, seek, finish, isPlaying,
  }
}
