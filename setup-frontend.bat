@echo off
echo Setting up AI Detector - Frontend
echo ====================================

:: Check Node.js
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo Node.js is not installed. Please install Node.js 18+ first.
    exit /b 1
)

echo Node.js version:
node --version

:: Install dependencies
echo.
echo Installing dependencies...
cd frontend
call npm install

:: Copy environment file
if not exist .env.local (
    echo.
    echo Creating environment file...
    copy .env.example .env.local
    echo Created .env.local - please update with your settings
)

echo.
echo Frontend setup complete!
echo.
echo To start the development server:
echo   cd frontend
echo   npm run dev
echo.
pause
