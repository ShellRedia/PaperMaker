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
      <template v-for="(msg, idx) in messages" :key="idx">
        <!-- 上下文分割线 -->
        <div
          v-if="msg.isDivider"
          ref="msgRefs"
          class="max-w-3xl mx-auto w-full flex items-center gap-3 py-3"
        >
          <div class="flex-1 h-px bg-surface-600/40" />
          <div class="flex items-center gap-2 px-3 py-1 rounded-full bg-surface-800/60 border border-surface-600/30">
            <span class="text-xs text-surface-400">🆕</span>
            <span class="text-xs text-surface-400 whitespace-nowrap">上下文已清空 — 以下为新对话</span>
          </div>
          <div class="flex-1 h-px bg-surface-600/40" />
        </div>

        <!-- 正常消息 -->
        <div
          v-else
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

          <!-- AI 回复：原文 + 各变体 -->
          <div class="space-y-3">
            <!-- ═══ 原版翻译 ═══ -->
            <TranslationBlock
              :english="msg.english"
              :chinese="msg.chinese"
              :streaming="msg.streaming"
              :usage="msg.usage"
              :show-copy="!msg.streaming"
              :show-refine-buttons="!msg.streaming && !!msg.english"
              :refining="msg.refining"
              :refine-done-modes="msg.refines.filter(r => !r.streaming).map(r => r.mode)"
              @copy-english="copyText(msg.english, '英文')"
              @copy-chinese="copyText(msg.chinese, '中文')"
              @refine="(mode: string) => refineMessage(idx, mode as 'concise' | 'academic')"
            />

            <!-- ═══ 优化变体（追加在下方） ═══ -->
            <TranslationBlock
              v-for="(variant, vi) in msg.refines"
              :key="vi"
              :label="variant.label"
              :english="variant.english"
              :chinese="variant.chinese"
              :streaming="variant.streaming"
              :usage="variant.usage"
              :show-copy="!variant.streaming && !!variant.english"
              label-class="bg-cyan-500/20 text-cyan-400 border-cyan-500/30"
              english-label="🇬🇧 English"
              chinese-label="🇨🇳 回译中文"
            />
          </div>
        </div>
      </template>
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

    <!-- 📐 翻译规则面板 — 可折叠 -->
    <div class="border-t border-surface-700/50 bg-surface-900">
      <button
        class="w-full flex items-center justify-between px-4 py-2 hover:bg-surface-800/50 transition-colors"
        @click="rulesExpanded = !rulesExpanded"
      >
        <span class="text-xs font-semibold text-surface-400 uppercase tracking-wider">
          📐 翻译规则
          <span class="text-surface-600 ml-1">({{ rules.length }})</span>
        </span>
        <span class="text-xs text-surface-500 transition-transform" :class="{ 'rotate-180': rulesExpanded }">
          ▼
        </span>
      </button>

      <div
        v-show="rulesExpanded"
        class="px-4 pb-3 space-y-2"
      >
        <p class="text-xs text-surface-500 leading-relaxed">
          设置固定的翻译规则：特定中文名词翻译为固定含义，或保持某些缩写不翻译。
        </p>

        <div
          v-for="(rule, ri) in rules"
          :key="rule.id"
          class="flex items-center gap-2"
        >
          <select
            v-model="rule.rule_type"
            class="bg-surface-800 border border-surface-700 rounded text-xs text-surface-300 px-2 py-1.5
                   focus:outline-none focus:border-primary-500/50 shrink-0"
          >
            <option value="replace">翻译为</option>
            <option value="no_translate">保持原样</option>
          </select>
          <input
            v-model="rule.pattern"
            type="text"
            placeholder="原文（如：注意力机制）"
            class="flex-1 bg-surface-800 border border-surface-700 rounded text-sm text-white px-2 py-1.5
                   placeholder-surface-600 focus:outline-none focus:border-primary-500/50 min-w-0"
          />
          <input
            v-if="rule.rule_type === 'replace'"
            v-model="rule.replacement"
            type="text"
            placeholder="译文（如：attention mechanism）"
            class="flex-1 bg-surface-800 border border-surface-700 rounded text-sm text-white px-2 py-1.5
                   placeholder-surface-600 focus:outline-none focus:border-primary-500/50 min-w-0"
          />
          <button
            class="shrink-0 text-surface-500 hover:text-red-400 text-sm px-1 transition-colors"
            @click="removeRule(ri)"
            title="删除此规则"
          >
            ✕
          </button>
        </div>

        <div class="flex items-center gap-2 pt-1">
          <button
            class="text-xs text-primary-400 hover:text-primary-300 border border-primary-500/30 hover:border-primary-500/50
                   rounded px-3 py-1.5 transition-colors"
            @click="addRule"
          >
            ＋ 添加规则
          </button>
          <button
            v-if="rulesDirty"
            class="text-xs text-emerald-400 hover:text-emerald-300 bg-emerald-500/15 border border-emerald-500/30
                   rounded px-3 py-1.5 transition-colors"
            @click="saveRules"
          >
            保存规则
          </button>
          <span v-if="rulesSaving" class="text-xs text-amber-400">保存中...</span>
          <span v-if="rulesSaved" class="text-xs text-emerald-400">✓ 已保存</span>
        </div>
      </div>
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
            v-if="messages.length > 0"
            class="text-xs text-surface-400 hover:text-amber-400 border border-surface-600/40 hover:border-amber-500/50
                   rounded px-2 py-1 transition-colors"
            title="清空LLM对话记忆（不删除页面内容）"
            @click="resetContext"
          >
            🆕 清空上下文
          </button>
          <button
            class="mt-1 text-xs text-surface-500 hover:text-white bg-surface-800 rounded px-2 py-1"
            @click="debugClick"
          >
            🔍调试
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch } from 'vue'
import AnimatedButton from '@/components/shared/AnimatedButton.vue'
import TranslationBlock from './TranslationBlock.vue'
import { useUIStore } from '@/stores/ui'
import { useDocumentStore } from '@/stores/document'
import { translateApi } from '@/services/endpoints/translate'
import type { TranslateResult } from '@/services/endpoints/translate'
import type { HistoryMessage } from '@/services/endpoints/translate'
import type { TranslationRuleItem } from '@/services/endpoints/translate'
import type { TokenUsage } from '@/services/endpoints/settings'
import { animate } from '@/composables/animeAdapter'

interface RefineVariant {
  label: string
  mode: 'concise' | 'academic'
  english: string
  chinese: string
  streaming: boolean
  usage?: TokenUsage
}

interface ChatMessage {
  input: string
  english: string
  chinese: string
  streaming: boolean
  refining?: boolean
  usage?: TokenUsage
  refines: RefineVariant[]
  isDivider?: boolean  // 上下文清空分割线
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

// ── 翻译规则状态 ──
const rulesExpanded = ref(false)
const rules = ref<TranslationRuleItem[]>([])
const rulesDirty = ref(false)
const rulesSaving = ref(false)
const rulesSaved = ref(false)

// ── 当前文档 ID ──
const documentId = computed(() => docStore.currentDocument?.id || '')

// ── 加载翻译规则 ──
async function loadRules() {
  try {
    const config = await translateApi.getRules()
    rules.value = config.rules || []
    rulesDirty.value = false
  } catch (e: any) {
    console.error('[TranslateChat] 加载翻译规则失败:', e.message || e)
  }
}

async function saveRules() {
  rulesSaving.value = true
  rulesSaved.value = false
  try {
    await translateApi.saveRules({ rules: rules.value })
    rulesDirty.value = false
    rulesSaved.value = true
    setTimeout(() => { rulesSaved.value = false }, 2000)
  } catch (e: any) {
    ui.addToast(`保存规则失败: ${e.message || e}`, 'error')
  } finally {
    rulesSaving.value = false
  }
}

function addRule() {
  rules.value.push({
    id: crypto.randomUUID?.() || Date.now().toString(36) + Math.random().toString(36).slice(2),
    pattern: '',
    replacement: '',
    rule_type: 'replace',
  })
  rulesDirty.value = true
}

function removeRule(index: number) {
  rules.value.splice(index, 1)
  rulesDirty.value = true
}

watch(rules, () => {
  rulesDirty.value = true
}, { deep: true })

loadRules()

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
        refines: [],
      }
      if (assistantRecord && assistantRecord.role === 'assistant') {
        try {
          const parsed = JSON.parse(assistantRecord.content)
          msg.english = parsed.english || ''
          msg.chinese = parsed.chinese || ''
          // 恢复优化变体
          if (parsed.refines && Array.isArray(parsed.refines)) {
            msg.refines = parsed.refines.map((r: any) => ({
              label: r.label || '',
              mode: r.mode || 'concise',
              english: r.english || '',
              chinese: r.chinese || '',
              streaming: false,
              usage: r.usage || undefined,
            }))
          }
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

    const usage: TokenUsage = {}
    for (const m of chatMessages) {
      if (m.usage) {
        usage.prompt_tokens = (usage.prompt_tokens || 0) + (m.usage.prompt_tokens || 0)
        usage.completion_tokens = (usage.completion_tokens || 0) + (m.usage.completion_tokens || 0)
        usage.total_tokens = (usage.total_tokens || 0) + (m.usage.total_tokens || 0)
      }
    }
    totalUsage.value = usage
  } catch (e: any) {
    console.error('[TranslateChat] 加载历史失败:', e.message || e)
  }
}

watch(documentId, (newId, oldId) => {
  if (newId && newId !== oldId) {
    loadHistory()
  }
}, { immediate: true })

function autoResize() {
  const lines = inputText.value.split('\n').length
  inputRows.value = Math.min(Math.max(lines, 2), 8)
}

function buildHistory(): HistoryMessage[] {
  const history: HistoryMessage[] = []
  for (const msg of messages.value) {
    if (msg.isDivider) {
      // 分割线之后只包含后续消息作为上下文
      continue
    }
    if (msg.streaming || msg.refining) continue
    history.push({ role: 'user', content: msg.input })
    history.push({ role: 'assistant', content: JSON.stringify({ english: msg.english, chinese: msg.chinese }) })
  }
  return history
}

// ── 发送翻译 ──
async function send() {
  const text = inputText.value.trim()
  if (!text || isTranslating.value) return

  const msg: ChatMessage = {
    input: text,
    english: '',
    chinese: '',
    streaming: true,
    refines: [],
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

// ── 优化（精简/学术化）—— 追加在原版下方 ──
async function refineMessage(msgIndex: number, mode: 'concise' | 'academic') {
  if (msgIndex < 0 || msgIndex >= messages.value.length) return
  const targetMsg = messages.value[msgIndex]
  if (!targetMsg.english || targetMsg.streaming || targetMsg.refining) return

  const modeLabel = mode === 'concise' ? '精简版' : '学术版'

  // 创建优化变体，追加到 refines 数组
  const variant: RefineVariant = {
    label: modeLabel,
    mode,
    english: '',
    chinese: '',
    streaming: true,
  }
  targetMsg.refines.push(variant)
  const variantIndex = targetMsg.refines.length - 1
  targetMsg.refining = true
  isTranslating.value = true
  statusText.value = mode === 'concise' ? '✂️ 正在精简...' : '🎓 正在学术化...'
  statusColor.value = 'text-cyan-400'
  tokenCount.value = 0

  await nextTick()
  scrollToBottom()

  try {
    let englishBuf = ''
    for await (const chunk of translateApi.refineStream(targetMsg.input, targetMsg.english, mode)) {
      if (chunk.type === 'token') {
        englishBuf += chunk.payload.token
        tokenCount.value++
        statusText.value = `⏳ 正在优化... ${tokenCount.value} tokens`
        targetMsg.refines[variantIndex].english = englishBuf
        await nextTick()
        scrollToBottom()
      } else if (chunk.type === 'done') {
        const result = chunk.payload
        targetMsg.refines[variantIndex].english = result.english || englishBuf
        targetMsg.refines[variantIndex].chinese = result.chinese || ''
        targetMsg.refines[variantIndex].streaming = false
        targetMsg.refines[variantIndex].usage = result.usage
        targetMsg.refining = false
        if (result.usage) {
          totalUsage.value = {
            prompt_tokens: (totalUsage.value.prompt_tokens || 0) + (result.usage.prompt_tokens || 0),
            completion_tokens: (totalUsage.value.completion_tokens || 0) + (result.usage.completion_tokens || 0),
            total_tokens: (totalUsage.value.total_tokens || 0) + (result.usage.total_tokens || 0),
          }
        }
        statusText.value = ''
        statusColor.value = 'text-surface-400'
        tokenCount.value = 0
        ui.addToast(`已完成${modeLabel}优化`, 'success')
      } else if (chunk.type === 'error') {
        targetMsg.refines[variantIndex].streaming = false
        targetMsg.refining = false
        statusText.value = '❌ ' + String(chunk.payload)
        statusColor.value = 'text-red-400'
        ui.addToast(`优化失败: ${chunk.payload}`, 'error')
      }
    }

    if (targetMsg.refines[variantIndex]?.streaming) {
      targetMsg.refines[variantIndex].streaming = false
      targetMsg.refining = false
      statusText.value = ''
    }
  } catch (e: any) {
    if (targetMsg.refines[variantIndex]) {
      targetMsg.refines[variantIndex].streaming = false
    }
    targetMsg.refining = false
    statusText.value = '❌ 优化失败: ' + e.message
    statusColor.value = 'text-red-400'
    ui.addToast('优化请求失败，请检查 API 配置', 'error')
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

function clearInput() {
  inputText.value = ''
  inputRows.value = 3
}

// ── 清空上下文：插入分割线，后续翻译不再使用之前的对话历史 ──
function resetContext() {
  // 插入一条分割线标记
  messages.value.push({
    input: '',
    english: '',
    chinese: '',
    streaming: false,
    refines: [],
    isDivider: true,
  })
  scrollToBottom()
  ui.addToast('上下文已清空 — 之后的翻译将不带之前的历史记忆', 'info')
}

// ── 完全清空：删除所有消息和历史 ──
async function clearAll() {
  messages.value = []
  statusText.value = ''
  totalUsage.value = {}
  tokenCount.value = 0
  if (documentId.value) {
    try { await translateApi.clearHistory(documentId.value) } catch { /* ignore */ }
  }
}

function scrollToBottom() {
  if (chatContainerRef.value) {
    chatContainerRef.value.scrollTop = chatContainerRef.value.scrollHeight
  }
}

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

  try {
    const r = await fetch(window.location.origin + '/health')
    const d = await r.json()
    lines.push('/health: ' + JSON.stringify(d))
  } catch (e: any) {
    lines.push('/health FAIL: ' + e.message)
  }

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