import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { documentApi } from '@/services/endpoints/documents'
import type { DocumentItem, DocumentDetail } from '@/services/endpoints/documents'

export const useDocumentStore = defineStore('document', () => {
  // ── 状态 ──
  const documents = ref<DocumentItem[]>([])
  const currentDocument = ref<DocumentDetail | null>(null)
  const totalCount = ref(0)
  const currentPage = ref(1)
  const loading = ref(false)

  // ── 计算属性 ──
  const sortedDocuments = computed(() =>
    [...documents.value].sort(
      (a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
    )
  )

  // ── 操作 ──
  async function fetchDocuments(page = 1, pageSize = 20) {
    loading.value = true
    try {
      const res = await documentApi.list(page, pageSize)
      documents.value = res.items
      totalCount.value = res.total
      currentPage.value = page
    } finally {
      loading.value = false
    }
  }

  async function createDocument(title = 'Untitled', fileType = 'markdown') {
    const res = await documentApi.create(title, '', fileType)
    await fetchDocuments()
    return res.id
  }

  async function fetchDocument(id: string) {
    loading.value = true
    try {
      currentDocument.value = await documentApi.get(id)
      return currentDocument.value
    } finally {
      loading.value = false
    }
  }

  async function updateDocument(id: string, data: { title?: string; content?: string }) {
    await documentApi.update(id, data)
    if (currentDocument.value && currentDocument.value.id === id) {
      if (data.title !== undefined) currentDocument.value.title = data.title
      if (data.content !== undefined) currentDocument.value.content = data.content
      currentDocument.value.updated_at = new Date().toISOString()
    }
  }

  async function deleteDocument(id: string) {
    await documentApi.delete(id)
    documents.value = documents.value.filter(d => d.id !== id)
    if (currentDocument.value?.id === id) {
      currentDocument.value = null
    }
  }

  async function fetchSections(docId: string) {
    return await documentApi.getSections(docId)
  }

  return {
    documents, currentDocument, totalCount, currentPage, loading,
    sortedDocuments,
    fetchDocuments, createDocument, fetchDocument, updateDocument,
    deleteDocument, fetchSections,
  }
})
