/**
 * Anime.js v3 → v4 API 适配层
 *
 * anime.js v4.4.1 改变了 API 签名和参数命名：
 *   v3:  animate({ targets, opacity: [0,1], easing: 'easeOutCubic', complete: fn })
 *   v4:  animate(targets, { opacity: [0,1], ease: 'easeOutCubic', onComplete: fn })
 *
 * 这个适配器接收 v3 风格的调用，自动转换为 v4 调用。
 */

import {
  animate as animeV4,
  stagger as animeStaggerV4,
  createTimeline as animeCreateTimelineV4,
} from 'animejs'

// ── 参数名映射：v3 → v4 ──
const PARAM_MAP: Record<string, string> = {
  easing: 'ease',
  complete: 'onComplete',
  begin: 'onBegin',
  update: 'onUpdate',
  loopBegin: 'onLoop',
  loopComplete: 'onLoopComplete',
}

// 处理 v3 → v4 参数转换
function convertParams(params: Record<string, any>): Record<string, any> {
  const converted: Record<string, any> = {}
  for (const [key, value] of Object.entries(params)) {
    const newKey = PARAM_MAP[key] || key

    // direction: 'alternate' → alternate: true
    if (key === 'direction') {
      if (value === 'alternate') {
        converted.alternate = true
      }
      continue
    }

    // targets 不作为参数传递（v4 中单独传递）
    if (key === 'targets') continue

    converted[newKey] = value
  }
  return converted
}

/**
 * v3 兼容的 animate 函数
 *
 * 用法（v3 风格）:
 *   animate({ targets: el, opacity: [0, 1], duration: 400, easing: 'easeOutCubic' })
 */
export function animate(
  targetsOrParams: any,
  maybeParams?: Record<string, any>,
): ReturnType<typeof animeV4> {
  // v4 风格：两个参数 → 直接透传
  if (maybeParams !== undefined) {
    return animeV4(targetsOrParams, maybeParams)
  }

  const params = targetsOrParams

  // v3 风格：单对象参数 → 分离 targets 和其余属性，转换参数名
  const { targets, ...rest } = params || {}
  const converted = convertParams(params)

  if (!targets) {
    return animeV4(targets, converted as any)
  }

  return animeV4(targets, converted as any)
}

/**
 * v3 兼容的 stagger 函数 — 直接透传
 */
export function stagger(
  val: number | string | [number, number] | [string, string],
  params?: Record<string, any>,
): (target: any, i: number, targets: any[], prevTween: any, tl: any) => number {
  return animeStaggerV4(val, params)
}

/**
 * v3 兼容的 createTimeline 函数 — 直接透传
 */
export function createTimeline(
  parameters?: Record<string, any>,
): ReturnType<typeof animeCreateTimelineV4> {
  return animeCreateTimelineV4(parameters)
}

// 重新导出类型
export type { AnimationParams, JSAnimation } from 'animejs'
