@echo off
REM Start Gunicorn, Celery Worker, and Celery Beat

echo.
echo ====================================
echo Starting FIR_PRO Services...
echo ====================================
echo.

REM Activate virtual environment
call myenv\Scripts\activate.bat

REM Collect static files
echo Collecting static files...
python manage.py collectstatic --noinput

REM Start Gunicorn in a new window
echo Starting Gunicorn on 127.0.0.1:8000...
start "Gunicorn" cmd /k gunicorn -c gunicorn_config.py psn_project.wsgi

timeout /t 2

REM Start Celery Worker in a new window
echo Starting Celery Worker...
start "Celery Worker" cmd /k celery -A psn_project worker -l info --concurrency=4

timeout /t 2

REM Start Celery Beat in a new window
echo Starting Celery Beat...
start "Celery Beat" cmd /k celery -A psn_project beat -l info

timeout /t 2

REM Start Nginx in a new window
echo Starting Nginx...
start "Nginx" cmd /k cd C:\nginx && nginx.exe

echo.
echo ====================================
echo All services started!
echo ====================================
echo.
echo Access your app at: https://localhost
echo.
pause