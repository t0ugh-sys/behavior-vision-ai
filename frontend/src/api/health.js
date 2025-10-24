import request from '@/utils/request'

/**
 * 获取所有服务状态
 */
export function getAllServicesStatus() {
  return request({
    url: '/health/status',
    method: 'get'
  })
}

/**
 * 获取后端健康状态
 */
export function getBackendHealth() {
  return request({
    url: '/health',
    method: 'get'
  })
}

/**
 * 获取Python服务健康状态
 */
export function getPythonHealth() {
  return request({
    url: '/health/python',
    method: 'get'
  })
}

/**
 * 获取系统信息
 */
export function getSystemInfo() {
  return request({
    url: '/health/info',
    method: 'get'
  })
}

