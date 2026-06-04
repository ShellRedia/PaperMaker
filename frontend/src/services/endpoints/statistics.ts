import { api } from '../api'

export interface DocumentStats {
  word_count: number
  sentence_count: number
  paragraph_count: number
  section_count: number
  avg_sentence_length: number
  flesch_reading_ease: number
  flesch_kincaid_grade: number
}

export interface ReadabilityScore {
  flesch_reading_ease: number
  flesch_kincaid_grade: number
  avg_sentence_length: number
  interpretation: string
}

export interface TermFrequency {
  term: string
  count: number
}

export const statisticsApi = {
  async getStats(docId: string) {
    const res = await api.get(`/statistics/document/${docId}`)
    return res.data as DocumentStats
  },

  async getReadability(docId: string) {
    const res = await api.get(`/statistics/document/${docId}/readability`)
    return res.data as ReadabilityScore
  },

  async getTerms(docId: string, limit = 50) {
    const res = await api.get(`/statistics/document/${docId}/terms`, { params: { limit } })
    return res.data as TermFrequency[]
  },
}
