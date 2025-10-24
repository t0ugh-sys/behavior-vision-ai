import request from '@/utils/request'

/**
 * 创建检测区域
 */
export function createZone(data) {
  return request({
    url: '/zones',
    method: 'post',
    data
  })
}

/**
 * 更新检测区域
 */
export function updateZone(zoneId, data) {
  return request({
    url: `/zones/${zoneId}`,
    method: 'put',
    data
  })
}

/**
 * 删除检测区域
 */
export function deleteZone(zoneId) {
  return request({
    url: `/zones/${zoneId}`,
    method: 'delete'
  })
}

/**
 * 获取用户的所有区域
 */
export function getUserZones(userId) {
  return request({
    url: `/zones/user/${userId}`,
    method: 'get'
  })
}

/**
 * 获取用户的启用区域
 */
export function getActiveZones(userId) {
  return request({
    url: `/zones/user/${userId}/active`,
    method: 'get'
  })
}

/**
 * 获取指定区域
 */
export function getZone(zoneId) {
  return request({
    url: `/zones/${zoneId}`,
    method: 'get'
  })
}

/**
 * 切换区域状态
 */
export function toggleZoneStatus(zoneId) {
  return request({
    url: `/zones/${zoneId}/toggle`,
    method: 'put'
  })
}

