<template>
  <div class="loading-spinner-wrapper">
    <div class="spinner" :style="spinnerStyle">
      <div class="spinner-blade" v-for="i in 12" :key="i"></div>
    </div>
    <p v-if="text" class="loading-text">{{ text }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  size: {
    type: String,
    default: 'default', // small, default, large
    validator: (value) => ['small', 'default', 'large'].includes(value)
  },
  text: {
    type: String,
    default: ''
  },
  color: {
    type: String,
    default: '#409eff'
  }
})

const spinnerStyle = computed(() => {
  const sizes = {
    small: '24px',
    default: '40px',
    large: '56px'
  }
  return {
    width: sizes[props.size],
    height: sizes[props.size]
  }
})
</script>

<style scoped>
.loading-spinner-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
}

.spinner {
  position: relative;
  margin: 0 auto;
}

.spinner-blade {
  position: absolute;
  left: 50%;
  top: 0;
  width: 6%;
  height: 25%;
  background-color: v-bind(color);
  border-radius: 50px;
  transform-origin: center 200%;
  opacity: 0.25;
  animation: spinner-fade 1.2s linear infinite;
}

.spinner-blade:nth-child(1) {
  transform: rotate(0deg);
  animation-delay: 0s;
}

.spinner-blade:nth-child(2) {
  transform: rotate(30deg);
  animation-delay: -1.1s;
}

.spinner-blade:nth-child(3) {
  transform: rotate(60deg);
  animation-delay: -1s;
}

.spinner-blade:nth-child(4) {
  transform: rotate(90deg);
  animation-delay: -0.9s;
}

.spinner-blade:nth-child(5) {
  transform: rotate(120deg);
  animation-delay: -0.8s;
}

.spinner-blade:nth-child(6) {
  transform: rotate(150deg);
  animation-delay: -0.7s;
}

.spinner-blade:nth-child(7) {
  transform: rotate(180deg);
  animation-delay: -0.6s;
}

.spinner-blade:nth-child(8) {
  transform: rotate(210deg);
  animation-delay: -0.5s;
}

.spinner-blade:nth-child(9) {
  transform: rotate(240deg);
  animation-delay: -0.4s;
}

.spinner-blade:nth-child(10) {
  transform: rotate(270deg);
  animation-delay: -0.3s;
}

.spinner-blade:nth-child(11) {
  transform: rotate(300deg);
  animation-delay: -0.2s;
}

.spinner-blade:nth-child(12) {
  transform: rotate(330deg);
  animation-delay: -0.1s;
}

@keyframes spinner-fade {
  0%, 100% {
    opacity: 0.25;
  }
  50% {
    opacity: 1;
  }
}

.loading-text {
  margin-top: 16px;
  font-size: 14px;
  color: #606266;
}
</style>

