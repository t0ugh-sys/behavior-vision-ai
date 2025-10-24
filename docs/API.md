# API 接口文档

## 基础信息

- **Base URL**: `http://localhost:8080/api`
- **数据格式**: JSON
- **字符编码**: UTF-8

## 通用响应格式

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

## 1. 用户接口

### 1.1 用户登录
- **URL**: `/users/login`
- **Method**: `POST`
- **请求体**:
```json
{
  "username": "admin",
  "password": "admin123"
}
```
- **响应**:
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "id": 1,
    "username": "admin",
    "realName": "系统管理员",
    "role": "ADMIN"
  }
}
```

### 1.2 用户注册
- **URL**: `/users/register`
- **Method**: `POST`
- **请求体**:
```json
{
  "username": "testuser",
  "password": "123456",
  "email": "test@example.com",
  "realName": "测试用户"
}
```

### 1.3 获取用户信息
- **URL**: `/users/{userId}`
- **Method**: `GET`

## 2. 检测接口

### 2.1 上传文件并检测
- **URL**: `/detections/upload`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`
- **请求参数**:
  - `file`: 文件（图片或视频）
  - `userId`: 用户ID
  - `sourceType`: 来源类型（IMAGE/VIDEO）

### 2.2 获取检测记录列表
- **URL**: `/detections/user/{userId}`
- **Method**: `GET`
- **Query参数**:
  - `page`: 页码（从0开始）
  - `size`: 每页数量

- **响应**:
```json
{
  "code": 200,
  "data": {
    "content": [
      {
        "id": 1,
        "userId": 1,
        "sourceType": "VIDEO",
        "hasAbnormal": true,
        "behaviorType": "fall",
        "confidence": 0.95,
        "status": "COMPLETED",
        "createdAt": "2025-10-22T10:00:00"
      }
    ],
    "totalElements": 100,
    "totalPages": 10,
    "number": 0,
    "size": 10
  }
}
```

### 2.3 获取检测记录详情
- **URL**: `/detections/{recordId}`
- **Method**: `GET`

### 2.4 获取行为数据
- **URL**: `/detections/{recordId}/behaviors`
- **Method**: `GET`

### 2.5 获取用户统计数据
- **URL**: `/detections/statistics/{userId}`
- **Method**: `GET`
- **响应**:
```json
{
  "code": 200,
  "data": {
    "total_records": 150,
    "abnormal_records": 45,
    "normal_records": 105,
    "behavior_type_stats": {
      "fall": 20,
      "fight": 15,
      "abnormal_pose": 10
    },
    "recent_trend": [
      {"date": "2025-10-16", "count": 10},
      {"date": "2025-10-17", "count": 15}
    ]
  }
}
```

### 2.6 获取全局统计
- **URL**: `/detections/statistics/global`
- **Method**: `GET`

### 2.7 删除检测记录
- **URL**: `/detections/{recordId}`
- **Method**: `DELETE`

## 3. 告警接口

### 3.1 接收告警通知（Python服务调用）
- **URL**: `/alerts/notify`
- **Method**: `POST`
- **请求体**:
```json
{
  "user_id": 1,
  "record_id": 123,
  "alert_type": "fall",
  "alert_level": "HIGH",
  "confidence": 0.95,
  "description": "检测到跌倒行为",
  "snapshot_path": "/path/to/snapshot.jpg"
}
```

### 3.2 获取用户告警列表
- **URL**: `/alerts/user/{userId}`
- **Method**: `GET`
- **Query参数**:
  - `page`: 页码
  - `size`: 每页数量

### 3.3 获取未处理告警
- **URL**: `/alerts/user/{userId}/unhandled`
- **Method**: `GET`

### 3.4 处理告警
- **URL**: `/alerts/{alertId}/handle`
- **Method**: `PUT`
- **请求体**:
```json
{
  "handled_by": "admin",
  "handle_note": "已确认并处理"
}
```

### 3.5 标记告警为已读
- **URL**: `/alerts/{alertId}/read`
- **Method**: `PUT`

### 3.6 批量标记已读
- **URL**: `/alerts/user/{userId}/read-all`
- **Method**: `PUT`

### 3.7 获取未读数量
- **URL**: `/alerts/user/{userId}/unread-count`
- **Method**: `GET`

### 3.8 获取告警统计
- **URL**: `/alerts/statistics/{userId}`
- **Method**: `GET`

### 3.9 获取时间范围内的告警
- **URL**: `/alerts/user/{userId}/range`
- **Method**: `GET`
- **Query参数**:
  - `start`: 开始时间（ISO 8601格式）
  - `end`: 结束时间

## 4. 健康检查

### 4.1 系统健康状态
- **URL**: `/health`
- **Method**: `GET`
- **响应**:
```json
{
  "code": 200,
  "message": "系统运行正常",
  "data": {
    "backend": "healthy",
    "database": "healthy",
    "pythonService": "healthy",
    "timestamp": 1729580400000
  }
}
```

## 5. WebSocket接口

### 5.1 连接WebSocket
- **URL**: `ws://localhost:8080/api/ws`
- **Protocol**: WebSocket

### 5.2 订阅告警通道
- **Topic**: `/topic/alerts/{userId}` - 用户告警
- **Topic**: `/topic/alerts/all` - 全局告警（管理员）

### 5.3 告警消息格式
```json
{
  "id": 1,
  "userId": 1,
  "alertType": "fall",
  "alertLevel": "HIGH",
  "confidence": 0.95,
  "description": "检测到跌倒行为",
  "snapshotPath": "/path/to/snapshot.jpg",
  "createdAt": "2025-10-22T10:00:00"
}
```

## 6. Python服务接口

### 6.1 健康检查
- **URL**: `http://localhost:5000/health`
- **Method**: `GET`

### 6.2 检测图片/视频
- **URL**: `http://localhost:5000/detect`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`
- **请求参数**:
  - `file`: 文件
  - `source_type`: IMAGE/VIDEO

### 6.3 实时流检测
- **URL**: `http://localhost:5000/stream`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **请求体**:
```json
{
  "user_id": 1,
  "stream_url": "rtsp://camera-ip/stream"
}
```

## 错误码说明

| 错误码 | 说明 |
|-------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 注意事项

1. 所有时间格式使用ISO 8601标准
2. 文件上传限制为100MB
3. WebSocket需要先建立连接后才能接收消息
4. 分页参数page从0开始计数
5. 置信度confidence范围为0-1

