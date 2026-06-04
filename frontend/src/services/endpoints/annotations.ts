import { api } from '../api'

export interface AnnotationCreate {
  document_id: string
  type: string
  label: string
  color: string
  page_index: number
  data: Record<string, any>
  comment: string
}

export interface AnnotationItem {
  id: string
  document_id: string
  type: string
  label: string
  color: string
  page_index: number
  data: Record<string, any>
  comment: string
  created_at: string
}

export const annotationApi = {
  async list(docId: string) {
    const res = await api.get(`/annotations/document/${docId}`)
    return res.data as AnnotationItem[]
  },

  async create(data: AnnotationCreate) {
    const res = await api.post('/annotations/', data)
    return res.data as { id: string }
  },

  async update(id: string, data: Partial<AnnotationItem>) {
    const res = await api.put(`/annotations/${id}`, data)
    return res.data as { id: string }
  },

  async delete(id: string) {
    await api.delete(`/annotations/${id}`)
  },
}
