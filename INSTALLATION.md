# Руководство по установке RentalAll

## Пошаговая инструкция

### Шаг 1: Установка необходимого ПО

#### 1.1 Python 3.10+
- Скачайте с https://www.python.org/downloads/
- При установке отметьте "Add Python to PATH"
- Проверьте установку: `python --version`

#### 1.2 Node.js 16+
- Скачайте с https://nodejs.org/
- Установите LTS версию
- Проверьте установку: `node --version` и `npm --version`

#### 1.3 PostgreSQL 12+
- Скачайте с https://www.postgresql.org/download/
- Запомните пароль для пользователя postgres
- Проверьте установку: `psql --version`

### Шаг 2: Создание базы данных

Запустите psql и выполните:

```sql
-- Подключитесь к PostgreSQL
psql -U postgres

-- Создайте базу данных
CREATE DATABASE rentalall_db;

-- Создайте пользователя (опционально)
CREATE USER rentalall_user WITH PASSWORD 'your_secure_password';

-- Выдайте права
GRANT ALL PRIVILEGES ON DATABASE rentalall_db TO rentalall_user;

-- Выйдите
\q
```

### Шаг 3: Настройка Backend

```bash
# Перейдите в папку проекта
cd путь/к/rentalall

# Перейдите в папку backend
cd backend

# Создайте виртуальное окружение
python -m venv venv

# Активируйте виртуальное окружение
# На Windows:
venv\Scripts\activate
# На Linux/Mac:
source venv/bin/activate

# Установите зависимости
pip install -r requirements.txt

# Создайте файл .env
# Windows:
copy .env.example .env
# Linux/Mac:
cp .env.example .env
```

### Шаг 4: Настройка .env файла

Откройте файл `backend/.env` и настройте:

```env
SECRET_KEY=django-insecure-your-secret-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=rentalall_db
DB_USER=postgres
DB_PASSWORD=ваш_пароль_postgres
DB_HOST=localhost
DB_PORT=5432

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Шаг 5: Применение миграций

```bash
# Убедитесь, что вы в папке backend с активированным venv
python manage.py makemigrations
python manage.py migrate
```

### Шаг 6: Создание администратора

```bash
python manage.py createsuperuser

# Введите:
# - Username (например: admin)
# - Email (например: admin@example.com)
# - Password (дважды)
```

### Шаг 7: Заполнение тестовыми данными (опционально)

Войдите в Django admin (http://localhost:8000/admin) и создайте:
- Несколько категорий (Конференц-зал, Актовый зал, Фотостудия)
- Несколько площадок с фотографиями

Или используйте Django shell:

```bash
python manage.py shell
```

```python
from venues.models import Category, Venue
from users.models import User

# Создание категорий
cat1 = Category.objects.create(name="Конференц-зал")
cat2 = Category.objects.create(name="Актовый зал")
cat3 = Category.objects.create(name="Фотостудия")

# Создание тестовой площадки
venue = Venue.objects.create(
    title="Большой конференц-зал",
    description="Просторный зал для конференций до 100 человек",
    capacity=100,
    price_per_hour=5000,
    address="Москва, ул. Примерная, д. 1",
    latitude=55.751244,
    longitude=37.618423,
    is_active=True
)
venue.categories.add(cat1)

print("Данные созданы!")
exit()
```

### Шаг 8: Запуск Backend сервера

```bash
# Убедитесь, что вы в папке backend
python manage.py runserver
```

Backend будет доступен: http://localhost:8000
Django Admin: http://localhost:8000/admin
API Docs: http://localhost:8000/api/docs/

### Шаг 9: Настройка Frontend

Откройте новый терминал:

```bash
# Перейдите в папку frontend
cd путь/к/rentalall/frontend

# Установите зависимости
npm install

# Запустите сервер разработки
npm start
```

Frontend автоматически откроется: http://localhost:3000

### Шаг 10: Проверка работы

1. Откройте http://localhost:3000
2. Перейдите в раздел "Регистрация"
3. Создайте учетную запись
4. Войдите в систему
5. Просмотрите каталог площадок
6. Попробуйте создать бронирование

## Возможные проблемы и решения

### Ошибка подключения к базе данных

**Проблема:** `django.db.utils.OperationalError: could not connect to server`

**Решение:**
- Убедитесь, что PostgreSQL запущен
- Проверьте параметры в `.env` файле
- Проверьте, что пользователь имеет права на базу данных

### Ошибка CORS

**Проблема:** Frontend не может обратиться к Backend

**Решение:**
- Убедитесь, что в `backend/.env` указано `CORS_ALLOWED_ORIGINS=http://localhost:3000`
- Перезапустите backend сервер

### Ошибка миграций

**Проблема:** `No migrations to apply` или ошибки миграций

**Решение:**
```bash
# Удалите миграции (кроме __init__.py)
# Удалите базу данных и создайте заново
# Выполните:
python manage.py makemigrations
python manage.py migrate
```

### Проблемы с виртуальным окружением

**Проблема:** Не активируется venv или не находятся команды

**Решение:**
- Windows: используйте PowerShell или CMD от имени администратора
- Linux/Mac: убедитесь, что используете `source venv/bin/activate`

### Порт уже занят

**Проблема:** `Error: That port is already in use`

**Решение:**
- Backend: запустите на другом порту `python manage.py runserver 8001`
- Frontend: выберите другой порт когда появится запрос

## Дополнительные команды

### Очистка базы данных

```bash
python manage.py flush
```

### Создание дампа БД

```bash
python manage.py dumpdata > data.json
```

### Загрузка дампа БД

```bash
python manage.py loaddata data.json
```

### Сборка Frontend для продакшн

```bash
cd frontend
npm run build
```

## Поддержка

При возникновении проблем:
1. Проверьте логи в терминале
2. Убедитесь, что все зависимости установлены
3. Проверьте версии Python и Node.js
4. Убедитесь, что PostgreSQL запущен

## Следующие шаги

После успешной установки:
1. Изучите API документацию: http://localhost:8000/api/docs/
2. Войдите в админку: http://localhost:8000/admin
3. Создайте тестовые данные
4. Протестируйте все функции системы

