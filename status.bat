@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
title Detection System - Status

echo.
echo ========================================
echo    Service Status Check
echo ========================================
echo.

set RUNNING=0

REM Check Backend (port 8080)
netstat -ano | findstr ":8080" | findstr "LISTENING" >nul 2>&1
if errorlevel 1 (
    echo [X] Backend Service (port 8080^): Not Running
) else (
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8080" ^| findstr "LISTENING"') do (
        echo [OK] Backend Service (port 8080^): Running (PID: %%a^)
        set /a RUNNING+=1
        goto :backend_done
    )
)
:backend_done

REM Check Python Service (port 5000)
netstat -ano | findstr ":5000" | findstr "LISTENING" >nul 2>&1
if errorlevel 1 (
    echo [X] Python Service (port 5000^): Not Running
) else (
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5000" ^| findstr "LISTENING"') do (
        echo [OK] Python Service (port 5000^): Running (PID: %%a^)
        set /a RUNNING+=1
        goto :python_done
    )
)
:python_done

REM Check Frontend (port 5173)
netstat -ano | findstr ":5173" | findstr "LISTENING" >nul 2>&1
if errorlevel 1 (
    echo [X] Frontend Service (port 5173^): Not Running
) else (
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5173" ^| findstr "LISTENING"') do (
        echo [OK] Frontend Service (port 5173^): Running (PID: %%a^)
        set /a RUNNING+=1
        goto :frontend_done
    )
)
:frontend_done

echo.
echo ========================================
echo    Summary: !RUNNING!/3 services running
echo ========================================
echo.

if !RUNNING!==0 (
    echo [!] No services are running
    echo [!] Run start.bat to start all services
) else if !RUNNING!==3 (
    echo [OK] All services are running normally!
    echo.
    echo Access URLs:
    echo   Frontend: http://localhost:5173
    echo   Backend:  http://localhost:8080
    echo   Python:   http://localhost:5000
) else (
    echo [!] Some services are not running
    echo [!] Check the logs and restart if needed
)

echo.
pause
