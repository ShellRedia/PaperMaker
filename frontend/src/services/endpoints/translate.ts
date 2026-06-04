import { api } from '../api'
import type { TranslateResult, TokenUsage } from './settings'

export type { TranslateResult, TokenUsage }

export interface HistoryMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface TranslationRecord {
  id: string
  document_id: string
  role: 'user' | 'assistant'
  content: string
  usage_json: string
  created_at: string
}

export const translateApi = {
  /** 一次性翻译（带上下文） */
  async translate(
    text: string,
    history: HistoryMessage[] = [],
    documentId?: string,
  ): Promise<TranslateResult> {
    const res = await api.post('/translate', { text, history, document_id: documentId || null })
    return res.data as TranslateResult
  },

  /**
   * 流式翻译 — 返回 SSE reader（带上下文）
   */
  async *translateStream(
    text: string,
    history: HistoryMessage[] = [],
    documentId?: string,
  ): AsyncGenerator<
    { type: 'token'; payload: { token: string } }
    | { type: 'done'; payload: TranslateResult }
    | { type: 'error'; payload: string },
    void,
    unknown
  > {
    const API_BASE = window.__PAPERMAKER_API__ || window.location.origin
    const response = await fetch(`${API_BASE}/api/translate/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, history, document_id: documentId || null }),
    })

    if (!response.ok) {
      yield { type: 'error', payload: `HTTP ${response.status}` }
      return
    }

    const reader = response.body!.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))
            yield data
          } catch {
            // skip malformed
          }
        }
      }
    }
  },

  /** 获取文档的翻译历史 */
  async getHistory(documentId: string): Promise<TranslationRecord[]> {
    const res = await api.get(`/translate/history/${documentId}`)
    return (res.data?.data || []) as TranslationRecord[]
  },

  /** 清空文档的翻译历史 */
  async clearHistory(documentId: string): Promise<void> {
    await api.delete(`/translate/history/${documentId}`)
  },
}
