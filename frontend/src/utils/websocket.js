import SockJS from 'sockjs-client'
import Stomp from 'stompjs'

class WebSocketService {
  constructor() {
    this.stompClient = null
    this.connected = false
    this.subscriptions = new Map()
  }

  /**
   * 连接WebSocket
   */
  connect(userId, onMessageCallback) {
    return new Promise((resolve, reject) => {
      const socket = new SockJS('http://localhost:8080/api/ws')
      this.stompClient = Stomp.over(socket)
      
      // 关闭控制台日志
      this.stompClient.debug = null
      
      this.stompClient.connect(
        {},
        frame => {
          console.log('WebSocket连接成功:', frame)
          this.connected = true
          
          // 订阅个人告警通道
          this.subscribe(`/topic/alerts/${userId}`, onMessageCallback)
          
          resolve()
        },
        error => {
          console.error('WebSocket连接失败:', error)
          this.connected = false
          reject(error)
        }
      )
    })
  }

  /**
   * 订阅主题
   */
  subscribe(topic, callback) {
    if (!this.stompClient || !this.connected) {
      console.error('WebSocket未连接')
      return
    }

    const subscription = this.stompClient.subscribe(topic, message => {
      try {
        const data = JSON.parse(message.body)
        callback(data)
      } catch (error) {
        console.error('解析消息失败:', error)
      }
    })

    this.subscriptions.set(topic, subscription)
    console.log('已订阅主题:', topic)
  }

  /**
   * 取消订阅
   */
  unsubscribe(topic) {
    const subscription = this.subscriptions.get(topic)
    if (subscription) {
      subscription.unsubscribe()
      this.subscriptions.delete(topic)
      console.log('已取消订阅:', topic)
    }
  }

  /**
   * 断开连接
   */
  disconnect() {
    if (this.stompClient) {
      // 取消所有订阅
      this.subscriptions.forEach(subscription => {
        subscription.unsubscribe()
      })
      this.subscriptions.clear()
      
      // 断开连接
      this.stompClient.disconnect(() => {
        console.log('WebSocket已断开')
        this.connected = false
      })
    }
  }

  /**
   * 发送消息
   */
  send(destination, message) {
    if (!this.stompClient || !this.connected) {
      console.error('WebSocket未连接')
      return
    }

    this.stompClient.send(destination, {}, JSON.stringify(message))
  }
}

export default new WebSocketService()

