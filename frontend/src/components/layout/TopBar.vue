<template>
  <header
    class="flex items-center justify-between h-12 px-4
           bg-surface-900 border-b border-surface-700/50 select-none
           shrink-0"
    style="-webkit-app-region: drag"
  >
    <!-- 左侧 -->
    <div class="flex items-center gap-3" style="-webkit-app-region: no-drag">
      <button
        class="p-1.5 rounded-lg hover:bg-surface-700 text-surface-400 hover:text-white transition-colors"
        @click="ui.toggleSidebar()"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>

      <div class="flex items-center gap-2">
        <span class="text-lg">📝</span>
        <span class="font-semibold text-white text-sm tracking-wide">
          PaperMaker
        </span>
      </div>
    </div>

    <!-- 中间 — 面包屑 / 文档标题 -->
    <div class="flex-1 flex justify-center" style="-webkit-app-region: no-drag">
      <span
        v-if="docTitle"
        class="text-sm text-surface-400 truncate max-w-[400px]"
        v-anime:fadeIn
      >
        {{ docTitle }}
      </span>
    </div>

    <!-- 右侧 -->
    <div class="flex items-center gap-1" style="-webkit-app-region: no-drag">
      <!-- 主题切换 -->
      <button
        class="p-1.5 rounded-lg hover:bg-surface-700 text-surface-400 hover:text-white transition-colors"
        title="切换主题"
        @click="ui.toggleTheme()"
      >
        <svg v-if="ui.theme === 'dark'" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
        </svg>
        <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
        </svg>
      </button>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useUIStore } from '@/stores/ui'
import { useDocumentStore } from '@/stores/document'

const ui = useUIStore()
const docStore = useDocumentStore()

const docTitle = computed(() => docStore.currentDocument?.title || '')
</script>
