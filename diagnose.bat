@echo off
chcp 65001 >nul
title System Diagnosis

echo.
echo ========================================
echo    System Diagnosis
echo ========================================
echo.

echo [1] Checking Backend Service (Port 8080)...
netstat -ano | findstr ":8080" | findstr "LISTENING"
if errorlevel 1 (
    echo [X] Backend service is NOT running on port 8080
    echo [!] Please start backend service first
) else (
    echo [OK] Backend service is running
)

echo.
echo [2] Checking Python Service (Port 5000)...
netstat -ano | findstr ":5000" | findstr "LISTENING"
if errorlevel 1 (
    echo [X] Python service is NOT running on port 5000
    echo [!] Please start Python service first
) else (
    echo [OK] Python service is running
)

echo.
echo [3] Checking Frontend Service (Port 5173)...
netstat -ano | findstr ":5173" | findstr "LISTENING"
if errorlevel 1 (
    echo [X] Frontend service is NOT running on port 5173
    echo [!] Please start frontend service first
) else (
    echo [OK] Frontend service is running
)

echo.
echo [4] Testing Backend Health API...
curl -s http://localhost:8080/api/health 2>nul
if errorlevel 1 (
    echo [X] Cannot connect to backend
) else (
    echo.
    echo [OK] Backend is responding
)

echo.
echo ========================================
echo    Browser Instructions
echo ========================================
echo.
echo To fix the flickering issue:
echo.
echo 1. Open browser and press F12
echo 2. Go to Console tab
echo 3. Run these commands:
echo    localStorage.clear();
echo    sessionStorage.clear();
echo    location.reload();
echo.
echo 4. You should see login page WITHOUT flickering
echo 5. Try to login with: admin / admin123
echo.
echo If login button has no response:
echo    - Check Console tab for errors
echo    - Check Network tab to see if requests are sent
echo    - Make sure all services are running (see above)
echo.

pause

