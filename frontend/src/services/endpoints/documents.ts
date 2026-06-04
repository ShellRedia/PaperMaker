import { api } from '../api'

export interface DocumentItem {
  id: string
  title: string
  file_type: string
  updated_at: string
}

export interface DocumentDetail {
  id: string
  title: string
  content: string
  file_type: string
  created_at: string
  updated_at: string
}

export interface SectionNode {
  title: string
  level: number
  start_line: number
  children: SectionNode[]
}

export const documentApi = {
  async list(page = 1, pageSize = 20) {
    const res = await api.get('/documents/', { params: { page, page_size: pageSize } })
    return res.data as { items: DocumentItem[]; total: number; page: number; page_size: number }
  },

  async create(title: string, content = '', fileType = 'markdown') {
    const res = await api.post('/documents/', { title, content, file_type: fileType })
    return res.data as { id: string; title: string }
  },

  async get(id: string) {
    const res = await api.get(`/documents/${id}`)
    return res.data as DocumentDetail
  },

  async update(id: string, data: { title?: string; content?: string }) {
    const res = await api.put(`/documents/${id}`, data)
    return res.data as { id: string; updated_at: string }
  },

  async delete(id: string) {
    await api.delete(`/documents/${id}`)
  },

  async getSections(docId: string) {
    const res = await api.get(`/documents/${docId}/sections`)
    return res.data as SectionNode[]
  },
}
