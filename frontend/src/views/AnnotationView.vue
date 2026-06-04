<template>
  <div class="h-full overflow-auto p-6">
    <div class="max-w-5xl mx-auto space-y-6">
      <h1 class="text-2xl font-bold text-white">数据标注</h1>

      <!-- 选择文档提示 -->
      <div v-if="!route.params.docId || route.params.docId === 'annotation'" class="text-center py-20">
        <div class="text-5xl mb-4">🏷️</div>
        <p class="text-surface-400 mb-4">请从文档页面打开标注功能</p>
        <AnimatedButton variant="primary" @click="router.push('/document')">
          前往文档
        </AnimatedButton>
      </div>

      <!-- 标注工作区 -->
      <div v-else class="space-y-4">
        <!-- 工具栏 -->
        <div class="flex items-center gap-3 p-3 bg-surface-800 border border-surface-700 rounded-xl">
          <div class="flex items-center gap-2">
            <span class="text-sm text-surface-400">工具:</span>
            <button
              v-for="tool in tools"
              :key="tool.id"
              class="px-3 py-1.5 rounded-lg text-sm transition-colors duration-200"
              :class="activeTool === tool.id
                ? 'bg-primary-500 text-white'
                : 'bg-surface-700 text-surface-300 hover:bg-surface-600'"
              @click="activeTool = tool.id"
            >
              {{ tool.icon }} {{ tool.label }}
            </button>
          </div>

          <div class="w-px h-6 bg-surface-600" />

          <!-- 标签选择 -->
          <LabelPalette
            v-model="annStore.currentLabel"
            v-model:color="annStore.currentColor"
          />

          <div class="flex-1" />

          <AnimatedButton variant="ghost" @click="saveAnnotations">
            💾 保存标注
          </AnimatedButton>
        </div>

        <!-- Canvas 画布 -->
        <div class="bg-surface-800 border border-surface-700 rounded-xl overflow-hidden"
             style="height: 500px;">
          <div ref="canvasContainerRef" class="w-full h-full" />
        </div>

        <!-- 标注列表 -->
        <div ref="listRef" class="space-y-2">
          <h3 class="text-sm font-medium text-surface-400">
            标注列表 ({{ annStore.annotations.length }})
          </h3>
          <div
            v-for="ann in annStore.annotations"
            :key="ann.id"
            class="anim-list-item flex items-center gap-3 px-4 py-2.5 rounded-lg
                   bg-surface-800/50 cursor-pointer"
            :class="{ 'ring-1 ring-primary-500/50': annStore.selectedId === ann.id }"
            @click="annStore.selectAnnotation(ann.id)"
          >
            <span
              class="w-3 h-3 rounded-full flex-shrink-0"
              :style="{ backgroundColor: ann.color }"
            />
            <span class="text-sm text-white">{{ ann.label }}</span>
            <span class="text-xs text-surface-500 bg-surface-700 px-2 py-0.5 rounded">
              {{ ann.type }}
            </span>
            <span class="flex-1" />
            <button
              class="text-surface-500 hover:text-red-400 transition-colors"
              @click.stop="annStore.deleteAnnotation(ann.id)"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAnnotationStore } from '@/stores/annotation'
import { useUIStore } from '@/stores/ui'
import AnimatedButton from '@/components/shared/AnimatedButton.vue'
import LabelPalette from '@/components/annotation/LabelPalette.vue'

const route = useRoute()
const router = useRouter()
const annStore = useAnnotationStore()
const ui = useUIStore()

const canvasContainerRef = ref<HTMLElement | null>(null)
const listRef = ref<HTMLElement | null>(null)
const activeTool = ref('bbox')

const tools = [
  { id: 'bbox', icon: '⬜', label: '边界框' },
  { id: 'polygon', icon: '🔷', label: '多边形' },
  { id: 'relation', icon: '🔗', label: '关系' },
  { id: 'select', icon: '🖱️', label: '选择' },
]

async function saveAnnotations() {
  ui.addToast('标注已保存', 'success')
}

onMounted(async () => {
  const docId = route.params.docId as string
  if (docId && docId !== 'annotation') {
    await annStore.fetchAnnotations(docId)
  }
})

watch(() => route.params.docId, (newId) => {
  if (newId && newId !== 'annotation') {
    annStore.fetchAnnotations(newId as string)
  }
})
</script>
