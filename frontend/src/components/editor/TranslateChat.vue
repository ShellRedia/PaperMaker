<template>
  <div class="h-full flex flex-col bg-surface-950">
    <!-- 对话历史区 -->
    <div ref="chatContainerRef" class="flex-1 overflow-auto px-4 py-4 space-y-4">
      <!-- 欢迎提示 -->
      <div
        v-if="messages.length === 0"
        ref="welcomeRef"
        class="flex flex-col items-center justify-center h-full"
      >
        <div class="w-16 h-16 mb-4 rounded-2xl bg-primary-500/15 flex items-center justify-center">
          <span class="text-3xl">🌐</span>
        </div>
        <p class="text-white text-lg font-medium mb-1">学术翻译助手</p>
        <p class="text-surface-400 text-sm text-center max-w-md">
          输入中文论文片段，AI 将先翻译为地道学术英文，
          <br />再回译中文，帮助你确认语义准确性。
        </p>
        <p class="text-surface-500 text-xs mt-4">
          请在「设置」中配置 LLM API 地址和密钥
        </p>
      </div>

      <!-- 消息列表 -->
      <div
        v-for="(msg, idx) in messages"
        :key="idx"
        ref="msgRefs"
        class="max-w-3xl mx-auto w-full space-y-3"
      >
        <!-- 用户输入 -->
        <div class="flex justify-end">
          <div
            class="max-w-[85%] bg-primary-500/15 border border-primary-500/25
                   rounded-2xl rounded-br-md px-4 py-3"
          >
            <p class="text-sm text-surface-200 whitespace-pre-wrap break-words">
              {{ msg.input }}
            </p>
          </div>
        </div>

        <!-- AI 回复 -->
        <div class="space-y-3">
          <!-- 英文结果 — 重点展示 -->
          <div
            class="bg-surface-800/80 border border-surface-700/50 rounded-2xl rounded-bl-md overflow-hidden"
          >
            <!-- 英文区头部 -->
            <div class="flex items-center justify-between px-4 py-2 bg-surface-700/30 border-b border-surface-700/50">
              <span class="text-xs font-semibold text-primary-400 uppercase tracking-wider">
                🇬🇧 English
              </span>
              <div class="flex items-center gap-1">
                <!-- 流式指示器 -->
                <span
                  v-if="msg.streaming"
                  class="flex items-center gap-1 text-xs text-amber-400"
                >
                  <span class="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />
                  生成中...
                </span>
                <!-- Token 用量标签 -->
                <span
                  v-if="msg.usage && msg.usage.total_tokens"
                  class="text-xs text-surface-500 font-mono"
                  :title="`prompt: ${msg.usage.prompt_tokens} · completion: ${msg.usage.completion_tokens}`"
                >
                  🔢 {{ msg.usage.total_tokens }} tokens
                </span>
                <AnimatedButton
                  v-if="msg.english && !msg.streaming"
                  variant="ghost"
                  size="xs"
                  @click="copyText(msg.english, '英文')"
                >
                  📋 复制
                </AnimatedButton>
              </div>
            </div>
            <!-- 英文内容 -->
            <div class="px-4 py-3">
              <p
                class="text-sm text-white leading-relaxed whitespace-pre-wrap break-words font-mono"
                v-text="msg.english || '…'"
              />
            </div>
          </div>

          <!-- 中文回译 -->
          <div
            v-if="msg.chinese"
            class="bg-surface-800/50 border border-surface-700/30 rounded-2xl rounded-bl-md overflow-hidden"
          >
            <div class="flex items-center justify-between px-4 py-2 bg-surface-700/20 border border-surface-700/30">
              <span class="text-xs font-semibold text-emerald-400 uppercase tracking-wider">
                🇨🇳 回译中文
              </span>
              <AnimatedButton
                v-if="msg.chinese && !msg.streaming"
                variant="ghost"
                size="xs"
                @click="copyText(msg.chinese, '中文')"
              >
                📋 复制
              </AnimatedButton>
            </div>
            <div class="px-4 py-3">
              <p
                class="text-sm text-surface-300 leading-relaxed whitespace-pre-wrap break-words"
                v-text="msg.chinese"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 🔍 状态指示器 — 始终可见 -->
    <div
      v-if="statusText || totalUsage.total_tokens"
      class="px-4 py-1.5 bg-surface-800 border-b border-surface-700/50 flex items-center justify-between"
    >
      <p v-if="statusText" class="text-xs font-mono" :class="statusColor">{{ statusText }}</p>
      <p v-else class="text-xs font-mono text-surface-500">
        📊 总消耗:
        <span class="text-surface-400">{{ totalUsage.total_tokens?.toLocaleString() || 0 }}</span> tokens
        <span class="text-surface-600 mx-1">·</span>
        prompt <span class="text-blue-400">{{ totalUsage.prompt_tokens?.toLocaleString() || 0 }}</span>
        <span class="text-surface-600 mx-1">·</span>
        completion <span class="text-emerald-400">{{ totalUsage.completion_tokens?.toLocaleString() || 0 }}</span>
      </p>
    </div>

    <!-- 输入区 -->
    <div class="border-t border-surface-700/50 bg-surface-900 px-4 py-3">
      <div class="max-w-3xl mx-auto flex gap-3">
        <div class="flex-1 relative">
          <textarea
            ref="inputRef"
            v-model="inputText"
            class="w-full bg-surface-800 border border-surface-700/50 rounded-xl px-4 py-3
                   text-sm text-white placeholder-surface-500 resize-none
                   focus:outline-none focus:border-primary-500/50 focus:ring-1 focus:ring-primary-500/25
                   transition-colors duration-200"
            :rows="inputRows"
            placeholder="输入中文论文文字，按 Ctrl+Enter 发送..."
            :disabled="isTranslating"
            @keydown.ctrl.enter="send"
            @keydown.escape="clearInput"
            @input="autoResize"
          />
          <!-- 字数统计 -->
          <span class="absolute right-3 bottom-2 text-xs text-surface-600">
            {{ inputText.length }} 字
          </span>
        </div>
        <div class="flex flex-col gap-2">
          <AnimatedButton
            variant="primary"
            :disabled="!inputText.trim() || isTranslating"
            @click="send"
          >
            <template #icon>➤</template>
            翻译
          </AnimatedButton>
          <button
            class="mt-1 text-xs text-surface-500 hover:text-white bg-surface-800 rounded px-2 py-1"
            @click="debugClick"
          >
            🔍调试
          </button>
          <AnimatedButton
            variant="ghost"
            size="xs"
            :disabled="messages.length === 0"
            @click="clearAll"
          >
            🗑️
          </AnimatedButton>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch } from 'vue'
import AnimatedButton from '@/components/shared/AnimatedButton.vue'
import { useUIStore } from '@/stores/ui'
import { useDocumentStore } from '@/stores/document'
import { translateApi } from '@/services/endpoints/translate'
import type { TranslateResult } from '@/services/endpoints/translate'
import type { HistoryMessage } from '@/services/endpoints/translate'
import type { TokenUsage } from '@/services/endpoints/settings'
import { animate } from '@/composables/animeAdapter'

interface ChatMessage {
  input: string
  english: string
  chinese: string
  streaming: boolean
  usage?: TokenUsage
}

const ui = useUIStore()
const docStore = useDocumentStore()

const chatContainerRef = ref<HTMLElement | null>(null)
const inputRef = ref<HTMLTextAreaElement | null>(null)
const welcomeRef = ref<HTMLElement | null>(null)
const msgRefs = ref<HTMLElement[]>([])

const inputText = ref('')
const inputRows = ref(3)
const isTranslating = ref(false)
const messages = ref<ChatMessage[]>([])
const statusText = ref('')
const statusColor = ref('text-surface-400')
const tokenCount = ref(0)
const totalUsage = ref<TokenUsage>({})

// ── 当前文档 ID ──
const documentId = computed(() => docStore.currentDocument?.id || '')

// ── 从后端加载翻译历史 ──
async function loadHistory() {
  if (!documentId.value) return
  try {
    const records = await translateApi.getHistory(documentId.value)
    const chatMessages: ChatMessage[] = []
    for (let i = 0; i < records.length; i += 2) {
      const userRecord = records[i]
      const assistantRecord = records[i + 1]
      if (!userRecord || userRecord.role !== 'user') continue
      const msg: ChatMessage = {
        input: userRecord.content,
        english: '',
        chinese: '',
        streaming: false,
      }
      if (assistantRecord && assistantRecord.role === 'assistant') {
        try {
          const parsed = JSON.parse(assistantRecord.content)
          msg.english = parsed.english || ''
          msg.chinese = parsed.chinese || ''
        } catch {
          msg.english = assistantRecord.content
        }
        if (assistantRecord.usage_json) {
          try {
            msg.usage = JSON.parse(assistantRecord.usage_json) as TokenUsage
          } catch { /* ignore */ }
        }
      }
      chatMessages.push(msg)
    }
    messages.value = chatMessages

    // 计算累计 usage
    const usage: TokenUsage = {}
    for (const m of chatMessages) {
      if (m.usage) {
        usage.prompt_tokens = (usage.prompt_tokens || 0) + (m.usage.prompt_tokens || 0)
        usage.completion_tokens = (usage.completion_tokens || 0) + (m.usage.completion_tokens || 0)
        usage.total_tokens = (usage.total_tokens || 0) + (m.usage.total_tokens || 0)
      }
    }
    totalUsage.value = usage
  } catch {
    // 加载失败时静默
  }
}

// 监听文档切换 + 初始化加载
watch(documentId, (newId, oldId) => {
  if (newId && newId !== oldId) {
    loadHistory()
  }
}, { immediate: true })

// ── 自动调整输入框高度 ──
function autoResize() {
  const lines = inputText.value.split('\n').length
  inputRows.value = Math.min(Math.max(lines, 2), 8)
}

// ── 构建对话历史 ──
function buildHistory(): HistoryMessage[] {
  const history: HistoryMessage[] = []
  for (const msg of messages.value) {
    if (msg.streaming) continue
    history.push({ role: 'user', content: msg.input })
    const assistantContent = JSON.stringify({
      english: msg.english,
      chinese: msg.chinese,
    })
    history.push({ role: 'assistant', content: assistantContent })
  }
  return history
}

// ── 格式化 token 用量文字 ──
function formatUsage(usage?: TokenUsage): string {
  if (!usage || !usage.total_tokens) return ''
  const parts: string[] = []
  if (usage.prompt_tokens) parts.push(`prompt:${usage.prompt_tokens}`)
  if (usage.completion_tokens) parts.push(`completion:${usage.completion_tokens}`)
  parts.push(`total:${usage.total_tokens}`)
  return parts.join(' · ')
}

// ── 发送翻译 ──
async function send() {
  const text = inputText.value.trim()
  if (!text || isTranslating.value) return

  // 创建消息并推入数组
  const msg: ChatMessage = {
    input: text,
    english: '',
    chinese: '',
    streaming: true,
  }
  messages.value.push(msg)
  const msgIndex = messages.value.length - 1
  inputText.value = ''
  inputRows.value = 3
  isTranslating.value = true
  statusText.value = '🔗 正在连接 LLM...'
  statusColor.value = 'text-amber-400'
  tokenCount.value = 0

  await nextTick()
  scrollToBottom()
  animateNewMessage()

  try {
    const history = buildHistory()
    statusText.value = '⏳ 正在生成翻译...'
    statusColor.value = 'text-amber-400'

    let englishBuf = ''
    for await (const chunk of translateApi.translateStream(text, history, documentId.value)) {
      if (chunk.type === 'token') {
        englishBuf += chunk.payload.token
        tokenCount.value++
        // 🔑 实时显示 token 数
        statusText.value = `⏳ 正在生成... ${tokenCount.value} tokens`
        statusColor.value = 'text-amber-400'
        messages.value[msgIndex].english = englishBuf
        await nextTick()
        scrollToBottom()
      } else if (chunk.type === 'done') {
        const result = chunk.payload as TranslateResult & { usage?: TokenUsage }
        messages.value[msgIndex].english = result.english || englishBuf
        messages.value[msgIndex].chinese = result.chinese || ''
        messages.value[msgIndex].streaming = false
        // 🔑 保存 usage 并更新累计
        if (result.usage) {
          messages.value[msgIndex].usage = result.usage
          totalUsage.value = {
            prompt_tokens: (totalUsage.value.prompt_tokens || 0) + (result.usage.prompt_tokens || 0),
            completion_tokens: (totalUsage.value.completion_tokens || 0) + (result.usage.completion_tokens || 0),
            total_tokens: (totalUsage.value.total_tokens || 0) + (result.usage.total_tokens || 0),
          }
        }
        statusText.value = ''
        statusColor.value = 'text-surface-400'
        tokenCount.value = 0
      } else if (chunk.type === 'error') {
        const errMsg = String(chunk.payload)
        messages.value[msgIndex].english = messages.value[msgIndex].english || `[错误] ${errMsg}`
        messages.value[msgIndex].streaming = false
        statusText.value = '❌ ' + errMsg
        statusColor.value = 'text-red-400'
        ui.addToast(`翻译失败: ${errMsg}`, 'error')
      }
    }

    // 流结束时如果还在 streaming 状态，手动标记完成
    if (messages.value[msgIndex].streaming) {
      messages.value[msgIndex].streaming = false
      statusText.value = ''
    }
  } catch (e: any) {
    messages.value[msgIndex].english = messages.value[msgIndex].english || `[请求失败] ${e.message}`
    messages.value[msgIndex].streaming = false
    statusText.value = '❌ 请求失败: ' + e.message
    statusColor.value = 'text-red-400'
    ui.addToast('翻译请求失败，请检查 API 配置', 'error')
  }

  isTranslating.value = false
  await nextTick()
  scrollToBottom()
}

// ── 复制 ──
async function copyText(text: string, label: string) {
  try {
    await navigator.clipboard.writeText(text)
    ui.addToast(`${label}内容已复制到剪贴板`, 'success')
  } catch {
    const ta = document.createElement('textarea')
    ta.value = text
    document.body.appendChild(ta)
    ta.select()
    document.execCommand('copy')
    document.body.removeChild(ta)
    ui.addToast(`${label}内容已复制`, 'success')
  }
}

// ── 清理 ──
function clearInput() {
  inputText.value = ''
  inputRows.value = 3
}

async function clearAll() {
  messages.value = []
  statusText.value = ''
  totalUsage.value = {}
  tokenCount.value = 0
  // 同时清空后端数据
  if (documentId.value) {
    try {
      await translateApi.clearHistory(documentId.value)
    } catch { /* ignore */ }
  }
}

// ── 滚动到底部 ──
function scrollToBottom() {
  if (chatContainerRef.value) {
    chatContainerRef.value.scrollTop = chatContainerRef.value.scrollHeight
  }
}

// ── 新消息动画 ──
function animateNewMessage() {
  if (!ui.animEnabled) return
  const container = chatContainerRef.value
  if (!container) return
  const lastMsg = container.querySelector('.max-w-3xl:last-child')
  if (lastMsg) {
    animate({
      targets: lastMsg,
      opacity: [0, 1],
      translateY: [12, 0],
      duration: 350,
      easing: 'easeOutCubic',
    })
  }
}

// ── 暴露给父组件调用的方法 ──
function translateSelection(text: string) {
  inputText.value = text
  autoResize()
  send()
}

// 🔍 调试按钮
async function debugClick() {
  const lines: string[] = []
  lines.push('origin: ' + window.location.origin)
  lines.push('inputText: ' + (inputText.value || '(空)'))
  lines.push('isTranslating: ' + isTranslating.value)
  lines.push('messages: ' + messages.value.length)

  // 测试 /health
  try {
    const r = await fetch(window.location.origin + '/health')
    const d = await r.json()
    lines.push('/health: ' + JSON.stringify(d))
  } catch (e: any) {
    lines.push('/health FAIL: ' + e.message)
  }

  // 测试 /api/settings/llm-config
  try {
    const r = await fetch(window.location.origin + '/api/settings/llm-config')
    const d = await r.json()
    lines.push('LLM配置: url=' + (d.data?.api_url || '?') + ' model=' + (d.data?.model_name || '?'))
  } catch (e: any) {
    lines.push('LLM配置 FAIL: ' + e.message)
  }

  statusText.value = lines.join(' | ')
  statusColor.value = 'text-blue-400'
  ui.addToast('调试信息已显示在状态栏', 'info')
}

defineExpose({ translateSelection, messages, clearAll })
</script>
