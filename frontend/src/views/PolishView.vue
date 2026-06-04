<template>
  <div class="h-full overflow-auto p-6">
    <div class="max-w-5xl mx-auto space-y-6">
      <h1 class="text-2xl font-bold text-white">文本润色</h1>

      <div v-if="!docId || docId === 'polish'" class="text-center py-20">
        <div class="text-5xl mb-4">✨</div>
        <p class="text-surface-400 mb-4">请从文档页面打开润色功能</p>
        <AnimatedButton variant="primary" @click="router.push('/document')">
          前往文档
        </AnimatedButton>
      </div>

      <template v-else>
        <!-- 输入区 -->
        <div class="space-y-3">
          <div class="flex items-center gap-3">
            <span class="text-sm text-surface-400">润色风格:</span>
            <button
              v-for="s in styles"
              :key="s.id"
              class="px-4 py-1.5 rounded-lg text-sm transition-colors duration-200"
              :class="selectedStyle === s.id
                ? 'bg-primary-500 text-white'
                : 'bg-surface-700 text-surface-300 hover:bg-surface-600'"
              @click="selectedStyle = s.id"
            >
              {{ s.label }}
            </button>
          </div>

          <textarea
            v-model="inputText"
            class="w-full h-40 bg-surface-800 border border-surface-700 rounded-xl p-4
                   text-white text-sm resize-none
                   focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500/50
                   placeholder-surface-500"
            placeholder="输入需要润色的文本..."
          />

          <div class="flex gap-3">
            <AnimatedButton variant="primary" @click="startPolish">
              <template #icon>✨</template>
              开始润色
            </AnimatedButton>
            <AnimatedButton
              v-if="isPolishing"
              variant="ghost"
              @click="isPolishing = false"
            >
              取消
            </AnimatedButton>
          </div>
        </div>

        <!-- 流式输出区 -->
        <div
          v-if="polishedText || isPolishing"
          class="bg-surface-800 border border-surface-700 rounded-xl p-5 space-y-3"
          v-anime:fadeInUp
        >
          <div class="flex items-center gap-2">
            <span class="text-sm text-surface-400">润色结果</span>
            <span v-if="isPolishing" class="anim-breathe text-xs text-primary-400">
              推理中...
            </span>
          </div>
          <div class="text-white whitespace-pre-wrap leading-relaxed">
            {{ polishedText }}
            <span v-if="isPolishing" class="inline-block w-0.5 h-4 bg-primary-400 anim-typewriter-cursor align-middle ml-0.5" />
          </div>

          <!-- 进度条 -->
          <div v-if="isPolishing" class="w-full h-1 bg-surface-700 rounded-full overflow-hidden">
            <div
              class="h-full bg-primary-500 rounded-full transition-all duration-300"
              :style="{ width: streamProgress * 100 + '%' }"
            />
          </div>
        </div>

        <!-- 润色历史 -->
        <div v-if="history.length > 0" class="space-y-3">
          <h3 class="text-white font-semibold">润色历史</h3>
          <div
            v-for="item in history"
            :key="item.id"
            class="bg-surface-800/50 border border-surface-700/50 rounded-lg p-4"
          >
            <div class="flex items-center gap-2 mb-2">
              <span class="text-xs text-surface-500 bg-surface-700 px-2 py-0.5 rounded">
                {{ item.style }}
              </span>
              <span class="text-xs text-surface-500">{{ formatDate(item.created_at) }}</span>
            </div>
            <p class="text-sm text-surface-300 line-clamp-2">{{ item.polished_text }}</p>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { polishApi, type PolishHistoryItem } from '@/services/endpoints/polish'
import { modelApi } from '@/services/endpoints/models'
import { useUIStore } from '@/stores/ui'
import AnimatedButton from '@/components/shared/AnimatedButton.vue'

const route = useRoute()
const router = useRouter()
const ui = useUIStore()

const docId = computed(() => route.params.docId as string | undefined)

const inputText = ref('')
const polishedText = ref('')
const selectedStyle = ref('academic')
const isPolishing = ref(false)
const streamProgress = ref(0)
const history = ref<PolishHistoryItem[]>([])

const styles = [
  { id: 'academic', label: '🎓 学术风格' },
  { id: 'concise', label: '📐 精简表达' },
  { id: 'expanded', label: '📖 扩展详细' },
]

async function startPolish() {
  if (!inputText.value.trim()) {
    ui.addToast('请先输入文本', 'warning')
    return
  }

  const id = docId.value!
  isPolishing.value = true
  polishedText.value = ''
  streamProgress.value = 0

  try {
    // 使用 REST 方式 (WebSocket 备选)
    const result = await polishApi.polish(id, inputText.value, '', selectedStyle.value)
    polishedText.value = result.polished
    streamProgress.value = 1
    ui.addToast('润色完成', 'success')

    // 刷新历史
    loadHistory()
  } catch (e) {
    ui.addToast('润色失败，请重试', 'error')
  } finally {
    isPolishing.value = false
  }
}

async function loadHistory() {
  const id = docId.value
  if (id && id !== 'polish') {
    try {
      history.value = await polishApi.getHistory(id)
    } catch (e) {
      console.error('Failed to load polish history:', e)
    }
  }
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('zh-CN', {
    year: 'numeric', month: 'short', day: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

onMounted(() => {
  loadHistory()
})
</script>
