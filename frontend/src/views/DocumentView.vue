<template>
  <div class="h-full flex flex-col">
    <!-- 未选择文档: 文档列表 -->
    <div v-if="!route.params.id" class="flex-1 overflow-auto p-8">
      <div class="max-w-2xl mx-auto space-y-6">
        <div class="flex items-center justify-between">
          <h1 class="text-2xl font-bold text-white">文档列表</h1>
          <AnimatedButton variant="primary" @click="createNew">
            <template #icon>➕</template>
            新建
          </AnimatedButton>
        </div>

        <SkeletonLoader v-if="docStore.loading" v-for="n in 5" :key="n" height="52px" />

        <div
          v-for="doc in docStore.sortedDocuments"
          :key="doc.id"
          class="anim-list-item flex items-center gap-4 px-4 py-3 rounded-lg
                 bg-surface-800/50 cursor-pointer"
          @click="openDocument(doc.id)"
        >
          <span class="text-xl">📄</span>
          <div class="flex-1 min-w-0">
            <div class="text-white text-sm font-medium truncate">{{ doc.title }}</div>
            <div class="text-xs text-surface-500">{{ formatDate(doc.updated_at) }}</div>
          </div>
          <span class="text-xs text-surface-600 bg-surface-700 px-2 py-0.5 rounded">
            {{ doc.file_type }}
          </span>
        </div>
      </div>
    </div>

    <!-- 已选文档: Tab 布局 -->
    <template v-else>
      <!-- 顶部：标题 + 操作 -->
      <div class="flex items-center gap-2 px-4 py-2 bg-surface-900 border-b border-surface-700/50">
        <AnimatedButton variant="ghost" size="sm" @click="backToList">
          ← 返回
        </AnimatedButton>
        <input
          ref="titleInputRef"
          v-model="editTitle"
          class="flex-1 bg-transparent text-white text-lg font-semibold
                 border-none outline-none focus:ring-0 px-2 py-1"
          placeholder="文档标题..."
          @blur="saveTitle"
        />
        <span class="text-xs text-surface-500">{{ docStore.currentDocument?.file_type }}</span>
        <AnimatedButton variant="ghost" size="sm" @click="saveContent">💾 保存</AnimatedButton>
      </div>

      <!-- Tab 区域 -->
      <AnimatedTabs
        v-model="activeTab"
        :tabs="tabItems"
        :closable="tabItems.length > 1"
        :addable="true"
        :compact="true"
        :keep-alive="aliveTabs"
        @add="addCustomTab"
        @close="closeCustomTab"
      >
        <template #panel="{ tab }">
          <TranslateChat
            v-if="tab.id === 'translate'"
            ref="translateChatRef"
          />
          <EditorTab
            v-else-if="tab.id === 'editor'"
            ref="editorTabRef"
            :content="editorContent"
            :language="editorLanguage"
            @update:content="onContentChange"
            @save="saveContent"
          />
          <OutlineTab
            v-else-if="tab.id === 'outline'"
            :sections="sections"
          />
          <InfoTab
            v-else-if="tab.id === 'info'"
            :document="docStore.currentDocument"
            :content="editorContent"
            :sections="sections"
          />
          <div v-else class="h-full overflow-auto p-4">
            <p class="text-sm text-surface-400">自定义标签页: {{ tab.label }}</p>
            <p class="text-xs text-surface-500 mt-2">此 Tab 可以随时关闭，之后可重新添加。</p>
          </div>
        </template>
      </AnimatedTabs>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDocumentStore } from '@/stores/document'
import { useUIStore } from '@/stores/ui'
import AnimatedButton from '@/components/shared/AnimatedButton.vue'
import SkeletonLoader from '@/components/shared/SkeletonLoader.vue'
import AnimatedTabs, { type TabItem } from '@/components/shared/AnimatedTabs.vue'
import EditorTab from '@/components/editor/EditorTab.vue'
import OutlineTab from '@/components/editor/OutlineTab.vue'
import InfoTab from '@/components/editor/InfoTab.vue'
import TranslateChat from '@/components/editor/TranslateChat.vue'

const route = useRoute()
const router = useRouter()
const docStore = useDocumentStore()
const ui = useUIStore()

const titleInputRef = ref<HTMLInputElement | null>(null)
const editorTabRef = ref<InstanceType<typeof EditorTab> | null>(null)
const translateChatRef = ref<InstanceType<typeof TranslateChat> | null>(null)
const editTitle = ref('')
const editorContent = ref('')
const sections = ref<any[]>([])

// ── Tab 管理 ──
const activeTab = ref('translate')

const baseTabs: TabItem[] = [
  { id: 'translate', label: '翻译', icon: '🌐' },
  { id: 'editor', label: '编辑器', icon: '📝' },
  { id: 'outline', label: '大纲', icon: '📑' },
  { id: 'info', label: '信息', icon: 'ℹ️' },
]

const customTabs = ref<TabItem[]>([])

const tabItems = computed<TabItem[]>(() => [
  ...baseTabs,
  ...customTabs.value,
])

// 保持所有 base tab 的 DOM 存活，防止切换丢失状态（翻译对话历史、编辑器内容等）
const aliveTabs = computed(() => new Set(baseTabs.map(t => t.id)))

const editorLanguage = computed(() => {
  const ft = docStore.currentDocument?.file_type
  if (ft === 'latex' || ft === 'tex') return 'latex'
  return 'markdown'
})

let customTabCounter = 0

function addCustomTab() {
  customTabCounter++
  const id = `custom-${customTabCounter}`
  customTabs.value.push({
    id,
    label: `标签 ${customTabCounter}`,
    icon: '📋',
  })
  activeTab.value = id
}

function closeCustomTab(id: string) {
  // 只允许关闭自定义 tab，baseTabs 不可关闭
  const idx = customTabs.value.findIndex(t => t.id === id)
  if (idx === -1) return

  const wasActive = activeTab.value === id
  customTabs.value.splice(idx, 1)

  // 如果关闭的是当前激活的 tab，切换到编辑器
  if (wasActive) {
    activeTab.value = 'editor'
  }
}

// ── 内容同步 ──
function onContentChange(value: string) {
  editorContent.value = value
}

// ── 加载文档 ──
async function loadDocument(id: string) {
  const doc = await docStore.fetchDocument(id)
  if (doc) {
    editTitle.value = doc.title
    editorContent.value = doc.content
    loadSections()
  }
}

async function loadSections() {
  const docId = route.params.id as string
  if (docId) {
    sections.value = await docStore.fetchSections(docId)
  }
}

// ── 保存 ──
async function saveTitle() {
  const id = route.params.id as string
  if (id && editTitle.value !== docStore.currentDocument?.title) {
    await docStore.updateDocument(id, { title: editTitle.value })
    ui.addToast('标题已保存', 'success')
  }
}

async function saveContent() {
  const id = route.params.id as string
  if (id && editorContent.value !== docStore.currentDocument?.content) {
    await docStore.updateDocument(id, { content: editorContent.value })
    docStore.currentDocument!.content = editorContent.value
    ui.addToast('内容已保存', 'success')
    loadSections()
  }
}

// ── 文档操作 ──
async function createNew() {
  const id = await docStore.createDocument('新论文')
  ui.addToast('文档创建成功', 'success')
  router.push(`/document/${id}`)
}

function openDocument(id: string) {
  router.push(`/document/${id}`)
}

function backToList() {
  router.push('/document')
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('zh-CN', {
    year: 'numeric', month: 'short', day: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

// ── 生命周期 ──
onMounted(async () => {
  if (route.params.id) {
    loadDocument(route.params.id as string)
  } else {
    docStore.fetchDocuments()
  }
})

watch(() => route.params.id, (newId, oldId) => {
  if (newId) {
    loadDocument(newId as string)
  } else {
    docStore.currentDocument = null
    docStore.fetchDocuments()
  }
  // 切换文档时重置到翻译 tab
  if (newId !== oldId) {
    activeTab.value = 'translate'
  }
})
</script>
