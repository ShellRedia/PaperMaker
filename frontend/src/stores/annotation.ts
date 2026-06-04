import { defineStore } from 'pinia'
import { ref } from 'vue'
import { annotationApi } from '@/services/endpoints/annotations'
import type { AnnotationItem, AnnotationCreate } from '@/services/endpoints/annotations'

export const useAnnotationStore = defineStore('annotation', () => {
  // ── 状态 ──
  const annotations = ref<AnnotationItem[]>([])
  const selectedId = ref<string | null>(null)
  const currentLabel = ref('default')
  const currentColor = ref('#3B82F6')
  const loading = ref(false)

  // ── 操作 ──
  async function fetchAnnotations(docId: string) {
    loading.value = true
    try {
      annotations.value = await annotationApi.list(docId)
    } finally {
      loading.value = false
    }
  }

  async function createAnnotation(data: AnnotationCreate) {
    const result = await annotationApi.create(data)
    // 重新加载以获取完整数据
    await fetchAnnotations(data.document_id)
    return result.id
  }

  async function updateAnnotation(id: string, data: Partial<AnnotationItem>) {
    await annotationApi.update(id, data)
    const idx = annotations.value.findIndex(a => a.id === id)
    if (idx !== -1) {
      Object.assign(annotations.value[idx], data)
    }
  }

  async function deleteAnnotation(id: string) {
    await annotationApi.delete(id)
    annotations.value = annotations.value.filter(a => a.id !== id)
    if (selectedId.value === id) {
      selectedId.value = null
    }
  }

  function selectAnnotation(id: string | null) {
    selectedId.value = id
  }

  return {
    annotations, selectedId, currentLabel, currentColor, loading,
    fetchAnnotations, createAnnotation, updateAnnotation, deleteAnnotation,
    selectAnnotation,
  }
})
