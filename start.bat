@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
title Human Behavior Detection System - Startup

echo.
echo ========================================
echo    Human Behavior Detection System
echo ========================================
echo.

REM Load configuration file
if exist config.bat (
    call config.bat
    echo [OK] Configuration loaded
) else (
    echo [!] config.bat not found, using defaults
)
echo.

REM ===========================================
REM Environment Check
REM ===========================================
echo ========================================
echo    Environment Check
echo ========================================
echo.

REM Check Java
if defined JAVA_HOME (
    set "PATH=%JAVA_HOME%\bin;%PATH%"
)
where java >nul 2>&1
if errorlevel 1 (
    echo [X] Java not found
    echo [!] Please install Java 17+ or configure JAVA_HOME
    pause
    exit /b 1
)
for /f "tokens=3" %%i in ('java -version 2^>^&1 ^| findstr "version"') do (
    echo [OK] Java: %%i
    goto :java_ok
)
:java_ok

REM Check Maven
if defined MAVEN_HOME (
    set "PATH=%MAVEN_HOME%\bin;%PATH%"
)
where mvn >nul 2>&1
if errorlevel 1 (
    echo [!] Maven not found, will try to run jar directly
    set MAVEN_FOUND=0
) else (
    for /f "tokens=3" %%i in ('mvn -version 2^>^&1 ^| findstr "Apache Maven"') do (
        echo [OK] Maven: %%i
        set MAVEN_FOUND=1
        goto :maven_ok
    )
)
:maven_ok

REM Check Node.js
if defined NODE_PATH (
    set "PATH=%NODE_PATH%;%PATH%"
)
where node >nul 2>&1
if errorlevel 1 (
    echo [X] Node.js not found
    echo [!] Please install Node.js or configure NODE_PATH
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('node -v') do (
    echo [OK] Node.js: %%i
)

REM Check Python (Conda)
set PYTHON_FOUND=0
set CONDA_FOUND=0

REM Try to find conda if CONDA_PATH and CONDA_ENV are specified
if defined CONDA_PATH (
    if defined CONDA_ENV (
        echo [*] Checking Conda installation at: %CONDA_PATH%
        
        REM Check if conda exists at specified path
        if exist "%CONDA_PATH%\Scripts\conda.exe" (
            echo [OK] Conda found at: %CONDA_PATH%
            
            REM Initialize conda for this session
            call "%CONDA_PATH%\Scripts\activate.bat" "%CONDA_PATH%" >nul 2>&1
            
            REM Activate the specified environment
            call conda activate %CONDA_ENV% >nul 2>&1
            if not errorlevel 1 (
                echo [OK] Conda environment activated: %CONDA_ENV%
                set CONDA_FOUND=1
                set PYTHON_FOUND=1
            ) else (
                echo [!] Failed to activate environment: %CONDA_ENV%
                echo [!] Make sure the environment exists
                echo [!] Using system Python instead
            )
        ) else (
            echo [!] Conda not found at: %CONDA_PATH%
            echo [!] Please check CONDA_PATH in config.bat
            echo [!] Using system Python instead
        )
    )
)

REM If conda not found or not configured, use system Python
if !PYTHON_FOUND!==0 (
    if defined PYTHON_PATH (
        set "PATH=%PYTHON_PATH%;%PATH%"
    )
    where python >nul 2>&1
    if errorlevel 1 (
        echo [X] Python not found
        echo [!] Please install Python or configure PYTHON_PATH/CONDA_ENV
        pause
        exit /b 1
    )
    for /f "tokens=*" %%i in ('python --version') do (
        echo [OK] Python: %%i
        set PYTHON_FOUND=1
    )
)

echo.
echo ========================================
echo    Starting Services
echo ========================================
echo.

REM ===========================================
REM 1. Start Backend (Spring Boot)
REM ===========================================
echo [1/3] Starting Backend Service...

cd backend

REM Check if backend is already running
netstat -ano | findstr ":8080.*LISTENING" >nul 2>&1
if not errorlevel 1 (
    echo [!] Backend service already running on port 8080
    echo [!] Skipping compilation to avoid file conflicts
    set SKIP_COMPILE=1
) else (
    set SKIP_COMPILE=0
)

REM Check if Maven is available and compile if needed
if %MAVEN_FOUND%==1 (
    if %SKIP_COMPILE%==0 (
        echo [*] Compiling backend with Maven...
        call mvn clean package -DskipTests
        if errorlevel 1 (
            echo [!] Compilation failed, will try to use existing jar...
            REM Don't exit, try to use existing jar
        ) else (
            echo [OK] Compilation successful
        )
    ) else (
        echo [OK] Using existing compiled jar (service already running)
    )
) else (
    echo [!] Maven not found, will try to use existing jar...
)

REM Find the compiled jar file
set "JAR_FILE="
for %%f in (target\*.jar) do (
    set "FILENAME=%%~nf"
    if not "!FILENAME!"=="!FILENAME:.original=!" (
        REM Skip .original files
    ) else (
        set "JAR_FILE=%%f"
    )
)

if defined JAR_FILE (
    echo [OK] Found jar: !JAR_FILE!
    
    REM Check if backend is already running
    netstat -ano | findstr ":8080.*LISTENING" >nul 2>&1
    if not errorlevel 1 (
        echo [OK] Backend service is already running on port 8080
        echo [!] Skipping startup to avoid duplicate instances
    ) else (
        echo [*] Starting backend service...
        
        REM Create temporary startup script for backend
        set "BACKEND_START_SCRIPT=%CD%\_start_backend.bat"
        (
            echo @echo off
            echo cd /d "%CD%"
            echo echo Backend Service
            echo echo.
            echo java -jar "!JAR_FILE!"
        ) > "!BACKEND_START_SCRIPT!"
        start "Backend Service" cmd /k "!BACKEND_START_SCRIPT!"
        echo [OK] Backend started in separate window
    )
) else (
    echo [X] No jar file found
    if %MAVEN_FOUND%==0 (
        echo [!] Please install Maven or compile the backend manually
    )
    cd ..
    pause
    exit /b 1
)

cd ..
timeout /t 3 /nobreak >nul

REM ===========================================
REM 2. Start Python Service
REM ===========================================
echo.
echo [2/3] Starting Python Detection Service...

cd python-service

REM Check if Python service is already running
netstat -ano | findstr ":5000.*LISTENING" >nul 2>&1
if not errorlevel 1 (
    echo [OK] Python service is already running on port 5000
    echo [!] Skipping startup to avoid duplicate instances
    cd ..
    goto :skip_python
)

REM Create temporary startup script for Python service
set "PYTHON_START_SCRIPT=%CD%\_start_python.bat"
if %CONDA_FOUND%==1 (
    REM Use conda environment
    echo [*] Starting with Conda environment: %CONDA_ENV%
    (
        echo @echo off
        echo cd /d "%CD%"
        echo call "%CONDA_PATH%\Scripts\activate.bat" "%CONDA_PATH%"
        echo if errorlevel 1 (
        echo     echo [X] Failed to initialize Conda
        echo     pause
        echo     exit /b 1
        echo ^)
        echo call conda activate %CONDA_ENV%
        echo if errorlevel 1 (
        echo     echo [X] Failed to activate environment: %CONDA_ENV%
        echo     pause
        echo     exit /b 1
        echo ^)
        echo echo.
        echo echo ========================================
        echo echo    Python Detection Service
        echo echo    Conda Environment: %CONDA_ENV%
        echo echo ========================================
        echo echo.
        echo python app.py
    ) > "%PYTHON_START_SCRIPT%"
    start "Python Detection Service" cmd /k "%PYTHON_START_SCRIPT%"
) else (
    REM Use system Python
    echo [*] Starting with system Python
    REM Check if pip is available
    python -m pip --version >nul 2>&1
    if errorlevel 1 (
        echo [X] pip not found, cannot install dependencies
        cd ..
        pause
        exit /b 1
    )
    
    REM Check dependencies
    python -c "import fastapi" >nul 2>&1
    if errorlevel 1 (
        echo [!] Installing Python dependencies...
        python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
        if errorlevel 1 (
            echo [X] Failed to install dependencies
            cd ..
            pause
            exit /b 1
        )
    )
    
    (
        echo @echo off
        echo cd /d "%CD%"
        echo echo Python Detection Service
        echo echo.
        echo python app.py
    ) > "%PYTHON_START_SCRIPT%"
    start "Python Detection Service" cmd /k "%PYTHON_START_SCRIPT%"
)

echo [OK] Python service started, separate window opened

cd ..

:skip_python
timeout /t 2 /nobreak >nul

REM ===========================================
REM 3. Start Frontend (Vue)
REM ===========================================
echo.
echo [3/3] Starting Frontend Service...

cd frontend

REM Check if Frontend service is already running
netstat -ano | findstr ":5173.*LISTENING" >nul 2>&1
if not errorlevel 1 (
    echo [OK] Frontend service is already running on port 5173
    echo [!] Skipping startup to avoid duplicate instances
    cd ..
    goto :skip_frontend
)

REM Check if node_modules exists
if not exist node_modules (
    echo [!] Installing frontend dependencies...
    call npm install
    if errorlevel 1 (
        echo [X] Failed to install dependencies
        cd ..
        pause
        exit /b 1
    )
)

start "Frontend Service" cmd /k "echo Frontend Service && echo. && npm run dev"

echo [OK] Frontend service started, separate window opened

cd ..

:skip_frontend

echo.
echo ========================================
echo    All Services Started!
echo ========================================
echo.
echo Service Status:
echo   Backend:  http://localhost:8080
echo   Python:   http://localhost:5000
echo   Frontend: http://localhost:5173
echo.
echo Opening browser...
timeout /t 5 /nobreak >nul
start http://localhost:5173
echo.
echo Press any key to exit this window...
echo (Service windows will remain open)
pause >nul
