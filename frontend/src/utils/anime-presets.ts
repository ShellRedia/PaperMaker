/**
 * Anime.js 预定义动画参数集
 *
 * 集中管理项目中所有可复用的动画参数，
 * 确保动画风格统一。通过 CSS 变量实现运行时调整。
 */

import type { AnimationParams } from 'animejs'

// ── 从 CSS 变量读取动画参数 ──
const cssVar = (name: string, fallback: string): string => {
  if (typeof document === 'undefined') return fallback
  return getComputedStyle(document.documentElement).getPropertyValue(name) || fallback
}

const DURATION_SLOW = parseInt(cssVar('--anime-duration-slow', '800'))
const DURATION_NORMAL = parseInt(cssVar('--anime-duration-normal', '500'))
const DURATION_FAST = parseInt(cssVar('--anime-duration-fast', '250'))

// ── 预设集 ──
export const animePresets = {
  /** 页面进入 */
  pageEnter: {
    opacity: [0, 1],
    translateY: [16, 0],
    duration: DURATION_NORMAL,
    easing: 'easeOutCubic',
  } as AnimationParams,

  /** Modal / Dialog 弹簧弹入 */
  modalEnter: {
    scale: [0.85, 1],
    opacity: [0, 1],
    duration: DURATION_NORMAL,
    easing: 'easeOutBack(1.5)',
  } as AnimationParams,

  /** Modal / Dialog 退出 */
  modalExit: {
    scale: [1, 0.9],
    opacity: [1, 0],
    duration: DURATION_FAST,
    easing: 'easeInCubic',
  } as AnimationParams,

  /** Toast 消息滑入 */
  toastEnter: {
    translateX: [80, 0],
    opacity: [0, 1],
    duration: DURATION_FAST,
    easing: 'easeOutCubic',
  } as AnimationParams,

  /** Toast 消息滑出 */
  toastExit: {
    translateX: [0, 80],
    opacity: [1, 0],
    duration: DURATION_FAST,
    easing: 'easeInCubic',
  } as AnimationParams,

  /** 列表项逐条动画 */
  listItem: {
    opacity: [0, 1],
    translateY: [20, 0],
    duration: DURATION_NORMAL,
    easing: 'easeOutCubic',
  } as AnimationParams,

  /** 骨架屏 → 内容过渡 */
  skeletonToContent: {
    opacity: [0, 1],
    duration: DURATION_SLOW,
    easing: 'easeOutQuad',
  } as AnimationParams,

  /** 推理进度指示器脉冲 */
  inferencePulse: {
    scale: [1, 1.04],
    duration: 800,
    direction: 'alternate',
    loop: true,
    easing: 'easeInOutQuad',
  } as AnimationParams,

  /** SVG 连线绘制 */
  pathDraw: {
    strokeDashoffset: [1, 0],
    duration: 1000,
    easing: 'easeInOutQuad',
  } as AnimationParams,

  /** 侧边栏展开 */
  sidebarExpand: {
    width: [64, 260],
    duration: DURATION_NORMAL,
    easing: 'easeOutCubic',
  } as AnimationParams,

  /** 侧边栏折叠 */
  sidebarCollapse: {
    width: [260, 64],
    duration: DURATION_NORMAL,
    easing: 'easeInCubic',
  } as AnimationParams,

  /** 数值递增动画 (用于统计面板) */
  countUp: (target: any, from: number, to: number, duration: number = 1200): AnimationParams => ({
    targets: target,
    innerHTML: [from, to],
    duration,
    round: 1,
    easing: 'easeOutExpo',
  }),

  /** 按钮 Ripple */
  ripple: (targets: any, x: number, y: number): AnimationParams => ({
    targets,
    scale: [0, 2.5],
    opacity: [0.5, 0],
    left: x,
    top: y,
    duration: 600,
    easing: 'easeOutExpo',
  }),
} as const
