<div align="center">

# 🤖 Behavior Vision AI

**智能守护者 - 基于YOLOv8的人体异常行为检测系统**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Java 17+](https://img.shields.io/badge/java-17+-orange.svg)](https://www.oracle.com/java/technologies/downloads/)
[![Vue 3](https://img.shields.io/badge/vue-3.x-green.svg)](https://vuejs.org/)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Pose-red.svg)](https://github.com/ultralytics/ultralytics)

[功能特性](#-功能特性) • [快速开始](#-快速开始) • [技术栈](#-技术栈) • [文档](#-文档) • [贡献](#-贡献)

</div>

---

## 📖 项目简介

**Behavior Vision AI** 是一个基于深度学习的智能监控系统，利用YOLOv8-Pose人体姿态估计技术，实现对人体异常行为的实时检测与告警。系统采用前后端分离架构，支持图片、视频文件检测以及实时摄像头监控，可广泛应用于公共安全、养老看护、智能家居等场景。

### ✨ 亮点

- 🎯 **高精度检测** - 基于YOLOv8-Pose模型，准确识别跌倒、打架等异常行为
- ⚡ **实时处理** - 支持视频流实时分析，毫秒级响应
- 🎨 **现代化UI** - 采用Element Plus组件库，优雅的Cornflower Blue主题
- 🔔 **智能告警** - WebSocket实时推送，支持声音提醒
- 📊 **数据可视化** - ECharts图表展示统计分析结果
- 🚀 **一键部署** - 提供批处理脚本，Windows环境一键启动

## 系统架构

```
├── backend/              # Spring Boot后端服务
├── frontend/             # Vue 3前端应用
├── python-service/       # Python检测服务（YOLOv8-Pose）
├── database/            # 数据库脚本
├── docs/                # 文档
└── uploads/             # 文件上传目录
```

## 🛠️ 技术栈

<table>
<tr>
<td width="33%" valign="top">

### 🔧 后端服务
- **Spring Boot 3.2** - 企业级Java框架
- **MySQL 8.0** - 关系型数据库
- **Spring Data JPA** - ORM持久化
- **Spring Security + JWT** - 安全认证
- **WebSocket** - 实时双向通信
- **Maven** - 依赖管理

</td>
<td width="33%" valign="top">

### 🎨 前端应用
- **Vue 3** - 渐进式框架
- **Element Plus** - UI组件库
- **Pinia** - 状态管理
- **Vue Router** - 路由管理
- **Axios** - HTTP客户端
- **ECharts** - 数据可视化
- **Vite** - 构建工具

</td>
<td width="33%" valign="top">

### 🧠 AI检测服务
- **FastAPI** - 异步Web框架
- **YOLOv8-Pose** - 姿态估计
- **OpenCV** - 图像处理
- **NumPy** - 科学计算
- **Ultralytics** - 模型推理

</td>
</tr>
</table>

## 🎯 功能特性

### 核心功能模块

| 模块 | 功能描述 | 技术实现 |
|------|---------|---------|
| 🎬 **多源检测** | 支持图片、视频文件、实时摄像头、RTSP流检测 | YOLOv8-Pose + OpenCV |
| 🤖 **异常识别** | 跌倒、打架、异常姿势等多种行为检测 | 关键点分析 + 时序建模 |
| 🔔 **智能告警** | 实时推送、声音提醒、多级告警策略 | WebSocket + 浏览器API |
| 📊 **数据分析** | 行为统计、趋势分析、可视化图表 | ECharts + 数据聚合 |
| 🎨 **可视化** | 骨架标注、行为轨迹、热力图展示 | Canvas + SVG渲染 |
| 👥 **用户管理** | 角色权限、操作日志、个性化配置 | Spring Security + JWT |
| 📁 **记录管理** | 历史查询、导出报告、批量操作 | JPA + 文件服务 |
| ⚙️ **系统配置** | 阈值调整、区域设置、模型参数 | 动态配置热更新 |

### 检测能力详情

<details>
<summary><b>🔻 跌倒检测</b> - 点击展开</summary>

- ✅ 识别人体重心失衡
- ✅ 检测倒地姿态（侧倒、后仰、前扑）
- ✅ 支持单人/多人场景
- ✅ 实时输出置信度评分
</details>

<details>
<summary><b>🥊 打架检测</b> - 点击展开</summary>

- ✅ 多人肢体冲突识别
- ✅ 暴力动作模式匹配
- ✅ 时序行为分析
- ✅ 区域入侵检测
</details>

<details>
<summary><b>🚨 异常姿势</b> - 点击展开</summary>

- ✅ 长时间静止异常
- ✅ 非常规身体姿态
- ✅ 危险区域徘徊
- ✅ 自定义规则引擎
</details>

### 告警系统特性

- 🔔 **实时推送** - WebSocket双向通信，0延迟告警
- 🎵 **多模态提醒** - 声音、桌面通知、邮件（可扩展）
- 📝 **告警记录** - 自动保存快照、视频片段、行为标注
- 📊 **统计分析** - 告警频次、时段分布、趋势预测
- ✅ **处理流程** - 已读/未读、处理状态、备注记录

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
