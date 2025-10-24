# MySQL 8.0 安装到D盘指南

## 📥 方法1：使用官方安装器（推荐）

### 步骤1：下载MySQL安装器

访问官网下载：https://dev.mysql.com/downloads/installer/

选择：**mysql-installer-community-8.0.40.0.msi**

### 步骤2：运行安装器

1. 双击下载的 `.msi` 文件
2. 选择安装类型：**Custom** (自定义安装)

### 步骤3：选择安装路径 ⭐

**重要：在这一步指定D盘路径**

- **MySQL Server 安装路径**: `D:\MySQL\MySQL Server 8.0\`
- **数据存储路径**: `D:\MySQL\data\`

### 步骤4：配置MySQL

1. **Server Configuration Type**: 
   
   - 选择 `Development Computer`

2. **端口设置**:
   
   - 保持默认 `3306`

3. **Root密码设置**:
   
   - 输入密码: `root`
   - 确认密码: `root`

4. **Windows服务配置**:
   
   - ✅ 勾选 `Configure MySQL Server as a Windows Service`
   - 服务名称: `MySQL80`
   - ✅ 勾选 `Start the MySQL Server at System Startup`

5. **字符集设置**:
   
   - 选择 `Use UTF-8 (utf8mb4)`

### 步骤5：完成安装

点击 `Execute` 开始安装，等待完成。

---

## 📥 方法2：使用ZIP压缩包（手动安装）

### 步骤1：下载ZIP包

访问：https://dev.mysql.com/downloads/mysql/

选择：**Windows (x86, 64-bit), ZIP Archive**

### 步骤2：解压到D盘

将下载的ZIP文件解压到：`D:\MySQL\`

### 步骤3：创建配置文件

在 `D:\MySQL\` 目录下创建 `my.ini` 文件：

```ini
[mysqld]
# 设置MySQL安装目录
basedir=D:/MySQL
# 设置数据存储目录
datadir=D:/MySQL/data
# 设置端口
port=3306
# 字符集
character-set-server=utf8mb4
collation-server=utf8mb4_unicode_ci
# 默认存储引擎
default-storage-engine=INNODB
# 最大连接数
max_connections=200
# 允许的最大数据包
max_allowed_packet=16M

[mysql]
# 默认字符集
default-character-set=utf8mb4

[client]
port=3306
default-character-set=utf8mb4
```

### 步骤4：初始化数据库

以**管理员身份**打开PowerShell，执行：

```powershell
# 进入MySQL bin目录
cd D:\MySQL\bin

# 初始化数据库
.\mysqld --initialize --console

# 注意：会输出临时root密码，请记录！
```

### 步骤5：安装Windows服务

```powershell
# 安装MySQL服务
.\mysqld --install MySQL80 --defaults-file="D:\MySQL\my.ini"

# 启动服务
net start MySQL80
```

### 步骤6：修改root密码

```powershell
# 使用临时密码登录
.\mysql -u root -p
# 输入刚才记录的临时密码

# 在MySQL命令行中执行：
ALTER USER 'root'@'localhost' IDENTIFIED BY 'root';
FLUSH PRIVILEGES;
EXIT;
```

---

## 🗄️ 创建项目数据库

安装完成后，创建项目所需的数据库：

```powershell
# 方法1：命令行
D:\MySQL\bin\mysql -u root -p

# 输入密码：root

# 在MySQL中执行：
CREATE DATABASE behavior_detection CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
SHOW DATABASES;
EXIT;
```

或者使用图形化工具（推荐）：

- **MySQL Workbench**: https://dev.mysql.com/downloads/workbench/
- **Navicat**: https://www.navicat.com.cn/
- **HeidiSQL**: https://www.heidisql.com/

---

## ✅ 验证安装

```powershell
# 检查MySQL服务状态
net start | findstr MySQL

# 测试连接
D:\MySQL\bin\mysql -u root -p -e "SELECT VERSION();"
```

---

## 📝 配置项目

安装完成后，确认 `backend/src/main/resources/application.yml` 中的配置：

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/behavior_detection
    username: root
    password: root
    driver-class-name: com.mysql.cj.jdbc.Driver
```

---

## 🔧 常见问题

### Q1: 服务启动失败

```powershell
# 查看错误日志
type D:\MySQL\data\*.err
```

### Q2: 无法连接数据库

- 检查MySQL服务是否运行：`net start MySQL80`
- 检查端口3306是否被占用：`netstat -ano | findstr 3306`

### Q3: 忘记root密码

```powershell
# 停止服务
net stop MySQL80

# 跳过密码验证启动
D:\MySQL\bin\mysqld --skip-grant-tables

# 另开窗口登录并重置密码
D:\MySQL\bin\mysql -u root
USE mysql;
UPDATE user SET authentication_string='' WHERE user='root';
FLUSH PRIVILEGES;
EXIT;

# 重启MySQL服务
net stop MySQL80
net start MySQL80
```

---

## 🎯 安装完成后

运行项目启动脚本：

```bat
start.bat
```

访问：http://localhost:5173

默认账号：`admin` / `admin123`

---

**安装路径总结：**

- MySQL程序：`D:\MySQL\`
- 数据文件：`D:\MySQL\data\`
- 配置文件：`D:\MySQL\my.ini`
- 日志文件：`D:\MySQL\data\*.log`
