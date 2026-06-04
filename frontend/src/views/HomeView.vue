<template>
  <div ref="pageRef" class="h-full overflow-auto p-8">
    <!-- 欢迎区域 -->
    <div class="max-w-4xl mx-auto space-y-8">
      <!-- Hero -->
      <section v-anime:fadeInUp class="text-center py-12">
        <h1 class="text-4xl font-bold text-white mb-3">
          📝 PaperMaker
        </h1>
        <p class="text-lg text-surface-400 mb-8">
          深度学习论文写作助手 — 智能标注 · 图表展示 · 文本润色
        </p>
        <div class="flex justify-center gap-4">
          <AnimatedButton variant="primary" @click="createNewDoc">
            <template #icon>📄</template>
            新建文档
          </AnimatedButton>
          <AnimatedButton variant="secondary" @click="router.push('/document')">
            <template #icon>📂</template>
            打开文档
          </AnimatedButton>
        </div>
      </section>

      <!-- 功能卡片 -->
      <section class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div
          v-for="(card, i) in featureCards"
          :key="card.title"
          v-anime:fadeInUp
          class="group bg-surface-800 border border-surface-700 rounded-xl p-5
                 hover:border-primary-500/50 hover:bg-surface-750
                 transition-all duration-300 cursor-pointer"
          :style="{ transitionDelay: i * 80 + 'ms' }"
          @click="router.push(card.to)"
        >
          <div class="text-3xl mb-3 group-hover:scale-110 transition-transform duration-300">
            {{ card.icon }}
          </div>
          <h3 class="text-white font-semibold mb-1">{{ card.title }}</h3>
          <p class="text-sm text-surface-400">{{ card.desc }}</p>
        </div>
      </section>

      <!-- 最近文档 -->
      <section v-anime:fadeInUp>
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-semibold text-white">最近文档</h2>
          <AnimatedButton variant="ghost" size="sm" @click="docStore.fetchDocuments()">
            刷新
          </AnimatedButton>
        </div>

        <!-- 文档列表 -->
        <div ref="listRef" class="space-y-2">
          <SkeletonLoader
            v-if="docStore.loading && docStore.documents.length === 0"
            v-for="n in 3"
            :key="n"
            height="56px"
          />
          <div
            v-for="(doc, i) in docStore.sortedDocuments.slice(0, 5)"
            :key="doc.id"
            class="anim-list-item flex items-center gap-4 px-4 py-3 rounded-lg
                   bg-surface-800/50 cursor-pointer group"
            @click="router.push(`/document/${doc.id}`)"
          >
            <span class="text-xl flex-shrink-0">📄</span>
            <div class="flex-1 min-w-0">
              <div class="text-white text-sm font-medium truncate">
                {{ doc.title }}
              </div>
              <div class="text-xs text-surface-500">
                {{ formatDate(doc.updated_at) }}
              </div>
            </div>
            <span class="text-xs text-surface-600 bg-surface-700 px-2 py-0.5 rounded">
              {{ doc.file_type }}
            </span>
            <button
              class="opacity-0 group-hover:opacity-100 p-1 hover:bg-surface-600 rounded
                     transition-all duration-200"
              @click.stop="handleDelete(doc.id)"
            >
              <svg class="w-4 h-4 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>

          <!-- 空状态 -->
          <div
            v-if="!docStore.loading && docStore.documents.length === 0"
            class="text-center py-12 text-surface-500"
          >
            <div class="text-4xl mb-3">📭</div>
            <p>还没有文档，点击上方「新建文档」开始创作</p>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useDocumentStore } from '@/stores/document'
import { useUIStore } from '@/stores/ui'
import AnimatedButton from '@/components/shared/AnimatedButton.vue'
import SkeletonLoader from '@/components/shared/SkeletonLoader.vue'

const router = useRouter()
const docStore = useDocumentStore()
const ui = useUIStore()

const pageRef = ref<HTMLElement | null>(null)
const listRef = ref<HTMLElement | null>(null)

const featureCards = [
  { to: '/document', icon: '📝', title: '文档编辑', desc: 'Markdown/LaTeX 论文编辑，Monaco 编辑器' },
  { to: '/annotation', icon: '🏷️', title: '数据标注', desc: '图片/PDF 标注，画布交互' },
  { to: '/statistics', icon: '📊', title: '统计图表', desc: '论文字数、可读性、词频可视化' },
  { to: '/polish', icon: '✨', title: '文本润色', desc: 'AI 驱动的学术文本优化' },
]

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('zh-CN', {
    year: 'numeric', month: 'short', day: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

async function createNewDoc() {
  const id = await docStore.createDocument('新论文')
  ui.addToast('文档创建成功', 'success')
  router.push(`/document/${id}`)
}

async function handleDelete(id: string) {
  await docStore.deleteDocument(id)
  ui.addToast('文档已删除', 'info')
}

onMounted(() => {
  docStore.fetchDocuments()
})
</script>
