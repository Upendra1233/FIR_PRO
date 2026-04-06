@echo off
echo.
echo ====================================
echo Stopping FIR_PRO Services...
echo ====================================
echo.

REM Stop Nginx
taskkill /IM nginx.exe /F 2>nul
echo Nginx stopped.

REM Stop Gunicorn, Celery Worker, Celery Beat
taskkill /IM python.exe /F 2>nul
echo Python processes stopped.

echo.
echo ====================================
echo All services stopped!
echo ====================================
echo.
pause