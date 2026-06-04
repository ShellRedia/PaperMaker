<template>
  <div class="h-full overflow-auto p-6">
    <div v-if="document" class="max-w-lg mx-auto space-y-6">
      <!-- 文档元信息 -->
      <section>
        <h3 class="text-sm font-semibold text-surface-400 uppercase tracking-wider mb-3">
          文档信息
        </h3>
        <div class="space-y-2 bg-surface-800/50 rounded-lg p-4">
          <InfoRow label="标题" :value="document.title" />
          <InfoRow label="类型" :value="document.file_type" />
          <InfoRow label="创建时间" :value="formatDate(document.created_at)" />
          <InfoRow label="更新时间" :value="formatDate(document.updated_at)" />
        </div>
      </section>

      <!-- 统计 -->
      <section>
        <h3 class="text-sm font-semibold text-surface-400 uppercase tracking-wider mb-3">
          文档统计
        </h3>
        <div class="grid grid-cols-2 gap-3">
          <StatCard label="总字符数" :value="String(content.length)" icon="📝" />
          <StatCard label="总行数" :value="String(content.split('\n').length)" icon="📏" />
          <StatCard label="章节数" :value="String(sections.length)" icon="📑" />
          <StatCard label="字数估算" :value="String(Math.ceil(content.replace(/\s/g, '').length))" icon="🔤" />
        </div>
      </section>

      <!-- 待办 / 备注区 -->
      <section>
        <h3 class="text-sm font-semibold text-surface-400 uppercase tracking-wider mb-3">
          备注
        </h3>
        <textarea
          class="w-full h-24 bg-surface-800/50 border border-surface-700/50 rounded-lg p-3
                 text-sm text-surface-300 placeholder-surface-500 resize-none
                 focus:outline-none focus:border-primary-500/50 transition-colors"
          placeholder="添加备注...（即将支持）"
          disabled
        />
        <p class="text-xs text-surface-500 mt-1">备注功能即将上线</p>
      </section>
    </div>
    <div v-else class="flex items-center justify-center h-full text-surface-500 text-sm">
      未选择文档
    </div>
  </div>
</template>

<script setup lang="ts">
import type { DocumentDetail } from '@/services/endpoints/documents'

defineProps<{
  document: DocumentDetail | null
  content: string
  sections: any[]
}>()

function formatDate(iso: string) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}
</script>

<!-- 内联小组件 -->
<script lang="ts">
import { defineComponent, h } from 'vue'

export const InfoRow = defineComponent({
  props: { label: String, value: String },
  setup(props) {
    return () =>
      h('div', { class: 'flex items-center justify-between text-sm' }, [
        h('span', { class: 'text-surface-500' }, props.label),
        h('span', { class: 'text-surface-200 font-medium' }, props.value ?? '—'),
      ])
  },
})

export const StatCard = defineComponent({
  props: { label: String, value: String, icon: String },
  setup(props) {
    return () =>
      h('div', { class: 'bg-surface-800/50 rounded-lg p-3 text-center' }, [
        h('div', { class: 'text-lg mb-1' }, props.icon),
        h('div', { class: 'text-lg font-semibold text-white' }, props.value),
        h('div', { class: 'text-xs text-surface-500' }, props.label),
      ])
  },
})
</script>
