<template>
  <span>{{ displayValue }}</span>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'

const props = defineProps({
  endVal: {
    type: Number,
    required: true
  },
  duration: {
    type: Number,
    default: 2000
  },
  decimals: {
    type: Number,
    default: 0
  }
})

const displayValue = ref(0)

const animate = () => {
  const startVal = displayValue.value
  const endVal = props.endVal
  const duration = props.duration
  const startTime = Date.now()
  
  const step = () => {
    const now = Date.now()
    const elapsed = now - startTime
    const progress = Math.min(elapsed / duration, 1)
    
    // 缓动函数（easeOutExpo）
    const easeProgress = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress)
    
    displayValue.value = Math.floor(startVal + (endVal - startVal) * easeProgress)
    
    if (progress < 1) {
      requestAnimationFrame(step)
    } else {
      displayValue.value = endVal
    }
  }
  
  requestAnimationFrame(step)
}

onMounted(() => {
  animate()
})

watch(() => props.endVal, () => {
  animate()
})
</script>

