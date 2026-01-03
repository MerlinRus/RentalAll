# RentalAll - Система бронирования площадок для мероприятий

## О проекте

**RentalAll** - это веб-агрегатор площадок и аудиторий для проведения мероприятий. Система предоставляет удобный поиск, просмотр, бронирование и управление площадками для клиентов и организаторов.

### Дипломная работа
**Тема:** "Разработка информационной системы-агрегатора для бронирования площадок и аудиторий для мероприятий"

## Технологический стек

### Backend
- **Python 3.10+**
- **Django 4.2** - веб-фреймворк
- **Django REST Framework 3.14** - создание REST API
- **PostgreSQL** - база данных
- **JWT** - аутентификация
- **Django CORS Headers** - поддержка CORS

### Frontend
- **React 18** - библиотека для построения UI
- **React Router** - маршрутизация
- **Axios** - HTTP-клиент
- **Material-UI** - компоненты UI
- **React DatePicker** - выбор даты
- **React Toastify** - уведомления

## Архитектура системы

### Роли пользователей
1. **Гость** - просмотр каталога площадок
2. **Пользователь** - регистрация, бронирование, отзывы
3. **Администратор** - управление системой, модерация

### Основные модули

#### Backend (Django)
- **users** - пользователи и аутентификация
- **venues** - площадки и категории
- **bookings** - бронирования и платежи
- **reviews** - отзывы и рейтинги

#### Frontend (React)
- Главная страница
- Каталог площадок с фильтрами
- Детальная страница площадки
- Личный кабинет
- Страница бронирований
- Админ-панель

## База данных

### Основные таблицы
- `users_user` - пользователи
- `venues` - площадки
- `venue_images` - фотографии площадок
- `categories` - категории площадок
- `venue_categories` - связь площадок и категорий (M:N)
- `bookings` - бронирования
- `payments` - платежи
- `reviews` - отзывы

## Установка и запуск

### Требования
- Python 3.10 или выше
- Node.js 16 или выше
- PostgreSQL 12 или выше

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd rentalall
```

### 2. Настройка Backend

```bash
cd backend

# Создание виртуального окружения
python -m venv venv

# Активация виртуального окружения
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Создание файла .env на основе .env.example
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac

# Редактируйте .env файл, укажите параметры базы данных
```

### 3. Настройка базы данных PostgreSQL

```sql
-- Создайте базу данных в PostgreSQL
CREATE DATABASE rentalall_db;
CREATE USER rentalall_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE rentalall_db TO rentalall_user;
```

### 4. Миграции и создание суперпользователя

```bash
# Применение миграций
python manage.py makemigrations
python manage.py migrate

# Создание суперпользователя
python manage.py createsuperuser

# Запуск сервера разработки
python manage.py runserver
```

Backend будет доступен по адресу: http://localhost:8000

### 5. Настройка Frontend

```bash
cd frontend

# Установка зависимостей
npm install

# Запуск сервера разработки
npm start
```

Frontend будет доступен по адресу: http://localhost:3000

## API Документация

После запуска backend, документация API доступна по адресам:
- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/

## Основные эндпоинты API

### Аутентификация
- `POST /api/users/register/` - регистрация
- `POST /api/users/login/` - вход (получение JWT токена)
- `GET /api/users/profile/` - профиль пользователя
- `POST /api/users/change-password/` - смена пароля

### Площадки
- `GET /api/venues/` - список площадок
- `GET /api/venues/{id}/` - детали площадки
- `POST /api/venues/` - создание площадки (админ)
- `GET /api/venues/categories/` - категории

### Бронирования
- `GET /api/bookings/` - список бронирований
- `POST /api/bookings/` - создание бронирования
- `POST /api/bookings/{id}/cancel/` - отмена бронирования
- `POST /api/bookings/{id}/confirm/` - подтверждение (админ)

### Платежи
- `POST /api/bookings/payments/` - создание платежа
- `POST /api/bookings/payments/{id}/process/` - обработка платежа

### Отзывы
- `GET /api/reviews/` - список отзывов
- `POST /api/reviews/create/` - создание отзыва
- `POST /api/reviews/{id}/approve/` - одобрение (админ)

## Административная панель

Django Admin доступен по адресу: http://localhost:8000/admin

## Функциональность

### Для пользователей
- ✅ Регистрация и авторизация
- ✅ Просмотр каталога площадок
- ✅ Фильтрация по категориям, цене, вместимости
- ✅ Детальная информация о площадке
- ✅ Создание бронирования
- ✅ Онлайн оплата (имитация)
- ✅ Личный кабинет
- ✅ История бронирований
- ✅ Оставление отзывов

### Для администраторов
- ✅ Управление площадками
- ✅ Модерация отзывов
- ✅ Управление бронированиями
- ✅ Статистика системы
- ✅ Django Admin панель

## Структура проекта

```
rentalall/
├── backend/              # Django backend
│   ├── rentalall/       # Настройки проекта
│   ├── users/           # Приложение пользователей
│   ├── venues/          # Приложение площадок
│   ├── bookings/        # Приложение бронирований
│   ├── reviews/         # Приложение отзывов
│   ├── media/           # Медиа файлы
│   └── requirements.txt # Зависимости Python
│
├── frontend/            # React frontend
│   ├── public/         # Публичные файлы
│   ├── src/
│   │   ├── components/ # React компоненты
│   │   ├── pages/      # Страницы
│   │   ├── services/   # API сервисы
│   │   ├── context/    # React контексты
│   │   └── App.js      # Главный компонент
│   └── package.json    # Зависимости npm
│
└── README.md           # Документация
```

## Развертывание в продакшн

### Backend (Django)
1. Настройте `DEBUG=False` в `.env`
2. Настройте `ALLOWED_HOSTS`
3. Соберите статические файлы: `python manage.py collectstatic`
4. Используйте Gunicorn для запуска: `gunicorn rentalall.wsgi:application`
5. Настройте Nginx как reverse proxy

### Frontend (React)
1. Создайте production build: `npm run build`
2. Разверните содержимое папки `build` на веб-сервере

## Автор

Пивоваров Марк

## Лицензия

Этот проект создан в образовательных целях.

