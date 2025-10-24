<template>
  <div class="empty-state">
    <div class="empty-icon">
      <el-icon :size="iconSize">
        <component :is="iconComponent" />
      </el-icon>
    </div>
    <p class="empty-title">{{ title }}</p>
    <p v-if="description" class="empty-description">{{ description }}</p>
    <slot name="action"></slot>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Box, Document, Picture, VideoCamera, Bell, User } from '@element-plus/icons-vue'

const props = defineProps({
  type: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'data', 'image', 'video', 'alert', 'user'].includes(value)
  },
  title: {
    type: String,
    default: '暂无数据'
  },
  description: {
    type: String,
    default: ''
  },
  iconSize: {
    type: Number,
    default: 80
  }
})

const iconComponent = computed(() => {
  const icons = {
    default: Box,
    data: Document,
    image: Picture,
    video: VideoCamera,
    alert: Bell,
    user: User
  }
  return icons[props.type] || Box
})
</script>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.empty-icon {
  color: #dcdfe6;
  margin-bottom: 20px;
  opacity: 0.6;
}

.empty-title {
  font-size: 16px;
  color: #909399;
  margin-bottom: 8px;
  font-weight: 500;
}

.empty-description {
  font-size: 14px;
  color: #c0c4cc;
  margin-bottom: 20px;
  max-width: 400px;
  line-height: 1.6;
}
</style>

