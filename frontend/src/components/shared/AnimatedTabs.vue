<template>
  <div class="flex flex-col h-full">
    <!-- Tab 栏 -->
    <div
      ref="tabsBarRef"
      class="flex items-center bg-surface-900 border-b border-surface-700/50 overflow-x-auto"
      :class="compact ? 'px-2 py-0' : 'px-3 py-0'"
    >
      <div class="flex items-center gap-0.5 flex-1 min-w-0">
        <button
          v-for="(tab, index) in tabs"
          :key="tab.id"
          :ref="el => setTabRef(tab.id, el as HTMLElement)"
          class="group relative flex items-center gap-1.5 px-3 py-2 text-sm rounded-t-md
                 whitespace-nowrap select-none transition-colors duration-150
                 flex-shrink-0 max-w-[180px]"
          :class="tab.id === modelValue
            ? 'text-primary-400 bg-surface-800'
            : 'text-surface-400 hover:text-white hover:bg-surface-800/50'"
          @click="selectTab(tab.id)"
        >
          <span class="text-sm flex-shrink-0">{{ tab.icon }}</span>
          <span class="truncate text-xs font-medium">{{ tab.label }}</span>
          <!-- 关闭按钮 -->
          <span
            v-if="closable && tabs.length > 1"
            class="flex-shrink-0 w-4 h-4 flex items-center justify-center rounded
                   text-surface-500 hover:text-white hover:bg-surface-600/50
                   opacity-0 group-hover:opacity-100 transition-opacity duration-150"
            @click.stop="closeTab(tab.id)"
          >
            ✕
          </span>
        </button>
      </div>

      <!-- 添加 Tab 按钮 -->
      <button
        v-if="addable"
        class="flex-shrink-0 flex items-center justify-center w-7 h-7 ml-1 rounded
               text-surface-500 hover:text-white hover:bg-surface-700
               transition-colors duration-150"
        title="新建标签页"
        @click="$emit('add')"
      >
        <span class="text-base leading-none">+</span>
      </button>
    </div>

    <!-- Tab 内容区 -->
    <div ref="panelContainerRef" class="flex-1 overflow-hidden relative">
      <div
        v-for="tab in tabs"
        :key="tab.id"
        :ref="el => setPanelRef(tab.id, el as HTMLElement)"
        class="absolute inset-0 overflow-auto"
        :class="tab.id === modelValue ? '' : 'pointer-events-none'"
        :style="{
          visibility: tab.id === modelValue ? 'visible' : 'hidden',
        }"
      >
        <slot
          v-if="tab.id === modelValue || keepAlive.has(tab.id)"
          name="panel"
          :tab="tab"
          :active="tab.id === modelValue"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch, onMounted, nextTick } from 'vue'
import { animate } from '@/composables/animeAdapter'
import { useUIStore } from '@/stores/ui'

export interface TabItem {
  id: string
  label: string
  icon?: string
  /** 自定义数据，透传给 panel 插槽 */
  data?: any
}

const props = withDefaults(defineProps<{
  /** 当前激活的 tab id */
  modelValue: string
  /** tab 列表 */
  tabs: TabItem[]
  /** 是否可关闭 */
  closable?: boolean
  /** 是否可添加 */
  addable?: boolean
  /** 紧凑模式 */
  compact?: boolean
  /** 保持不活跃 tab 的 DOM */
  keepAlive?: Set<string>
}>(), {
  closable: true,
  addable: true,
  compact: false,
  keepAlive: () => new Set(),
})

const emit = defineEmits<{
  'update:modelValue': [id: string]
  'add': []
  'close': [id: string]
}>()

const ui = useUIStore()
const tabsBarRef = ref<HTMLElement | null>(null)
const panelContainerRef = ref<HTMLElement | null>(null)

// 存储 DOM 引用
const tabRefs = reactive<Record<string, HTMLElement>>({})
const panelRefs = reactive<Record<string, HTMLElement>>({})

function setTabRef(id: string, el: HTMLElement | null) {
  if (el) tabRefs[id] = el
}

function setPanelRef(id: string, el: HTMLElement | null) {
  if (el) panelRefs[id] = el
}

// ── 切换 Tab（带动画） ──
function selectTab(id: string) {
  if (id === props.modelValue) return

  const oldPanel = panelRefs[props.modelValue]
  const newPanel = panelRefs[id]
  const oldTab = tabRefs[props.modelValue]
  const newTab = tabRefs[id]

  emit('update:modelValue', id)

  if (!ui.animEnabled) return

  // 面板交叉淡入淡出
  if (oldPanel && newPanel) {
    animate({
      targets: oldPanel,
      opacity: [1, 0],
      translateX: [0, -12],
      duration: 200,
      easing: 'easeOutCubic',
    })
    animate({
      targets: newPanel,
      opacity: [0, 1],
      translateX: [12, 0],
      duration: 280,
      easing: 'easeOutCubic',
    })
  }
}

// ── 关闭 Tab ──
function closeTab(id: string) {
  emit('close', id)
}
</script>
