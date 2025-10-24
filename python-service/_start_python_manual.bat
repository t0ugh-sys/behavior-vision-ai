@echo off
cd /d C:\Users\Wells\Desktop\detection\python-service
call D:\miniconda3\Scripts\activate.bat D:\miniconda3
if errorlevel 1 (
    echo [X] Failed to initialize Conda
    pause
    exit /b 1
)
call conda activate ultralytics
if errorlevel 1 (
    echo [X] Failed to activate environment: ultralytics
    pause
    exit /b 1
)
echo.
echo ========================================
echo    Python Detection Service
echo    Conda Environment: ultralytics
echo ========================================
echo.
python app.py

