@echo off
REM SQL Security HUD - Windows Startup Script

echo ========================================
echo SQL Server Security HUD
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

REM Check if .env exists
if not exist ".env" (
    echo WARNING: .env file not found
    echo Creating .env from .env.example...

    if exist ".env.example" (
        copy ".env.example" ".env"
        echo Created .env file. Please edit it with your SQL Server credentials
        echo Opening notepad...
        notepad ".env"
    ) else (
        echo ERROR: .env.example not found
        pause
        exit /b 1
    )
)

REM Check if dependencies are installed
echo.
echo Checking Python dependencies...
python -c "import flask, pyodbc, flask_cors" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Start the application
echo.
echo ========================================
echo Starting SQL Security HUD...
echo ========================================
echo.
echo Access the application at: http://localhost:5000
echo.
echo Demo Login:
echo   Username: admin
echo   Password: admin123
echo.
echo Press CTRL+C to stop the server
echo.

python app.py
