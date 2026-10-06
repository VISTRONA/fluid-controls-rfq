@echo off
setlocal
cd /d "%~dp0"
docker info >nul 2>&1
if errorlevel 1 (
  echo Start Docker Desktop and wait for it to be ready.
  pause
  exit /b 1
)
if not exist ".env" copy ".env.example" ".env" >nul
docker compose up -d --build --wait
if errorlevel 1 (
  echo Startup failed. Check docker compose logs.
  pause
  exit /b 1
)
start "" http://localhost:5000
pause
