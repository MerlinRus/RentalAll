@echo off
echo ======================================
echo RentalAll - Запуск проекта (Windows)
echo ======================================
echo.

echo Проверка наличия виртуального окружения...
if not exist "backend\venv" (
    echo Виртуальное окружение не найдено!
    echo Пожалуйста, сначала выполните установку:
    echo python -m venv backend\venv
    echo backend\venv\Scripts\activate
    echo pip install -r backend\requirements.txt
    pause
    exit /b 1
)

echo Запуск Backend сервера...
start "RentalAll Backend" cmd /k "cd backend && venv\Scripts\activate && python manage.py runserver"

echo Ожидание запуска Backend...
timeout /t 5 /nobreak >nul

echo Запуск Frontend сервера...
start "RentalAll Frontend" cmd /k "cd frontend && npm start"

echo.
echo ======================================
echo Проект запущен!
echo ======================================
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo Admin:    http://localhost:8000/admin
echo API Docs: http://localhost:8000/api/docs/
echo ======================================
echo.
echo Для остановки закройте открывшиеся окна терминалов
echo.
pause

