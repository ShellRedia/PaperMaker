<template>
  <div class="h-full flex flex-col bg-surface-950">
    <!-- 顶部栏 -->
    <TopBar />

    <div class="flex-1 flex overflow-hidden">
      <!-- 侧边导航 -->
      <Sidebar />

      <!-- 主内容区 — 页面路由过渡 -->
      <main class="flex-1 overflow-hidden relative">
        <router-view v-slot="{ Component, route }">
          <Transition
            :name="ui.animEnabled ? 'page' : ''"
            @before-enter="onPageEnter"
            @leave="onPageLeave"
          >
            <component :is="Component" :key="route.path" />
          </Transition>
        </router-view>
      </main>
    </div>

    <!-- 底部状态栏 -->
    <StatusBar />

    <!-- 全局 Toast 容器 -->
    <AnimatedToast />
  </div>
</template>

<script setup lang="ts">
import TopBar from '@/components/layout/TopBar.vue'
import Sidebar from '@/components/layout/Sidebar.vue'
import StatusBar from '@/components/layout/StatusBar.vue'
import AnimatedToast from '@/components/shared/AnimatedToast.vue'
import { useUIStore } from '@/stores/ui'
import { animate } from '@/composables/animeAdapter'

const ui = useUIStore()

function onPageEnter(el: Element) {
  if (!ui.animEnabled) return
  animate({
    targets: el,
    opacity: [0, 1],
    translateY: [16, 0],
    duration: 400,
    easing: 'easeOutCubic',
  })
}

function onPageLeave(el: Element) {
  if (!ui.animEnabled) return
  animate({
    targets: el,
    opacity: [1, 0],
    translateY: [0, -8],
    duration: 250,
    easing: 'easeInCubic',
  })
}
</script>

<style scoped>
.page-enter-active {
  transition: opacity 0.4s cubic-bezier(0.25, 0.8, 0.25, 1),
              transform 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
}
.page-enter-from {
  opacity: 0;
  transform: translateY(16px);
}
.page-leave-active {
  transition: opacity 0.25s cubic-bezier(0.55, 0, 1, 0.45),
              transform 0.25s cubic-bezier(0.55, 0, 1, 0.45);
  position: absolute;
  inset: 0;
}
.page-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
