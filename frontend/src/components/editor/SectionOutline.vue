<template>
  <div class="space-y-1">
    <h4 class="text-xs font-semibold text-surface-500 uppercase tracking-wider mb-3">
      章节大纲
    </h4>
    <div v-if="sections.length === 0" class="text-xs text-surface-500 italic">
      暂无章节结构
    </div>
    <div
      v-for="section in sections"
      :key="section.title + section.start_line"
      class="space-y-0.5"
    >
      <TreeNode :node="section" :depth="0" />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  sections: any[]
  content?: string
}>()

// ── 递归树节点组件 ──
import { defineComponent, ref, computed, h } from 'vue'
import { animate } from '@/composables/animeAdapter'

const TreeNode = defineComponent({
  name: 'TreeNode',
  props: {
    node: { type: Object, required: true },
    depth: { type: Number, default: 0 },
  },
  setup(props) {
    const expanded = ref(props.depth < 2)
    const nodeRef = ref<HTMLElement | null>(null)

    const hasChildren = computed(() =>
      props.node.children && props.node.children.length > 0
    )

    const paddingLeft = computed(() => (props.depth * 16 + 8) + 'px')

    function toggle() {
      expanded.value = !expanded.value
      if (hasChildren.value && nodeRef.value?.nextElementSibling) {
        const childContainer = nodeRef.value.nextElementSibling
        animate({
          targets: childContainer,
          height: expanded.value ? [0, childContainer.scrollHeight] : [childContainer.scrollHeight, 0],
          opacity: expanded.value ? [0, 1] : [1, 0],
          duration: 300,
          easing: 'easeOutCubic',
        })
      }
    }

    return () => {
      const children = []
      children.push(
        h('div', {
          ref: nodeRef,
          class: 'flex items-center gap-1.5 py-1 px-1 rounded cursor-pointer hover:bg-surface-700/50 text-xs transition-colors duration-150',
          style: { paddingLeft: paddingLeft.value },
          onClick: toggle,
        }, [
          hasChildren.value
            ? h('span', {
                class: 'text-surface-500 w-3 flex-shrink-0 transition-transform duration-200',
                style: { transform: expanded.value ? 'rotate(90deg)' : 'rotate(0)' },
              }, '▸')
            : h('span', { class: 'w-3 flex-shrink-0' }),
          h('span', {
            class: 'text-surface-300 truncate',
            title: props.node.title,
          }, props.node.title),
        ]),
      )

      if (hasChildren.value) {
        children.push(
          h('div', {
            class: 'overflow-hidden',
            style: { height: expanded.value ? 'auto' : '0', opacity: expanded.value ? '1' : '0' },
          }, props.node.children.map((child: any) =>
            h(TreeNode, { node: child, depth: props.depth + 1 })
          )),
        )
      }

      return h('div', children)
    }
  },
})
</script>
