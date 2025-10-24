# JWT认证系统说明

## 系统概述

系统已完成JWT（JSON Web Token）认证和拦截器的集成，实现了完整的用户登录权限管理。

## 后端实现

### 1. JWT工具类 (`JwtUtil.java`)
- 生成JWT token
- 验证token有效性
- 从token中提取用户信息（用户名、角色、用户ID）
- Token有效期：24小时

### 2. 认证过滤器 (`JwtAuthenticationFilter.java`)
- 在每个请求前验证JWT token
- 从Authorization头中提取Bearer token
- 验证通过后设置Spring Security认证上下文
- 允许公开端点无需认证：
  - `/api/auth/**` - 认证相关接口
  - `/users/login` - 旧版登录接口（向后兼容）
  - `/users/register` - 旧版注册接口
  - `/api/health/**` - 健康检查
  - `/visualizations/**` - 可视化图片
  - `/snapshots/**` - 快照图片

### 3. Security配置 (`SecurityConfig.java`)
- 配置Spring Security
- 禁用CSRF（前后端分离项目）
- 设置无状态会话管理（使用JWT）
- 配置异常处理（401未授权、403权限不足）
- 密码加密器（BCrypt）

### 4. 认证控制器 (`AuthController.java`)
- `POST /api/auth/login` - 用户登录，返回JWT token
- `POST /api/auth/register` - 用户注册
- `GET /api/auth/validate` - 验证token是否有效

## 前端实现

### 1. API配置 (`request.js`)
- **请求拦截器**：自动在请求头添加 `Authorization: Bearer {token}`
- **响应拦截器**：
  - 处理401错误：清除token并跳转登录页
  - 处理403错误：提示权限不足

### 2. 用户Store (`user.js`)
- 保存用户信息和token到localStorage
- 提供token获取和清除方法

### 3. 路由守卫 (`router/index.js`)
- 检查token是否存在
- 未登录自动跳转登录页
- 已登录访问登录页自动跳转首页

### 4. 登录流程
1. 用户输入用户名和密码
2. 调用 `/api/auth/login` 获取token和用户信息
3. 保存token到localStorage
4. 后续所有请求自动携带token

## 使用流程

### 用户登录
```
1. 访问 http://localhost:5173
2. 自动跳转到登录页（因为没有token）
3. 输入用户名密码登录
4. 成功后跳转到系统首页
```

### Token验证
```
每次API请求：
Request Headers:
  Authorization: Bearer eyJhbGciOiJIUzI1NiJ9...
```

### 退出登录
```
清除localStorage中的token和user信息
跳转到登录页
```

## 默认用户

系统已在数据库中创建默认用户：

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin  | admin | ADMIN |
| user   | user  | USER |

## 安全特性

1. ✅ JWT token有效期24小时
2. ✅ 密码使用BCrypt加密存储
3. ✅ 未授权请求自动拒绝（401）
4. ✅ Token过期自动跳转登录
5. ✅ CSRF保护已禁用（使用JWT）
6. ✅ 无状态会话管理

## 注意事项

1. **首次启动**：确保MySQL数据库已运行，数据库schema已创建
2. **Token存储**：token保存在localStorage，刷新页面不会丢失
3. **安全性**：生产环境应将JWT密钥移到配置文件，不要硬编码
4. **有效期**：token有效期为24小时，过期需重新登录

## 扩展功能

可以添加的功能：
- Token刷新机制（Refresh Token）
- 记住我功能（延长有效期）
- 多设备登录管理
- 登录日志记录

