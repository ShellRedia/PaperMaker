/**
 * WebSocket 流式通信管理
 */

export interface StreamChunk {
  type: 'token' | 'progress' | 'done' | 'error'
  payload: any
}

export class StreamManager {
  private ws: WebSocket | null = null
  private listeners = new Map<string, Set<Function>>()
  private _connected = false

  get connected(): boolean {
    return this._connected
  }

  /**
   * 连接到流式端点
   * @param taskId 任务 ID
   * @param endpoint WebSocket 路径，如 '/ws/stream'
   */
  connect(taskId: string, endpoint: string = '/ws/stream') {
    const wsBase = window.__PAPERMAKER_API__?.replace('http', 'ws') || window.location.origin.replace('http', 'ws')
    const url = `${wsBase}/api${endpoint}/${taskId}`

    this.ws = new WebSocket(url)

    this.ws.onopen = () => {
      this._connected = true
    }

    this.ws.onmessage = (event) => {
      try {
        const chunk: StreamChunk = JSON.parse(event.data)
        this.dispatch(chunk.type, chunk.payload)
      } catch (e) {
        console.error('[WS] parse error:', e)
      }
    }

    this.ws.onerror = (event) => {
      console.error('[WS] connection error:', event)
      this.dispatch('error', 'WebSocket 连接失败')
    }

    this.ws.onclose = () => {
      this._connected = false
    }
  }

  /**
   * 发送 JSON 数据
   */
  send(data: Record<string, any>) {
    if (this.ws && this._connected) {
      this.ws.send(JSON.stringify(data))
    }
  }

  /**
   * 监听特定类型的事件
   */
  on(type: string, callback: Function) {
    if (!this.listeners.has(type)) {
      this.listeners.set(type, new Set())
    }
    this.listeners.get(type)!.add(callback)
  }

  /**
   * 移除监听
   */
  off(type: string, callback: Function) {
    this.listeners.get(type)?.delete(callback)
  }

  /**
   * 断开连接
   */
  disconnect() {
    this.ws?.close()
    this.listeners.clear()
  }

  private dispatch(type: string, payload: any) {
    this.listeners.get(type)?.forEach(fn => fn(payload))
  }
}
