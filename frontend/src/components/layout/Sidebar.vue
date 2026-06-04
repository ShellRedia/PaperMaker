<template>
  <aside
    ref="sidebarRef"
    class="flex flex-col shrink-0 bg-surface-900 border-r border-surface-700/50
           transition-none overflow-hidden"
    :style="{ width: sidebarWidth + 'px' }"
  >
    <!-- 导航菜单 -->
    <nav class="flex-1 py-2 px-2 space-y-1">
      <router-link
        v-for="item in navItems"
        :key="item.to"
        :to="item.to"
        class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm
               transition-colors duration-200 group overflow-hidden whitespace-nowrap"
        :class="isActive(item.to)
          ? 'bg-primary-500/15 text-primary-400 border-l-2 border-primary-500'
          : 'text-surface-400 hover:text-white hover:bg-surface-800 border-l-2 border-transparent'"
        @click="handleNavClick"
      >
        <span class="flex-shrink-0 text-lg w-6 text-center">{{ item.icon }}</span>
        <span
          ref="labelRefs"
          class="flex-1 text-sm"
          :class="{ 'opacity-0': ui.sidebar === 'collapsed' }"
        >{{ item.label }}</span>
      </router-link>
    </nav>

    <!-- 底部版本信息 -->
    <div
      class="px-4 py-3 border-t border-surface-700/50"
      :class="{ 'text-center': ui.sidebar === 'collapsed' }"
    >
      <span class="text-xs text-surface-500 whitespace-nowrap">
        v0.1.0
      </span>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useUIStore } from '@/stores/ui'

const route = useRoute()
const ui = useUIStore()
const sidebarRef = ref<HTMLElement | null>(null)

const sidebarWidth = computed(() =>
  ui.sidebar === 'expanded' ? 240 : 64
)

const navItems = [
  { to: '/', icon: '🏠', label: '首页' },
  { to: '/document', icon: '📄', label: '文档编辑' },
  { to: '/annotation', icon: '🏷️', label: '数据标注' },
  { to: '/statistics', icon: '📊', label: '统计图表' },
  { to: '/polish', icon: '✨', label: '文本润色' },
  { to: '/settings', icon: '⚙️', label: '设置' },
]

function isActive(to: string) {
  if (to === '/') return route.path === '/'
  return route.path.startsWith(to)
}

function handleNavClick() {
  // 窄屏时可以自动折叠
}
</script>
