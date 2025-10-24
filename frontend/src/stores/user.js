import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const userInfo = ref(null)
  const token = ref(null)

  function setUserInfo(info) {
    userInfo.value = info.user || info
    // 如果返回数据中包含token，保存它
    if (info.token) {
      token.value = info.token
      localStorage.setItem('token', info.token)
    }
    localStorage.setItem('user', JSON.stringify(userInfo.value))
  }

  function getUserInfo() {
    if (!userInfo.value) {
      const stored = localStorage.getItem('user')
      if (stored) {
        userInfo.value = JSON.parse(stored)
      }
    }
    if (!token.value) {
      const storedToken = localStorage.getItem('token')
      if (storedToken) {
        token.value = storedToken
      }
    }
    return userInfo.value
  }

  function clearUserInfo() {
    userInfo.value = null
    token.value = null
    localStorage.removeItem('user')
    localStorage.removeItem('token')
  }

  function getToken() {
    if (!token.value) {
      token.value = localStorage.getItem('token')
    }
    return token.value
  }

  return {
    userInfo,
    token,
    setUserInfo,
    getUserInfo,
    clearUserInfo,
    getToken
  }
})

