@echo off
setlocal
title Fluid Controls RFQ

cd /d "%~dp0"

echo ==========================================
echo        Fluid Controls RFQ
echo ==========================================
echo.

docker info >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not running.
    echo.
    echo Start Docker Desktop, wait for Docker Engine
    echo to be ready, then run start.bat again.
    echo.
    pause
    exit /b 1
)

if not exist ".env" (
    echo Creating .env...
    copy ".env.example" ".env" >nul
)

echo Starting application...
echo First launch may take several minutes.
echo.

docker compose up -d --build

if errorlevel 1 (
    echo.
    echo ERROR: Application failed to start.
    echo Run: docker compose logs
    echo.
    pause
    exit /b 1
)

echo.
docker compose ps

echo.
echo ==========================================
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8000
echo Swagger:  http://localhost:8000/docs
echo ==========================================
echo.

start "" http://localhost:3000
start "" http://localhost:8000/docs

pause
