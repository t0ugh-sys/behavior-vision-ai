# Windows脚本使用指南

本项目提供了一套完整的Windows批处理脚本，用于简化系统的启动、停止和管理。

## 📁 脚本文件

### 1. `start.bat` - 启动脚本
启动所有服务（后端、Python、前端）

**特性：**
- ✅ 自动环境检查（Java、Maven、Python、Node.js）
- ✅ 支持Conda环境自动激活
- ✅ 智能编译（如果jar包不存在）
- ✅ 独立窗口运行各服务（便于调试）
- ✅ 自动打开浏览器
- ✅ 详细的启动日志

**使用方法：**
```bash
# 方式1：双击运行
start.bat

# 方式2：命令行运行
cmd /c start.bat
```

### 2. `stop.bat` - 停止脚本
停止所有正在运行的服务

**特性：**
- ✅ 确认提示（防止误操作）
- ✅ 精确的端口检测
- ✅ 自动清理残留进程
- ✅ 可选日志清理
- ✅ 详细的停止状态

**使用方法：**
```bash
# 方式1：双击运行
stop.bat

# 方式2：命令行运行
cmd /c stop.bat
```

**交互提示：**
1. 确认是否停止服务 (Y/N)
2. 确认是否清理日志 (Y/N)

### 3. `status.bat` - 状态检查脚本
检查所有服务的运行状态

**特性：**
- ✅ 实时端口监听检测
- ✅ MySQL状态检查
- ✅ 服务状态总结
- ✅ 快捷操作菜单

**使用方法：**
```bash
# 双击运行
status.bat
```

**显示信息：**
- 后端服务状态 (端口8080)
- Python服务状态 (端口5000)
- 前端服务状态 (端口5173)
- MySQL数据库状态 (端口3306)

**快捷操作：**
- [1] 启动所有服务
- [2] 停止所有服务
- [3] 刷新状态
- [4] 退出

### 4. `clean.bat` - 清理脚本
清理项目临时文件和编译产物

**特性：**
- ✅ 清理Python临时文件
- ✅ 清理Python缓存(__pycache__)
- ✅ 清理Maven编译输出(target/)
- ✅ 清理后端日志文件
- ✅ 清理前端构建输出(dist/)
- ✅ 清理根目录日志
- ✅ 安全提示和统计

**使用方法：**
```bash
# 双击运行
clean.bat
```

**清理内容：**
- `python-service/temp/*` - Python临时文件
- `python-service/__pycache__/` - Python缓存
- `backend/target/` - Maven编译输出
- `backend/logs/*.log` - 后端日志
- `frontend/dist/` - 前端构建输出
- `logs/*.log` - 根目录日志

**注意：**
- 不会删除 `node_modules/`（需要手动清理）
- 不会删除用户上传的文件（`uploads/`）
- 不会删除检测结果（`visualizations/`）

### 5. `config.bat.example` - 配置示例
环境配置模板文件

**使用方法：**
```bash
# 1. 复制为config.bat
copy config.bat.example config.bat

# 2. 编辑config.bat，配置环境路径
notepad config.bat
```

**配置项说明：**
```batch
# Java路径（如果不在PATH中）
set "JAVA_HOME=C:\Program Files\Java\jdk-17"

# Maven路径（如果不在PATH中）
set "MAVEN_HOME=D:\apache-maven-3.9.11"

# Conda环境名称（推荐）
set "CONDA_ENV=detection"

# 或Python路径（不使用Conda时）
set "PYTHON_PATH=C:\Python39"

# Node.js路径（如果不在PATH中）
set "NODE_PATH=C:\Program Files\nodejs"
```

## 🚀 完整使用流程

### 首次启动

1. **配置环境**
```bash
# 复制配置文件
copy config.bat.example config.bat

# 编辑配置文件，设置环境路径
notepad config.bat
```

2. **初始化数据库**
```bash
# 登录MySQL
mysql -uroot -p

# 执行数据库脚本
source database/schema.sql
```

3. **启动系统**
```bash
# 双击运行start.bat
start.bat
```

4. **检查状态**
```bash
# 双击运行status.bat
status.bat
```

5. **访问系统**
- 前端：http://localhost:5173
- 后端：http://localhost:8080/api
- Python：http://localhost:5000

### 日常使用

**启动系统：**
```bash
start.bat
```

**检查状态：**
```bash
status.bat
```

**停止系统：**
```bash
stop.bat
```

## 🔧 环境配置说明

### 选项1：使用Conda（推荐）

**优点：**
- 环境隔离
- 依赖管理方便
- 多项目友好

**配置：**
```batch
# 在config.bat中设置
set "CONDA_ENV=detection"
```

**Conda环境创建：**
```bash
# 创建环境
conda create -n detection python=3.9

# 激活环境
conda activate detection

# 安装依赖
cd python-service
pip install -r requirements.txt
```

### 选项2：使用全局Python

**配置：**
```batch
# 在config.bat中设置
set "PYTHON_PATH=C:\Python39"
```

**安装依赖：**
```bash
cd python-service
pip install -r requirements.txt
```

## 📝 服务窗口说明

`start.bat` 会为每个服务打开独立的命令行窗口：

### 后端窗口
- **标题**：后端服务 - Spring Boot (端口:8080)
- **内容**：Spring Boot启动日志
- **关闭**：停止后端服务

### Python窗口
- **标题**：Python检测服务 (端口:5000)
- **内容**：FastAPI启动日志和检测日志
- **关闭**：停止Python服务

### 前端窗口
- **标题**：前端服务 - Vue (端口:5173)
- **内容**：Vite开发服务器日志
- **关闭**：停止前端服务

**优点：**
- 易于调试和查看日志
- 可以单独重启某个服务
- 错误信息直观显示

## ⚠️ 常见问题

### Q1: start.bat提示"未找到Java"

**解决方案：**
1. 安装JDK 17+
2. 在`config.bat`中配置`JAVA_HOME`
3. 或将Java添加到系统PATH

### Q2: 后端编译失败

**解决方案：**
1. 确认Maven已正确安装
2. 检查网络连接（下载依赖）
3. 手动编译：
```bash
cd backend
mvn clean package -DskipTests
```

### Q3: Python服务启动失败

**解决方案：**
1. 检查Python版本（需要3.8+）
2. 安装依赖：
```bash
cd python-service
pip install -r requirements.txt
```
3. 如果使用Conda，确认环境已激活

### Q4: 前端显示空白

**解决方案：**
1. 检查后端是否启动
2. 清除node_modules重新安装：
```bash
cd frontend
rmdir /s /q node_modules
npm install
```

### Q5: stop.bat无法停止服务

**解决方案：**
1. 手动关闭服务窗口
2. 使用任务管理器结束进程
3. 重启计算机（终极方案）

### Q6: 端口被占用

**解决方案：**
1. 运行`status.bat`检查哪个端口被占用
2. 找到占用端口的进程：
```bash
netstat -ano | findstr :8080
netstat -ano | findstr :5000
netstat -ano | findstr :5173
```
3. 结束进程：
```bash
taskkill /F /PID <进程ID>
```

## 💡 高级技巧

### 自定义端口

如需修改服务端口，需要同时修改：

**后端端口：**
```yaml
# backend/src/main/resources/application.yml
server:
  port: 8081  # 修改为新端口
```

**Python端口：**
```python
# python-service/config.py
APP_PORT = 5001  # 修改为新端口
```

**前端端口：**
```javascript
// frontend/vite.config.js
export default defineConfig({
  server: {
    port: 5174  // 修改为新端口
  }
})
```

### 后台运行（不显示窗口）

如果不需要看到服务窗口，可以修改`start.bat`：

将：
```batch
start "服务名" cmd /k "命令"
```

改为：
```batch
start /b cmd /c "命令 > logs\service.log 2>&1"
```

### 自动启动（开机启动）

1. 创建快捷方式到`start.bat`
2. 按`Win+R`，输入`shell:startup`
3. 将快捷方式复制到启动文件夹

## 📊 脚本对比

| 功能 | start.bat | stop.bat | status.bat | clean.bat |
|------|-----------|----------|------------|-----------|
| 环境检查 | ✅ | ❌ | ✅ | ❌ |
| 启动服务 | ✅ | ❌ | 可调用 | ❌ |
| 停止服务 | ❌ | ✅ | 可调用 | ❌ |
| 状态检测 | 部分 | ✅ | ✅ | ❌ |
| 交互确认 | ❌ | ✅ | ✅ | ❌ |
| 独立窗口 | ✅ | ❌ | ❌ | ❌ |
| 日志清理 | ❌ | 可选 | ❌ | ✅ |
| 清理缓存 | ❌ | ❌ | ❌ | ✅ |
| 清理编译产物 | ❌ | ❌ | ❌ | ✅ |

## 🎯 最佳实践

1. **首次使用**：先运行`status.bat`检查环境
2. **开发调试**：使用`start.bat`的独立窗口
3. **生产部署**：修改为后台运行模式
4. **定期维护**：
   - 使用`clean.bat`清理临时文件（每周或每次开发前）
   - 使用`stop.bat`清理日志（关闭服务时）
5. **快速检查**：使用`status.bat`监控状态
6. **磁盘空间**：定期运行`clean.bat`释放空间

## 📞 技术支持

如果遇到脚本相关问题：
1. 检查`config.bat`配置是否正确
2. 查看服务窗口的错误信息
3. 运行`status.bat`确认服务状态
4. 查阅本文档的常见问题部分

祝使用愉快！🎉

