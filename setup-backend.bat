@echo off
echo Setting up AI Detector - Backend
echo ===================================

:: Check Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python 3 is not installed. Please install Python 3.9+ first.
    exit /b 1
)

echo Python version:
python --version

:: Create virtual environment
echo.
echo Creating virtual environment...
cd backend
python -m venv venv

:: Activate virtual environment and install dependencies
echo.
echo Installing dependencies...
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt

:: Copy environment file
if not exist .env (
    echo.
    echo Creating environment file...
    copy .env.example .env
    echo Created .env - please update with your settings
)

:: Create directories
echo.
echo Creating required directories...
mkdir uploads 2>nul
mkdir temp 2>nul
mkdir models 2>nul

echo.
echo Backend setup complete!
echo.
echo To start the development server:
echo   cd backend
echo   venv\Scripts\activate
echo   uvicorn main:app --reload
echo.
echo Don't forget to:
echo   1. Start MongoDB
echo   2. Update .env with your configuration
echo.
pause
