<template>
  <div class="h-full overflow-auto p-6">
    <div class="max-w-2xl mx-auto space-y-8">
      <h1 class="text-2xl font-bold text-white">设置</h1>

      <!-- LLM API 配置 -->
      <section class="space-y-4">
        <h2 class="text-lg font-semibold text-white border-b border-surface-700 pb-2">
          🌐 LLM API 配置
        </h2>
        <p class="text-xs text-surface-400 -mt-2">
          配置大语言模型 API，用于学术翻译等功能。支持兼容 OpenAI 接口的服务。
        </p>

        <div class="bg-surface-800 rounded-xl p-4 space-y-4">
          <!-- API URL -->
          <div>
            <label class="block text-xs font-semibold text-surface-400 uppercase tracking-wider mb-1.5">
              API 地址
            </label>
            <input
              v-model="llmConfig.api_url"
              class="w-full bg-surface-900 border border-surface-700/50 rounded-lg px-3 py-2
                     text-sm text-white placeholder-surface-500
                     focus:outline-none focus:border-primary-500/50 transition-colors"
              placeholder="https://api.openai.com"
              @blur="saveLLMConfig"
            />
            <p class="text-xs text-surface-500 mt-1">
              例如: https://api.openai.com 或其他兼容接口
            </p>
          </div>

          <!-- API Key -->
          <div>
            <label class="block text-xs font-semibold text-surface-400 uppercase tracking-wider mb-1.5">
              API Key
            </label>
            <div class="relative">
              <input
                v-model="llmConfig.api_key"
                :type="showKey ? 'text' : 'password'"
                class="w-full bg-surface-900 border border-surface-700/50 rounded-lg px-3 py-2 pr-10
                       text-sm text-white placeholder-surface-500
                       focus:outline-none focus:border-primary-500/50 transition-colors"
                placeholder="sk-..."
                @blur="saveLLMConfig"
              />
              <button
                class="absolute right-2 top-1/2 -translate-y-1/2 text-surface-500 hover:text-surface-300
                       text-xs transition-colors"
                @click="showKey = !showKey"
              >
                {{ showKey ? '🙈' : '👁️' }}
              </button>
            </div>
          </div>

          <!-- 模型名称 -->
          <div>
            <label class="block text-xs font-semibold text-surface-400 uppercase tracking-wider mb-1.5">
              模型名称
            </label>
            <input
              v-model="llmConfig.model_name"
              class="w-full bg-surface-900 border border-surface-700/50 rounded-lg px-3 py-2
                     text-sm text-white placeholder-surface-500
                     focus:outline-none focus:border-primary-500/50 transition-colors"
              placeholder="gpt-4o"
              @blur="saveLLMConfig"
            />
            <p class="text-xs text-surface-500 mt-1">
              默认: gpt-4o。支持 gpt-4o-mini, deepseek-chat, claude-3-opus 等
            </p>
          </div>

          <!-- 保存状态 -->
          <div class="flex items-center justify-between pt-2 border-t border-surface-700/50">
            <span class="text-xs" :class="saveStatusClass">{{ saveStatusText }}</span>
            <AnimatedButton variant="primary" size="sm" @click="saveLLMConfig">
              💾 保存配置
            </AnimatedButton>
          </div>
        </div>
      </section>

      <!-- 外观 -->
      <section class="space-y-4">
        <h2 class="text-lg font-semibold text-white border-b border-surface-700 pb-2">外观</h2>

        <div class="flex items-center justify-between bg-surface-800 rounded-xl p-4">
          <div>
            <div class="text-white text-sm font-medium">主题模式</div>
            <div class="text-xs text-surface-400 mt-0.5">{{ ui.theme === 'dark' ? '暗色' : '亮色' }}</div>
          </div>
          <button
            class="w-12 h-6 rounded-full transition-colors duration-200 relative"
            :class="ui.theme === 'dark' ? 'bg-primary-500' : 'bg-surface-600'"
            @click="ui.toggleTheme()"
          >
            <span
              class="absolute top-0.5 w-5 h-5 rounded-full bg-white shadow transition-transform duration-200"
              :class="ui.theme === 'dark' ? 'translate-x-6' : 'translate-x-0.5'"
            />
          </button>
        </div>

        <div class="flex items-center justify-between bg-surface-800 rounded-xl p-4">
          <div>
            <div class="text-white text-sm font-medium">动画效果</div>
            <div class="text-xs text-surface-400 mt-0.5">控制界面动画的开关</div>
          </div>
          <button
            class="w-12 h-6 rounded-full transition-colors duration-200 relative"
            :class="ui.animEnabled ? 'bg-primary-500' : 'bg-surface-600'"
            @click="ui.toggleAnim()"
          >
            <span
              class="absolute top-0.5 w-5 h-5 rounded-full bg-white shadow transition-transform duration-200"
              :class="ui.animEnabled ? 'translate-x-6' : 'translate-x-0.5'"
            />
          </button>
        </div>
      </section>

      <!-- ML 模型 -->
      <section class="space-y-4">
        <h2 class="text-lg font-semibold text-white border-b border-surface-700 pb-2">ML 模型</h2>

        <div
          v-for="model in modelStore.models"
          :key="model.name"
          class="bg-surface-800 rounded-xl p-4 flex items-center justify-between"
        >
          <div>
            <div class="text-white text-sm font-medium">{{ model.description }}</div>
            <div class="text-xs text-surface-400 mt-0.5">
              {{ model.name }}
              <span class="ml-2 px-1.5 py-0.5 rounded text-xs"
                    :class="model.status === 'available' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-amber-500/20 text-amber-400'">
                {{ model.status }}
              </span>
            </div>
          </div>
          <button
            class="text-sm text-primary-400 hover:text-primary-300 transition-colors"
            @click="modelStore.activeModel = model.name"
          >
            {{ modelStore.activeModel === model.name ? '✓ 当前' : '选择' }}
          </button>
        </div>
      </section>

      <!-- 关于 -->
      <section class="space-y-4">
        <h2 class="text-lg font-semibold text-white border-b border-surface-700 pb-2">关于</h2>
        <div class="bg-surface-800 rounded-xl p-4 text-sm text-surface-400 space-y-1">
          <p>PaperMaker v0.1.0</p>
          <p>深度学习论文写作助手</p>
          <p class="text-surface-500 mt-2">
            前端: Vue 3 + Anime.js + ECharts + Fabric.js<br/>
            后端: FastAPI + ONNX Runtime + spaCy<br/>
            桌面: pywebview (Edge WebView2) + PyInstaller
          </p>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useUIStore } from '@/stores/ui'
import { useModelStore } from '@/stores/model'
import { settingsApi } from '@/services/endpoints/settings'
import type { LLMConfig } from '@/services/endpoints/settings'
import AnimatedButton from '@/components/shared/AnimatedButton.vue'

const ui = useUIStore()
const modelStore = useModelStore()

const showKey = ref(false)
const saveStatus = ref<'idle' | 'saving' | 'saved' | 'error'>('idle')

const llmConfig = reactive<LLMConfig>({
  api_url: '',
  api_key: '',
  model_name: '',
})

const saveStatusText = computed(() => {
  switch (saveStatus.value) {
    case 'saving': return '保存中...'
    case 'saved': return '✓ 已保存'
    case 'error': return '✗ 保存失败'
    default: return ''
  }
})

const saveStatusClass = computed(() => {
  switch (saveStatus.value) {
    case 'saved': return 'text-emerald-400'
    case 'error': return 'text-red-400'
    default: return 'text-surface-500'
  }
})

let saveTimer: ReturnType<typeof setTimeout> | null = null

async function saveLLMConfig() {
  saveStatus.value = 'saving'
  try {
    await settingsApi.updateLLMConfig({
      api_url: llmConfig.api_url,
      api_key: llmConfig.api_key,
      model_name: llmConfig.model_name,
    })
    saveStatus.value = 'saved'
  } catch (e) {
    saveStatus.value = 'error'
  }
  // 3秒后恢复
  if (saveTimer) clearTimeout(saveTimer)
  saveTimer = setTimeout(() => { saveStatus.value = 'idle' }, 3000)
}

onMounted(async () => {
  modelStore.fetchModels()
  try {
    const config = await settingsApi.getLLMConfig()
    if (config) {
      llmConfig.api_url = config.api_url || ''
      llmConfig.api_key = config.api_key || ''
      llmConfig.model_name = config.model_name || ''
    }
  } catch {
    // 后端可能还没启动
  }
})
</script>
