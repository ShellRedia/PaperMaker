import { api } from '../api'

export interface PolishResult {
  id: string
  original: string
  polished: string
  diff: Array<{
    op: string
    original_words: string[]
    polished_words: string[]
  }>
}

export interface PolishHistoryItem {
  id: string
  original_text: string
  polished_text: string
  style: string
  model_name: string
  created_at: string
}

export const polishApi = {
  async polish(docId: string, text: string, context = '', style = 'academic') {
    const res = await api.post('/polish/', {
      document_id: docId,
      text,
      context,
      style,
    })
    return res.data as PolishResult
  },

  async getHistory(docId: string) {
    const res = await api.get(`/polish/history/${docId}`)
    return res.data as PolishHistoryItem[]
  },
}
