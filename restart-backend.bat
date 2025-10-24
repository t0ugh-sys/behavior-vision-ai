@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo 重启后端服务
echo ========================================
echo.

:: 停止Java进程
echo [1/4] 停止现有后端服务...
taskkill /F /IM java.exe 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ✓ 后端服务已停止
) else (
    echo ℹ 后端服务未运行
)
timeout /t 2 /nobreak >nul
echo.

:: 编译后端
echo [2/4] 编译后端代码...
cd backend
if exist "C:\Program Files\Maven\apache-maven-3.9.9\bin\mvn.cmd" (
    call "C:\Program Files\Maven\apache-maven-3.9.9\bin\mvn.cmd" clean package -DskipTests
) else if exist mvnw.cmd (
    call mvnw.cmd clean package -DskipTests
) else (
    echo ✗ 找不到Maven，请手动编译
    pause
    exit /b 1
)

if %ERRORLEVEL% NEQ 0 (
    echo ✗ 编译失败
    pause
    exit /b 1
)
echo ✓ 编译成功
cd ..
echo.

:: 启动后端
echo [3/4] 启动后端服务...
cd backend\target
start "Behavior Detection Backend" java -jar behavior-detection-backend-1.0.0.jar
cd ..\..
timeout /t 3 /nobreak >nul
echo ✓ 后端服务已启动
echo.

:: 等待服务就绪
echo [4/4] 等待服务就绪...
timeout /t 5 /nobreak >nul

:: 检查服务状态
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8080/api/health' -TimeoutSec 5 -ErrorAction Stop; Write-Host '✓ 后端服务运行正常' -ForegroundColor Green } catch { Write-Host '✗ 后端服务可能未正常启动' -ForegroundColor Red }"

echo.
echo ========================================
echo 后端服务重启完成
echo 服务地址: http://localhost:8080
echo ========================================
echo.
echo 请检查新打开的后端控制台窗口查看日志
pause

