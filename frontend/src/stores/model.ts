import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { modelApi, StreamManager } from '@/services/endpoints/models'
import type { ModelInfo, StreamChunk } from '@/services/endpoints/models'

export const useModelStore = defineStore('model', () => {
  // ── 状态 ──
  const models = ref<ModelInfo[]>([])
  const activeModel = ref<string>('text_polish')
  const streamOutput = ref<string>('')
  const streamProgress = ref(0)
  const isStreaming = ref(false)
  const streamError = ref<string | null>(null)

  const activeModelInfo = computed(() =>
    models.value.find(m => m.name === activeModel.value)
  )

  // ── 操作 ──
  async function fetchModels() {
    models.value = await modelApi.list()
  }

  async function infer(inputText: string, params: Record<string, any> = {}) {
    return await modelApi.infer(activeModel.value, inputText, params)
  }

  function startStream(text: string, model?: string, style?: string) {
    const targetModel = model || activeModel.value
    streamOutput.value = ''
    streamProgress.value = 0
    streamError.value = null
    isStreaming.value = true

    const taskId = `task_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`
    const manager = new StreamManager()

    manager.on('token', (payload: StreamChunk['payload']) => {
      streamOutput.value += payload.token
      streamProgress.value = payload.progress
    })

    manager.on('done', () => {
      isStreaming.value = false
      streamProgress.value = 1
    })

    manager.on('error', (payload: any) => {
      streamError.value = payload
      isStreaming.value = false
    })

    // 占位: 通过 WebSocket 连接（后端 websocket 路径需要一致）
    // 当前使用 REST 轮询模拟
    manager.connect(taskId)

    return { taskId, manager }
  }

  return {
    models, activeModel, streamOutput, streamProgress,
    isStreaming, streamError, activeModelInfo,
    fetchModels, infer, startStream,
  }
})
