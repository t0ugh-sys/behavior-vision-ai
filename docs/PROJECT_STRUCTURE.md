# 项目结构说明

## 📁 项目目录结构

```
detection/
├── backend/                    # Spring Boot 后端服务
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/com/detection/
│   │   │   │   ├── config/           # 配置类（Security, JWT, WebSocket, CORS）
│   │   │   │   ├── controller/       # REST API 控制器
│   │   │   │   ├── dto/              # 数据传输对象
│   │   │   │   ├── entity/           # JPA 实体类
│   │   │   │   ├── exception/        # 全局异常处理
│   │   │   │   ├── repository/       # 数据访问层
│   │   │   │   ├── service/          # 业务逻辑层
│   │   │   │   └── util/             # 工具类（JWT）
│   │   │   └── resources/
│   │   │       ├── application.yml   # Spring Boot 配置
│   │   │       └── logback-spring.xml # 日志配置
│   ├── logs/                   # 应用日志（自动生成）
│   ├── uploads/                # 用户上传文件存储
│   ├── target/                 # Maven 编译输出（自动生成）
│   └── pom.xml                 # Maven 依赖配置
│
├── frontend/                   # Vue 3 前端应用
│   ├── src/
│   │   ├── api/                # API 客户端
│   │   │   ├── alert.js              # 告警相关 API
│   │   │   ├── detection.js          # 检测相关 API
│   │   │   ├── health.js             # 健康检查 API
│   │   │   ├── user.js               # 用户相关 API
│   │   │   └── zone.js               # 区域配置 API
│   │   ├── components/         # 可复用组件
│   │   │   ├── CountUp.vue           # 数字动画组件
│   │   │   ├── EmptyState.vue        # 空状态组件
│   │   │   ├── LoadingSpinner.vue    # 加载动画组件
│   │   │   └── StatCard.vue          # 统计卡片组件
│   │   ├── router/             # 路由配置
│   │   │   └── index.js
│   │   ├── stores/             # Pinia 状态管理
│   │   │   ├── alert.js              # 告警状态
│   │   │   └── user.js               # 用户状态
│   │   ├── styles/             # 全局样式
│   │   │   ├── global.css            # 全局样式
│   │   │   └── variables.css         # CSS 变量
│   │   ├── utils/              # 工具函数
│   │   │   ├── export.js             # 导出功能（Excel/CSV/JSON）
│   │   │   ├── request.js            # Axios 拦截器
│   │   │   └── websocket.js          # WebSocket 客户端
│   │   ├── views/              # 页面组件
│   │   │   ├── Alerts.vue            # 告警管理页面
│   │   │   ├── Dashboard.vue         # 仪表板页面
│   │   │   ├── Detection.vue         # 实时检测页面
│   │   │   ├── Layout.vue            # 主布局
│   │   │   ├── Login.vue             # 登录页面
│   │   │   ├── Records.vue           # 检测记录页面
│   │   │   ├── Settings.vue          # 系统设置页面
│   │   │   └── Statistics.vue        # 统计分析页面
│   │   ├── App.vue             # 根组件
│   │   └── main.js             # 应用入口
│   ├── public/
│   │   └── alert.mp3           # 告警音效
│   ├── index.html              # HTML 入口
│   ├── package.json            # npm 依赖配置
│   ├── package-lock.json       # npm 依赖锁定
│   ├── vite.config.js          # Vite 构建配置
│   └── node_modules/           # npm 依赖（自动生成）
│
├── python-service/             # Python 检测服务
│   ├── app.py                  # FastAPI 应用主文件
│   ├── detector.py             # YOLOv8 检测核心逻辑
│   ├── alert_notifier.py       # 告警通知模块
│   ├── config.py               # Python 服务配置
│   ├── rtsp_handler.py         # RTSP 流处理
│   ├── realtime_stream.py      # 实时流处理
│   ├── temporal.py             # 时序分析模块
│   ├── zone_detector.py        # 区域入侵检测
│   ├── yolov8n-pose.pt         # YOLOv8 姿态估计模型
│   ├── requirements.txt        # Python 依赖
│   ├── uploads/                # 上传文件临时存储
│   ├── visualizations/         # 检测结果可视化文件
│   ├── snapshots/              # 告警快照
│   ├── temp/                   # 临时文件（自动清理）
│   └── __pycache__/            # Python 缓存（自动生成）
│
├── database/                   # 数据库脚本
│   └── schema.sql              # 数据库表结构
│
├── docs/                       # 项目文档
│   ├── ALGORITHM.md            # 算法说明
│   ├── API.md                  # API 文档
│   ├── JWT认证说明.md          # JWT 认证说明
│   ├── PROJECT_STRUCTURE.md    # 项目结构说明（本文件）
│   ├── QUICKSTART.md           # 快速开始指南
│   ├── SCRIPTS_GUIDE.md        # 脚本使用指南
│   └── 安装MySQL到D盘.md       # MySQL 安装指南
│
├── uploads/                    # 用户上传文件（根目录）
├── logs/                       # 系统日志
│
├── start.bat                   # 启动所有服务
├── stop.bat                    # 停止所有服务
├── status.bat                  # 查看服务状态
├── diagnose.bat                # 诊断工具
├── config.bat                  # 配置文件（不提交到Git）
│
├── .gitignore                  # Git 忽略规则
├── README.md                   # 项目说明
└── PROJECT_STATUS.md           # 项目状态
```

## 📝 目录说明

### 后端服务 (backend/)

**技术栈**: Spring Boot 3.x + Spring Security + JWT + WebSocket + JPA + MySQL

**主要功能**:
- 用户认证与授权
- 检测记录管理
- 告警管理
- 统计分析
- WebSocket 实时推送
- 区域配置管理

**端口**: 8080  
**API前缀**: `/api`

### 前端应用 (frontend/)

**技术栈**: Vue 3 + Vite + Element Plus + Pinia + ECharts

**主要页面**:
- 仪表板：系统概览、服务状态
- 实时检测：文件检测、摄像头检测、RTSP流检测
- 检测记录：历史记录查看、导出、打印
- 告警管理：告警查看、处理、删除
- 统计分析：数据可视化、趋势分析
- 系统设置：用户信息、检测配置

**端口**: 5173 (开发环境)

### Python检测服务 (python-service/)

**技术栈**: FastAPI + Ultralytics YOLOv8 + OpenCV + NumPy

**主要功能**:
- 人体姿态估计
- 跌倒检测
- 异常姿态检测
- 打架检测
- 区域入侵检测
- 视频/图片检测
- RTSP实时流检测
- 结果可视化

**端口**: 5000

## 🗂️ 文件类型说明

### 自动生成（不应提交到Git）

- `backend/target/` - Maven编译输出
- `backend/logs/` - 应用日志
- `frontend/node_modules/` - npm依赖
- `frontend/dist/` - 前端构建输出
- `python-service/__pycache__/` - Python缓存
- `python-service/temp/` - 临时文件
- `*.log` - 日志文件
- `*.class` - Java字节码

### 运行时生成（需要保留目录）

- `uploads/` - 用户上传的文件
- `python-service/uploads/` - Python服务临时存储
- `python-service/visualizations/` - 检测结果可视化
- `python-service/snapshots/` - 告警快照

### 配置文件

- `config.bat` - 本地配置（包含敏感信息，不提交）
- `application.yml` - Spring Boot配置
- `vite.config.js` - Vite配置
- `requirements.txt` - Python依赖

### 脚本文件

- `start.bat` - 启动脚本（编译后端 + 启动所有服务）
- `stop.bat` - 停止脚本（停止所有服务）
- `status.bat` - 状态检查
- `diagnose.bat` - 诊断工具

## 🔧 维护建议

### 定期清理

1. **临时文件**:
   ```bash
   python-service/temp/*.mp4
   python-service/temp/*.jpg
   ```

2. **旧日志文件**:
   ```bash
   backend/logs/*.log
   ```

3. **编译产物**:
   ```bash
   backend/target/
   frontend/dist/
   ```

### 备份重要数据

- 数据库定期备份
- `uploads/` 目录（用户上传的文件）
- `python-service/visualizations/` 目录（检测结果）
- `python-service/snapshots/` 目录（告警快照）

### 更新依赖

1. **后端依赖**:
   ```bash
   cd backend
   mvn versions:display-dependency-updates
   ```

2. **前端依赖**:
   ```bash
   cd frontend
   npm outdated
   npm update
   ```

3. **Python依赖**:
   ```bash
   cd python-service
   pip list --outdated
   pip install --upgrade -r requirements.txt
   ```

## 📊 存储空间管理

### 占用空间最大的目录

1. `frontend/node_modules/` - 约 200-500 MB
2. `python-service/visualizations/` - 根据使用量增长
3. `uploads/` - 根据用户上传量增长
4. `backend/target/` - 约 50-100 MB
5. `python-service/yolov8n-pose.pt` - 约 6 MB

### 清理建议

- 开发环境可以定期删除 `node_modules/` 和 `target/`
- 生产环境应该定期归档或删除旧的检测结果和上传文件
- 使用日志轮转策略管理日志文件

## 🚀 快速命令

```bash
# 启动所有服务
.\start.bat

# 停止所有服务
.\stop.bat

# 查看服务状态
.\status.bat

# 诊断问题
.\diagnose.bat

# 只清理临时文件（不停止服务）
Remove-Item -Path "python-service\temp\*" -Force
Remove-Item -Path "python-service\__pycache__" -Recurse -Force
Remove-Item -Path "backend\target" -Recurse -Force
```

## 📌 注意事项

1. **不要手动修改**:
   - `target/` 目录
   - `node_modules/` 目录
   - `__pycache__/` 目录
   - `.class` 文件

2. **谨慎操作**:
   - `uploads/` 目录（用户数据）
   - `database/` 目录（数据库脚本）
   - 配置文件修改

3. **必须保留**:
   - `yolov8n-pose.pt` 模型文件
   - `schema.sql` 数据库表结构
   - `.gitkeep` 文件（保持目录结构）

## 🔗 相关文档

- [快速开始指南](./QUICKSTART.md)
- [API文档](./API.md)
- [算法说明](./ALGORITHM.md)
- [脚本使用指南](./SCRIPTS_GUIDE.md)

