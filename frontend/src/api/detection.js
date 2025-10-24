import request from '@/utils/request'

/**
 * 上传文件并检测
 */
export function uploadAndDetect(formData) {
  return request({
    url: '/detections/upload',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 获取检测记录列表
 */
export function getDetectionRecords(userId, page = 0, size = 10) {
  return request({
    url: `/detections/user/${userId}`,
    method: 'get',
    params: { page, size }
  })
}

/**
 * 获取检测记录详情
 */
export function getDetectionRecord(recordId) {
  return request({
    url: `/detections/${recordId}`,
    method: 'get'
  })
}

/**
 * 获取检测记录的行为数据
 */
export function getBehaviorData(recordId) {
  return request({
    url: `/detections/${recordId}/behaviors`,
    method: 'get'
  })
}

/**
 * 获取用户统计数据
 */
export function getUserStatistics(userId) {
  return request({
    url: `/detections/statistics/${userId}`,
    method: 'get'
  })
}

/**
 * 删除检测记录
 */
export function deleteDetectionRecord(recordId) {
  return request({
    url: `/detections/${recordId}`,
    method: 'delete'
  })
}

/**
 * 批量删除检测记录
 */
export function batchDeleteRecords(recordIds) {
  return request({
    url: '/detections/batch',
    method: 'delete',
    data: recordIds
  })
}

