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

/** 翻译规则项 */
export interface TranslationRuleItem {
  id: string
  pattern: string
  replacement: string
  rule_type: 'replace' | 'no_translate'
}

/** 翻译规则配置 */
export interface TranslationRulesConfig {
  rules: TranslationRuleItem[]
}

/** 优化结果（仅英文+中文，不含 usage，usage 在 done payload 里） */
export interface RefineResult {
  english: string
  chinese: string
  usage?: TokenUsage
  refine_mode?: string
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

  /**
   * 流式优化 — 精简/学术化
   * @param originalInput 原始中文输入
   * @param currentEnglish 当前英文翻译
   * @param refineMode "concise" | "academic"
   */
  async *refineStream(
    originalInput: string,
    currentEnglish: string,
    refineMode: 'concise' | 'academic',
  ): AsyncGenerator<
    { type: 'token'; payload: { token: string } }
    | { type: 'done'; payload: RefineResult }
    | { type: 'error'; payload: string },
    void,
    unknown
  > {
    const API_BASE = window.__PAPERMAKER_API__ || window.location.origin
    const response = await fetch(`${API_BASE}/api/translate/refine/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        original_input: originalInput,
        current_english: currentEnglish,
        refine_mode: refineMode,
      }),
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
    // axios 响应拦截器已返回 body，所以 res 就是 {code, data, message}
    // res.data 才是 TranslationRecord[] 数组
    return (res.data || []) as TranslationRecord[]
  },

  /** 清空文档的翻译历史 */
  async clearHistory(documentId: string): Promise<void> {
    await api.delete(`/translate/history/${documentId}`)
  },

  /** 获取翻译规则 */
  async getRules(): Promise<TranslationRulesConfig> {
    const res = await api.get('/translate/rules')
    return (res.data || { rules: [] }) as TranslationRulesConfig
  },

  /** 保存翻译规则 */
  async saveRules(config: TranslationRulesConfig): Promise<void> {
    await api.put('/translate/rules', config)
  },
}
