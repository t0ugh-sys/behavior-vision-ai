@echo off
chcp 65001 > nul
setlocal EnableDelayedExpansion

echo.
echo ========================================
echo    清理项目临时文件
echo ========================================
echo.

set /a CLEANED=0

:: 清理 Python 临时文件
echo [1/6] 清理 Python 临时文件...
if exist "python-service\temp\*" (
    del /F /Q "python-service\temp\*" 2>nul
    set /a CLEANED+=1
    echo [✓] Python temp 文件已清理
) else (
    echo [·] Python temp 文件夹为空
)

:: 清理 Python 缓存
echo [2/6] 清理 Python 缓存...
if exist "python-service\__pycache__" (
    rd /S /Q "python-service\__pycache__" 2>nul
    set /a CLEANED+=1
    echo [✓] Python 缓存已清理
) else (
    echo [·] Python 缓存不存在
)

:: 清理 Maven 编译输出
echo [3/6] 清理 Maven 编译输出...
if exist "backend\target" (
    rd /S /Q "backend\target" 2>nul
    set /a CLEANED+=1
    echo [✓] Maven target 已清理
) else (
    echo [·] Maven target 不存在
)

:: 清理后端日志
echo [4/6] 清理后端日志...
if exist "backend\logs\*.log" (
    del /F /Q "backend\logs\*.log" 2>nul
    set /a CLEANED+=1
    echo [✓] 后端日志已清理
) else (
    echo [·] 后端日志不存在
)

:: 清理前端构建输出
echo [5/6] 清理前端构建输出...
if exist "frontend\dist" (
    rd /S /Q "frontend\dist" 2>nul
    set /a CLEANED+=1
    echo [✓] 前端 dist 已清理
) else (
    echo [·] 前端 dist 不存在
)

:: 清理根目录日志
echo [6/6] 清理根目录日志...
if exist "logs\*.log" (
    del /F /Q "logs\*.log" 2>nul
    set /a CLEANED+=1
    echo [✓] 根目录日志已清理
) else (
    echo [·] 根目录日志不存在
)

echo.
echo ========================================
echo    清理完成！共清理 %CLEANED% 项
echo ========================================
echo.
echo 提示：
echo  - node_modules 和上传的文件未被清理
echo  - 如需清理 node_modules，请手动执行：
echo    cd frontend ^&^& rd /S /Q node_modules
echo.

pause

