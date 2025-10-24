import request from '@/utils/request'

/**
 * 获取告警列表
 */
export function getAlerts(userId, page = 0, size = 10) {
  return request({
    url: `/alerts/user/${userId}`,
    method: 'get',
    params: { page, size }
  })
}

/**
 * 获取未处理的告警
 */
export function getUnhandledAlerts(userId) {
  return request({
    url: `/alerts/user/${userId}/unhandled`,
    method: 'get'
  })
}

/**
 * 处理告警
 */
export function handleAlert(alertId, data) {
  return request({
    url: `/alerts/${alertId}/handle`,
    method: 'put',
    data
  })
}

/**
 * 获取告警统计
 */
export function getAlertStatistics(userId) {
  return request({
    url: `/alerts/statistics/${userId}`,
    method: 'get'
  })
}

/**
 * 获取时间范围内的告警
 */
export function getAlertsByTimeRange(userId, start, end) {
  return request({
    url: `/alerts/user/${userId}/range`,
    method: 'get',
    params: { start, end }
  })
}

/**
 * 删除告警
 */
export function deleteAlert(alertId) {
  return request({
    url: `/alerts/${alertId}`,
    method: 'delete'
  })
}

/**
 * 批量删除告警
 */
export function batchDeleteAlerts(alertIds) {
  return request({
    url: '/alerts/batch',
    method: 'delete',
    data: alertIds
  })
}

