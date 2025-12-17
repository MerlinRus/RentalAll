#!/bin/bash

echo "======================================"
echo "RentalAll - Запуск проекта (Linux/Mac)"
echo "======================================"
echo ""

# Проверка виртуального окружения
if [ ! -d "backend/venv" ]; then
    echo "Виртуальное окружение не найдено!"
    echo "Пожалуйста, сначала выполните установку:"
    echo "python3 -m venv backend/venv"
    echo "source backend/venv/bin/activate"
    echo "pip install -r backend/requirements.txt"
    exit 1
fi

# Запуск Backend
echo "Запуск Backend сервера..."
cd backend
source venv/bin/activate
python manage.py runserver &
BACKEND_PID=$!
cd ..

# Ожидание запуска Backend
echo "Ожидание запуска Backend..."
sleep 5

# Запуск Frontend
echo "Запуск Frontend сервера..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "======================================"
echo "Проект запущен!"
echo "======================================"
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "Admin:    http://localhost:8000/admin"
echo "API Docs: http://localhost:8000/api/docs/"
echo "======================================"
echo ""
echo "Для остановки нажмите Ctrl+C"
echo ""

# Функция для остановки серверов при завершении
cleanup() {
    echo ""
    echo "Остановка серверов..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "Серверы остановлены"
    exit 0
}

# Обработка сигнала завершения
trap cleanup SIGINT SIGTERM

# Ожидание завершения
wait

