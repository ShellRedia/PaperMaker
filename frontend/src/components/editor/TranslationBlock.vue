<!--
  TranslationBlock.vue — 单个翻译结果块（英文 + 中文回译）
  用于原版翻译和优化变体的统一渲染
-->
<template>
  <div
    class="bg-surface-800/80 border border-surface-700/50 rounded-2xl rounded-bl-md overflow-hidden"
    :class="{ 'border-cyan-500/30': label }"
  >
    <!-- 头部 -->
    <div class="flex items-center justify-between px-4 py-2 bg-surface-700/30 border-b border-surface-700/50">
      <div class="flex items-center gap-2">
        <span
          v-if="label"
          class="text-xs px-1.5 py-0.5 rounded-full border"
          :class="labelClass || 'bg-amber-500/20 text-amber-400 border-amber-500/30'"
        >
          {{ label }}
        </span>
        <span class="text-xs font-semibold text-primary-400 uppercase tracking-wider">
          {{ englishLabel || '🇬🇧 English' }}
        </span>
      </div>
      <div class="flex items-center gap-1">
        <!-- 流式指示器 -->
        <span
          v-if="streaming"
          class="flex items-center gap-1 text-xs text-amber-400"
        >
          <span class="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />
          生成中...
        </span>
        <!-- Token 用量 -->
        <span
          v-if="usage && usage.total_tokens"
          class="text-xs text-surface-500 font-mono"
          :title="`prompt: ${usage.prompt_tokens} · completion: ${usage.completion_tokens}`"
        >
          🔢 {{ usage.total_tokens }} tokens
        </span>
        <!-- 优化按钮 -->
        <template v-if="showRefineButtons">
          <AnimatedButton
            variant="ghost"
            size="xs"
            title="精简表达 — 去除冗余使翻译更简洁"
            @click="$emit('refine', 'concise')"
          >
            ✂️ 精简
          </AnimatedButton>
          <AnimatedButton
            variant="ghost"
            size="xs"
            title="学术化 — 提升措辞使其更符合期刊论文风格"
            @click="$emit('refine', 'academic')"
          >
            🎓 学术化
          </AnimatedButton>
        </template>
        <!-- 复制按钮 -->
        <AnimatedButton
          v-if="showCopy"
          variant="ghost"
          size="xs"
          @click="$emit('copyEnglish')"
        >
          📋 复制
        </AnimatedButton>
        <!-- 已优化标记 -->
        <span
          v-if="refineDoneModes && refineDoneModes.length > 0"
          class="text-xs text-surface-500"
        >
          {{ refineDoneModes.map(m => m === 'concise' ? '✂️' : m === 'academic' ? '🎓' : '').join(' ') }}
        </span>
      </div>
    </div>

    <!-- 英文内容 -->
    <div class="px-4 py-3">
      <p
        class="text-sm leading-relaxed whitespace-pre-wrap break-words"
        :class="english ? 'text-white font-mono' : 'text-surface-600'"
        v-text="english || '…'"
      />
    </div>

    <!-- 中文回译 -->
    <div
      v-if="chinese"
      class="border-t border-surface-700/50 px-4 py-3 bg-surface-800/40"
    >
      <div class="flex items-center justify-between mb-1.5">
        <span class="text-xs font-semibold text-emerald-400 uppercase tracking-wider">
          {{ chineseLabel || '🇨🇳 回译中文' }}
        </span>
        <AnimatedButton
          v-if="showCopy"
          variant="ghost"
          size="xs"
          @click="$emit('copyChinese')"
        >
          📋 复制
        </AnimatedButton>
      </div>
      <p
        class="text-sm text-surface-300 leading-relaxed whitespace-pre-wrap break-words"
        v-text="chinese"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import AnimatedButton from '@/components/shared/AnimatedButton.vue'
import type { TokenUsage } from '@/services/endpoints/settings'

defineProps<{
  label?: string
  labelClass?: string
  english?: string
  chinese?: string
  streaming?: boolean
  usage?: TokenUsage
  showCopy?: boolean
  showRefineButtons?: boolean
  /** 已完成的优化模式列表，用于显示标记图标 */
  refineDoneModes?: string[]
  englishLabel?: string
  chineseLabel?: string
}>()

defineEmits<{
  copyEnglish: []
  copyChinese: []
  refine: [mode: string]
}>()
</script>