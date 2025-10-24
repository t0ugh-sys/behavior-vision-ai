import request from '@/utils/request'

/**
 * 用户登录（使用JWT认证）
 */
export function login(data) {
  return request({
    url: '/auth/login',
    method: 'post',
    data
  })
}

/**
 * 用户注册
 */
export function register(data) {
  return request({
    url: '/auth/register',
    method: 'post',
    data
  })
}

/**
 * 验证token
 */
export function validateToken() {
  return request({
    url: '/auth/validate',
    method: 'get'
  })
}

/**
 * 获取用户信息
 */
export function getUserInfo(id) {
  return request({
    url: `/users/${id}`,
    method: 'get'
  })
}

/**
 * 更新用户信息
 */
export function updateUser(id, data) {
  return request({
    url: `/users/${id}`,
    method: 'put',
    data
  })
}

