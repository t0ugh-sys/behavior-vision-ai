<template>
  <el-card class="stat-card" :class="{ 'card-hover': hover }" @click="handleClick">
    <div class="card-content">
      <div class="stat-icon" :style="{ background: gradientColor }">
        <el-icon :size="iconSize">
          <component :is="icon" />
        </el-icon>
      </div>
      <div class="stat-info">
        <div class="stat-title">{{ title }}</div>
        <div class="stat-value">
          <count-up :end-val="value" :duration="2000" />
        </div>
        <div v-if="trend !== null" class="stat-trend" :class="trendClass">
          <el-icon><component :is="trendIcon" /></el-icon>
          <span>{{ Math.abs(trend) }}%</span>
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { computed } from 'vue'
import { ArrowUp, ArrowDown } from '@element-plus/icons-vue'
import CountUp from './CountUp.vue'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  value: {
    type: Number,
    default: 0
  },
  icon: {
    type: Object,
    required: true
  },
  color: {
    type: String,
    default: '#409eff'
  },
  gradient: {
    type: Array,
    default: () => ['#409eff', '#409eff']
  },
  trend: {
    type: Number,
    default: null
  },
  hover: {
    type: Boolean,
    default: true
  },
  iconSize: {
    type: Number,
    default: 32
  }
})

const emit = defineEmits(['click'])

const gradientColor = computed(() => {
  if (props.gradient && props.gradient.length === 2) {
    return `linear-gradient(135deg, ${props.gradient[0]} 0%, ${props.gradient[1]} 100%)`
  }
  return props.color
})

const trendClass = computed(() => {
  if (props.trend === null) return ''
  return props.trend >= 0 ? 'trend-up' : 'trend-down'
})

const trendIcon = computed(() => {
  return props.trend >= 0 ? ArrowUp : ArrowDown
})

const handleClick = () => {
  emit('click')
}
</script>

<style scoped>
.stat-card {
  border-radius: 12px;
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  overflow: hidden;
}

.stat-card.card-hover {
  cursor: pointer;
}

.stat-card.card-hover:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12);
}

.card-content {
  display: flex;
  align-items: center;
  padding: 8px;
}

.stat-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  border-radius: 12px;
  color: white;
  margin-right: 16px;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.stat-info {
  flex: 1;
  min-width: 0;
}

.stat-title {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
  font-weight: 500;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #303133;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-trend {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 4px;
}

.trend-up {
  color: #67c23a;
  background-color: #f0f9ff;
}

.trend-down {
  color: #f56c6c;
  background-color: #fef0f0;
}

@media (max-width: 768px) {
  .stat-icon {
    width: 48px;
    height: 48px;
  }
  
  .stat-value {
    font-size: 24px;
  }
}
</style>

