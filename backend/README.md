# RentalAll Backend

## Django REST API для системы бронирования площадок

### Технологии
- Django 4.2
- Django REST Framework 3.14
- PostgreSQL
- JWT Authentication

### Установка

1. Создайте виртуальное окружение:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Создайте файл `.env`:
```bash
copy .env.example .env
```

4. Настройте параметры в `.env`:
```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=rentalall_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

CORS_ALLOWED_ORIGINS=http://localhost:3000
```

5. Примените миграции:
```bash
python manage.py makemigrations
python manage.py migrate
```

6. Создайте суперпользователя:
```bash
python manage.py createsuperuser
```

7. Запустите сервер:
```bash
python manage.py runserver
```

### Структура приложений

#### users
Управление пользователями и аутентификация
- Модель: расширенная User модель с ролями (user/admin)
- API: регистрация, вход, профиль, смена пароля

#### venues
Управление площадками
- Модели: Venue, VenueImage, Category, VenueCategory
- API: CRUD площадок, загрузка изображений, фильтрация

#### bookings
Бронирования и платежи
- Модели: Booking, Payment
- API: создание брони, оплата, отмена, подтверждение

#### reviews
Отзывы и рейтинги
- Модель: Review
- API: создание отзывов, модерация

### API Endpoints

Полная документация: http://localhost:8000/api/docs/

### Команды управления

```bash
# Создание миграций
python manage.py makemigrations

# Применение миграций
python manage.py migrate

# Создание суперпользователя
python manage.py createsuperuser

# Запуск сервера
python manage.py runserver

# Сбор статических файлов
python manage.py collectstatic

# Создание дампа БД
python manage.py dumpdata > data.json

# Загрузка дампа БД
python manage.py loaddata data.json
```

### Тестирование API

Используйте Swagger UI для тестирования API:
http://localhost:8000/api/docs/

Или используйте curl/Postman:

```bash
# Регистрация
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@test.com","password":"testpass123","password2":"testpass123"}'

# Вход
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"testpass123"}'

# Получение списка площадок
curl -X GET http://localhost:8000/api/venues/
```

