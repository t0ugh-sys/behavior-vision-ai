import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAlertStore = defineStore('alert', () => {
  const alerts = ref([])
  const unreadCount = ref(0)

  function addAlert(alert) {
    alerts.value.unshift(alert)
    unreadCount.value++
  }

  function clearAlerts() {
    alerts.value = []
    unreadCount.value = 0
  }

  function markAsRead() {
    unreadCount.value = 0
  }

  return {
    alerts,
    unreadCount,
    addAlert,
    clearAlerts,
    markAsRead
  }
})

