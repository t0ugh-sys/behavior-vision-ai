# 人体异常行为检测系统

基于YOLOv8-Pose的实时人体异常行为检测系统，可识别跌倒、打架、异常姿势等行为。

## 系统架构

```
├── backend/              # Spring Boot后端服务
├── frontend/             # Vue 3前端应用
├── python-service/       # Python检测服务（YOLOv8-Pose）
├── database/            # 数据库脚本
├── docs/                # 文档
└── uploads/             # 文件上传目录
```

## 技术栈

### 后端
- **Spring Boot 3.2** - Java后端框架
- **MySQL 8.0** - 关系型数据库
- **Spring Data JPA** - ORM框架
- **WebSocket** - 实时通信
- **Maven** - 项目管理

### 前端
- **Vue 3** - 前端框架
- **Element Plus** - UI组件库
- **Pinia** - 状态管理
- **Vue Router** - 路由管理
- **Axios** - HTTP客户端
- **ECharts** - 数据可视化

### Python服务
- **FastAPI** - Web框架
- **YOLOv8-Pose** - 人体姿态估计模型
- **OpenCV** - 图像处理
- **NumPy** - 数值计算

## 功能特性

### ✅ 核心功能
- **图片/视频检测** - 支持上传图片或视频文件进行检测
- **实时摄像头检测** - 调用本地摄像头进行实时检测
- **异常行为识别** - 跌倒、打架、异常姿势检测
- **实时告警推送** - WebSocket推送异常行为告警
- **检测记录管理** - 查看历史检测记录
- **数据统计分析** - 可视化图表展示统计数据

### 🎯 检测能力
- **跌倒检测** - 识别人体跌倒姿态
- **打架检测** - 检测多人打斗行为
- **异常姿势** - 识别其他异常人体姿势

### 🔔 告警功能
- **实时推送** - WebSocket实时推送告警
- **声音提醒** - 浏览器播放告警音效
- **已读/未读** - 告警消息状态管理
- **告警处理** - 记录告警处理情况

## 快速开始

### 环境要求

- **Java**: JDK 17+
- **Maven**: 3.6+
- **Node.js**: 16+
- **Python**: 3.8+
- **MySQL**: 8.0+

### 安装步骤

#### 1. 克隆项目
```bash
git clone <repository-url>
cd detection
```

#### 2. 配置数据库
```bash
# 登录MySQL
mysql -uroot -p

# 执行数据库脚本
source database/schema.sql
```

#### 3. 启动后端
```bash
cd backend
mvn clean package -DskipTests
java -jar target/behavior-detection-backend-1.0.0.jar
```

#### 4. 启动Python服务
```bash
cd python-service
pip install -r requirements.txt
python app.py
```

#### 5. 启动前端
```bash
cd frontend
npm install
npm run dev
```

### Windows一键启动（推荐）

#### 1. 配置环境（首次使用）
```bash
# 复制配置示例
copy config.bat.example config.bat

# 编辑config.bat，设置以下路径：
# - JAVA_HOME (如果不在PATH中)
# - MAVEN_HOME (如果不在PATH中)
# - CONDA_ENV (使用Conda环境)
```

#### 2. 启动系统
```bash
# 双击运行或命令行执行
start.bat
```

#### 3. 检查状态
```bash
# 查看所有服务运行状态
status.bat
```

#### 4. 停止系统
```bash
# 停止所有服务
stop.bat
```

#### 5. 清理临时文件
```bash
# 清理编译产物、缓存、日志等
clean.bat
```

## 配置说明

### 后端配置 (`backend/src/main/resources/application.yml`)
```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/behavior_detection
    username: root
    password: root

server:
  port: 8080

file:
  upload:
    path: C:/path/to/uploads

python:
  service:
    url: http://localhost:5000
```

### Python服务配置 (`python-service/config.py`)
```python
# 服务配置
APP_HOST = "0.0.0.0"
APP_PORT = 5000

# 模型配置
MODEL_PATH = "yolov8n-pose.pt"
MODEL_DEVICE = "cpu"  # 或 "cuda"
MODEL_CONFIDENCE_THRESHOLD = 0.5

# 检测阈值
FALL_THRESHOLD = 0.7
FIGHT_THRESHOLD = 0.6
```

### 前端配置 (`frontend/src/utils/request.js`)
```javascript
const baseURL = 'http://localhost:8080/api'
```

## 默认账号

- **用户名**: admin
- **密码**: admin123

## 文档

- **[API文档](docs/API.md)** - REST API接口说明
- **[项目结构](docs/PROJECT_STRUCTURE.md)** - 详细的目录结构和文件说明
- **[算法说明](docs/ALGORITHM.md)** - 检测算法原理
- **[快速开始](docs/QUICKSTART.md)** - 快速入门指南
- **[脚本指南](docs/SCRIPTS_GUIDE.md)** - 批处理脚本使用说明

## 项目结构概览

```
detection/
├── backend/              # Spring Boot 后端服务 (端口: 8080)
├── frontend/             # Vue 3 前端应用 (端口: 5173)
├── python-service/       # Python 检测服务 (端口: 5000)
├── database/             # 数据库脚本
├── docs/                 # 项目文档
├── uploads/              # 用户上传文件
├── start.bat             # 启动所有服务
├── stop.bat              # 停止所有服务
├── clean.bat             # 清理临时文件
├── status.bat            # 查看服务状态
└── README.md             # 项目说明
```

> 📘 查看 [详细项目结构说明](docs/PROJECT_STRUCTURE.md) 了解完整的目录结构和维护指南

## 开发指南

### 添加新的检测算法

1. 在 `python-service/detector.py` 中添加检测函数
2. 在 `detector.py` 的 `detect_behaviors()` 中调用新函数
3. 更新前端显示逻辑

### 扩展后端API

1. 在 `backend/src/main/java/com/detection/controller/` 创建控制器
2. 在 `service/` 实现业务逻辑
3. 在 `repository/` 定义数据访问接口
4. 更新 `entity/` 添加实体类

### 添加前端页面

1. 在 `frontend/src/views/` 创建Vue组件
2. 在 `router/index.js` 添加路由
3. 在 `api/` 创建API调用函数
4. 更新导航菜单

## 常见问题

### 1. 后端无法连接MySQL
- 检查MySQL服务是否启动
- 确认配置文件中的数据库连接信息
- 确保已执行数据库初始化脚本

### 2. Python服务启动失败
- 检查Python版本（需要3.8+）
- 确认已安装所有依赖：`pip install -r requirements.txt`
- 确保YOLOv8模型文件存在

### 3. 前端无法访问
- 检查端口是否被占用（默认5173）
- 确认后端服务是否启动
- 检查浏览器控制台错误信息

### 4. 文件上传失败
- 检查上传目录是否存在且有写权限
- 确认配置文件中的上传路径正确
- 检查文件大小限制（默认100MB）

## 性能优化

- **模型加速**: 使用GPU（CUDA）进行推理
- **视频处理**: 调整帧跳过参数减少计算量
- **数据库**: 添加适当的索引
- **前端**: 使用虚拟滚动处理大量数据

## 许可证

MIT License

## 联系方式

如有问题或建议，欢迎提Issue或PR。
