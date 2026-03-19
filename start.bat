@echo off
setlocal
echo ==================================================
echo   🧠 Knowledge Synthesizer: Starting Dual-Server
echo ==================================================

REM 1. Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your PATH. 
    echo Please install Python 3.10+ and try again.
    pause
    exit /b
)

REM 2. Check for dependencies
echo [INFO] Ensuring backend dependencies are installed...
pip install -r backend/requirements.txt --quiet
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies. Check your internet connection.
    pause
    exit /b
)

REM 3. Start Backend in a separate window (Port 8000)
echo [INFO] Starting Backend Server (Port 8000)...
start "Backend (API)" cmd /c "cd backend && python main.py"

REM 4. Start Frontend in a separate window (Port 3000)
echo [INFO] Starting Frontend Server (Port 3000)...
start "Frontend (UI)" cmd /c "cd frontend && python -m http.server 3000"

REM 5. Wait for servers to initialize
echo [INFO] Waiting for servers to start (5s)...
timeout /t 5 /nobreak >nul

REM 6. Open Frontend
echo [INFO] Opening the application in your browser...
start http://localhost:3000

echo.
echo ==================================================
echo   🚀 Application is now running!
echo   Keep both command windows open while using the app.
echo   - UI: http://localhost:3000
echo   - API: http://localhost:8000
echo ==================================================
pause
