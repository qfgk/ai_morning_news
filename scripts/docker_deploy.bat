@echo off
REM Docker Quick Deployment Script for Windows

echo ============================================================
echo  Morning News System - Docker Deployment
echo ============================================================
echo.

REM Check Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo Error: Docker is not installed
    echo Please install Docker Desktop first: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

REM Check .env file
if not exist .env (
    echo.
    echo Creating .env file from template...
    copy .env.docker.example .env >nul
    echo ✅ Created .env file
    echo.
    echo ⚠️  IMPORTANT: Please edit .env file and set:
    echo    - ZHIPUAI_API_KEY
    echo    - API_KEY
    echo.
    pause
)

REM Check if API_KEY is set
findstr /C:"your-secret-api-key-here" .env >nul 2>&1
if not errorlevel 1 (
    echo.
    echo Generating API key...
    python scripts\generate_api_key.py
    echo.
    echo ⚠️  Please update API_KEY in .env file
    pause
)

REM Build images
echo.
echo Building Docker images...
docker-compose build

if errorlevel 1 (
    echo Error: Docker build failed
    pause
    exit /b 1
)

REM Start services
echo.
echo Starting services...
docker-compose up -d

if errorlevel 1 (
    echo Error: Failed to start services
    pause
    exit /b 1
)

REM Wait for services
echo.
echo Waiting for services to be ready...
timeout /t 10 /nobreak >nul

REM Check status
echo.
echo Checking service status...
docker-compose ps

REM Initialize database
echo.
echo Initializing database...
docker-compose exec -T web python scripts\init_db.py

echo.
echo ============================================================
echo ✅ Deployment completed!
echo ============================================================
echo.
echo Services:
echo   - Web API:  http://localhost:5000
echo   - MySQL:    localhost:3306
echo   - Redis:    localhost:6379
echo.
echo Commands:
echo   - View logs:     docker-compose logs -f
echo   - Stop all:      docker-compose down
echo   - Restart:       docker-compose restart
echo   - Shell access:  docker-compose exec web bash
echo.
echo Press any key to exit...
pause >nul
