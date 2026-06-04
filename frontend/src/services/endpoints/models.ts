import { api } from '../api'
import { StreamManager } from '../ws'

export { StreamManager }
export type { StreamChunk } from '../ws'

export interface ModelInfo {
  name: string
  description: string
  status: string
}

export const modelApi = {
  async list() {
    const res = await api.get('/models/')
    return res.data as ModelInfo[]
  },

  async infer(modelName: string, inputText: string, params: Record<string, any> = {}) {
    const res = await api.post('/models/infer', {
      model_name: modelName,
      input_text: inputText,
      params,
    })
    return res.data as { model: string; output: string }
  },

  /**
   * 创建流式推理连接 (WebSocket)
   * 使用 /api/polish/ws/stream/{taskId} 路径
   */
  async streamPolish(taskId: string, text: string, style: string = 'academic') {
    const manager = new StreamManager()
    manager.connect(taskId, '/polish/ws/stream')

    // 连接成功后发送数据
    const checkInterval = setInterval(() => {
      if (manager.connected) {
        clearInterval(checkInterval)
        manager.send({ text, style })
      }
    }, 50)

    return manager
  },
}
