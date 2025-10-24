# 快速开始指南

本指南将帮助您在5分钟内启动整个系统。

## 前置条件

确保已安装以下软件：

- ✅ Java 17+
- ✅ Maven 3.6+
- ✅ Node.js 16+
- ✅ Python 3.8+
- ✅ MySQL 8.0+

## Windows快速启动（推荐）

### 1. 配置环境

编辑 `config.bat` 文件，设置以下路径：

```batch
:: Java路径（根据实际安装位置修改）
set "JAVA_HOME=C:\Program Files\Java\jdk-17"

:: Maven路径
set "MAVEN_HOME=D:\apache-maven-3.9.11"

:: Python环境（如果使用conda）
set "CONDA_ENV=detection"
```

### 2. 初始化数据库

```bash
# 登录MySQL
mysql -uroot -p

# 执行数据库脚本
source database/schema.sql

# 或者在MySQL命令行中
USE behavior_detection;
SOURCE C:/path/to/detection/database/schema.sql;
```

### 3. 一键启动

双击运行 `start.bat`，脚本将自动：
- 启动后端服务（端口8080）
- 启动Python检测服务（端口5000）
- 启动前端开发服务器（端口5173）

### 4. 访问系统

打开浏览器访问：`http://localhost:5173`

默认账号：
- 用户名：`admin`
- 密码：`admin123`

### 5. 停止服务

双击运行 `stop.bat`

## 手动启动

### 步骤1：启动后端

```bash
cd backend

# 编译项目
mvn clean package -DskipTests

# 启动服务
java -jar target/behavior-detection-backend-1.0.0.jar
```

### 步骤2：启动Python服务

```bash
cd python-service

# 安装依赖（首次运行）
pip install -r requirements.txt

# 启动服务
python app.py
```

### 步骤3：启动前端

```bash
cd frontend

# 安装依赖（首次运行）
npm install

# 启动开发服务器
npm run dev
```

## 验证安装

### 1. 检查后端状态

访问：`http://localhost:8080/api/health`

应该返回：
```json
{
  "code": 200,
  "message": "系统运行正常",
  "data": {
    "backend": "healthy",
    "database": "healthy",
    "pythonService": "healthy"
  }
}
```

### 2. 检查Python服务

访问：`http://localhost:5000/health`

应该返回：
```json
{
  "status": "healthy",
  "model_loaded": true
}
```

### 3. 检查前端

访问：`http://localhost:5173`

应该显示登录页面

## 快速体验

### 1. 登录系统

- 用户名：`admin`
- 密码：`admin123`

### 2. 上传测试视频

1. 进入"实时检测"页面
2. 选择"文件检测"标签
3. 上传测试视频或图片
4. 点击"开始检测"

### 3. 查看检测结果

- **检测记录**：查看所有历史检测
- **告警管理**：查看异常行为告警
- **数据统计**：查看可视化统计图表

## 常见问题

### Q1: 后端启动失败，提示无法连接数据库

**解决方案：**
1. 确认MySQL服务已启动
2. 检查 `application.yml` 中的数据库配置
3. 确认已执行数据库初始化脚本

### Q2: Python服务启动失败

**解决方案：**
```bash
# 重新安装依赖
pip install --upgrade pip
pip install -r requirements.txt

# 如果使用conda
conda create -n detection python=3.9
conda activate detection
pip install -r requirements.txt
```

### Q3: 前端显示空白页面

**解决方案：**
1. 打开浏览器控制台查看错误
2. 确认后端服务已启动
3. 重新安装依赖：
```bash
cd frontend
rm -rf node_modules
npm install
npm run dev
```

### Q4: 文件上传失败

**解决方案：**
1. 检查上传目录是否存在：
```bash
mkdir -p uploads
```
2. 确认 `application.yml` 中的上传路径配置正确
3. 检查文件大小是否超过100MB限制

### Q5: YOLOv8模型文件丢失

**解决方案：**
```bash
cd python-service

# 下载模型文件
python -c "from ultralytics import YOLO; YOLO('yolov8n-pose.pt')"
```

## 端口占用处理

如果默认端口被占用，可以修改配置：

### 修改后端端口（默认8080）
编辑 `backend/src/main/resources/application.yml`：
```yaml
server:
  port: 8081  # 修改为其他端口
```

### 修改Python服务端口（默认5000）
编辑 `python-service/config.py`：
```python
APP_PORT = 5001  # 修改为其他端口
```

### 修改前端端口（默认5173）
编辑 `frontend/vite.config.js`：
```javascript
export default defineConfig({
  server: {
    port: 5174  // 修改为其他端口
  }
})
```

## 下一步

- 📖 阅读 [开发指南](DEVELOPMENT_GUIDE.md)
- 📖 查看 [API文档](API.md)
- 📖 了解 [算法原理](ALGORITHM.md)
- 📖 学习 [部署方案](DEPLOYMENT.md)

## 技术支持

如遇到问题，请检查：
1. 所有服务是否正常启动
2. 端口是否被占用
3. 配置文件是否正确
4. 查看服务日志获取详细错误信息

祝使用愉快！🎉
