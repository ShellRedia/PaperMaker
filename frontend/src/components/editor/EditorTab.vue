<template>
  <div class="h-full flex flex-col">
    <!-- 编辑器主体 -->
    <div ref="editorContainerRef" class="flex-1 monaco-editor-container" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as monaco from 'monaco-editor'

const props = defineProps<{
  content: string
  language?: string
}>()

const emit = defineEmits<{
  'update:content': [value: string]
  'save': []
}>()

const editorContainerRef = ref<HTMLElement | null>(null)
let editor: monaco.editor.IStandaloneCodeEditor | null = null

function getValue(): string {
  return editor?.getValue() ?? ''
}

function setValue(content: string) {
  if (editor && editor.getValue() !== content) {
    editor.setValue(content)
  }
}

onMounted(async () => {
  await nextTick()

  if (!editorContainerRef.value) return

  editor = monaco.editor.create(editorContainerRef.value, {
    value: props.content,
    language: props.language ?? 'markdown',
    theme: 'vs-dark',
    fontSize: 14,
    lineNumbers: 'on',
    minimap: { enabled: false },
    wordWrap: 'on',
    automaticLayout: true,
    scrollBeyondLastLine: false,
    padding: { top: 16, bottom: 16 },
  })

  // Ctrl+S 保存
  editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
    emit('save')
  })

  // 内容变更通知
  editor.onDidChangeModelContent(() => {
    if (editor) {
      emit('update:content', editor.getValue())
    }
  })
})

// 外部 content 变化时同步进编辑器
watch(() => props.content, (val) => {
  setValue(val)
})

onUnmounted(() => {
  editor?.dispose()
})

defineExpose({ getValue, setValue })
</script>
