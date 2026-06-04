import type { Directive } from 'vue'
import { animate } from '@/composables/animeAdapter'

/**
 * v-anime 自定义指令
 *
 * 声明式动画绑定:
 *   <div v-anime:fadeIn>              → 使用预设
 *   <div v-anime:fadeIn.visible>      → IntersectionObserver 触发
 *   <div v-anime:fadeIn="{ delay: 500 }"> → 自定义参数覆盖
 *
 * 可用预设:
 *   fadeIn, fadeInUp, fadeInDown, fadeInScale,
 *   slideInLeft, slideInRight, pulse, shake
 */

const PRESETS: Record<string, AnimationParams> = {
  fadeIn:       { opacity: [0, 1], duration: 400, easing: 'easeOutQuad' },
  fadeInUp:     { opacity: [0, 1], translateY: [20, 0], duration: 500, easing: 'easeOutCubic' },
  fadeInDown:   { opacity: [0, 1], translateY: [-20, 0], duration: 500, easing: 'easeOutCubic' },
  fadeInScale:  { opacity: [0, 1], scale: [0.9, 1], duration: 600, easing: 'easeOutBack(1.5)' },
  slideInLeft:  { translateX: [-40, 0], opacity: [0, 1], duration: 500, easing: 'easeOutCubic' },
  slideInRight: { translateX: [40, 0], opacity: [0, 1], duration: 500, easing: 'easeOutCubic' },
  pulse:        { scale: [1, 1.05, 1], duration: 300, easing: 'easeInOutQuad' },
  shake:        { translateX: [0, -8, 8, -6, 6, -3, 3, 0], duration: 500, easing: 'easeInOutQuad' },
}

export const vAnime: Directive<HTMLElement, string | Record<string, any>> = {
  mounted(el, binding) {
    const presetName = binding.arg || 'fadeIn'
    const preset = PRESETS[presetName] || PRESETS.fadeIn

    const extraParams = binding.value && typeof binding.value === 'object'
      ? binding.value
      : {}

    const merged = { targets: el, ...preset, ...extraParams }

    // .visible 修饰符 → IntersectionObserver
    if (binding.modifiers.visible) {
      const observer = new IntersectionObserver(
        ([entry]) => {
          if (entry.isIntersecting) {
            animate(merged)
            observer.unobserve(el)
          }
        },
        { threshold: 0.1 },
      )
      observer.observe(el)
      ;(el as any).__animeObserver = observer
    } else {
      animate(merged)
    }
  },

  unmounted(el) {
    ;(el as any).__animeObserver?.disconnect()
  },
}
