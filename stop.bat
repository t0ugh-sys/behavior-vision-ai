@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
title Human Behavior Detection System - Stop

echo.
echo ========================================
echo    Stopping All Services
echo ========================================
echo.

set STOPPED=0

REM Stop Backend (port 8080)
echo [1/3] Stopping Backend Service (port 8080)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8080" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
    if not errorlevel 1 (
        echo [OK] Backend stopped (PID: %%a)
        set /a STOPPED+=1
    )
)

REM Stop Python Service (port 5000)
echo [2/3] Stopping Python Service (port 5000)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5000" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
    if not errorlevel 1 (
        echo [OK] Python service stopped (PID: %%a)
        set /a STOPPED+=1
    )
)

REM Stop Frontend (port 5173)
echo [3/3] Stopping Frontend Service (port 5173)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5173" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
    if not errorlevel 1 (
        echo [OK] Frontend stopped (PID: %%a)
        set /a STOPPED+=1
    )
)

REM Also kill any remaining node/java/python processes from detection
taskkill /F /IM "node.exe" /FI "WINDOWTITLE eq Frontend Service*" >nul 2>&1
taskkill /F /IM "java.exe" /FI "WINDOWTITLE eq Backend Service*" >nul 2>&1
taskkill /F /IM "python.exe" /FI "WINDOWTITLE eq Python Detection Service*" >nul 2>&1

echo.
echo ========================================
echo    Stopped !STOPPED! service(s)
echo ========================================
echo.

if !STOPPED!==0 (
    echo [!] No running services found
) else (
    echo [OK] All services have been stopped
)

REM Clean up temporary startup scripts
set CLEANED=0
if exist "python-service\_start_python.bat" (
    del /f /q "python-service\_start_python.bat" >nul 2>&1
    set /a CLEANED+=1
)
if exist "backend\_start_backend.bat" (
    del /f /q "backend\_start_backend.bat" >nul 2>&1
    set /a CLEANED+=1
)
if !CLEANED! GTR 0 (
    echo [OK] Cleaned up temporary files
)

echo.
pause
