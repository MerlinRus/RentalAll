# API Документация RentalAll

## Базовый URL

```
http://localhost:8000/api
```

## Аутентификация

Система использует JWT (JSON Web Tokens) для аутентификации.

### Получение токена

```http
POST /api/users/login/
Content-Type: application/json

{
  "username": "user123",
  "password": "password123"
}
```

**Ответ:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Использование токена

Добавьте заголовок Authorization ко всем защищенным запросам:

```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### Обновление токена

```http
POST /api/users/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

## Эндпоинты API

### 👤 Пользователи

#### Регистрация

```http
POST /api/users/register/
Content-Type: application/json

{
  "username": "newuser",
  "email": "user@example.com",
  "password": "securepass123",
  "password2": "securepass123",
  "full_name": "Иван Иванов",
  "phone": "+79001234567"
}
```

**Ответ (201 Created):**
```json
{
  "user": {
    "id": 1,
    "username": "newuser",
    "email": "user@example.com",
    "full_name": "Иван Иванов",
    "phone": "+79001234567",
    "role": "user",
    "date_joined": "2025-12-11T10:00:00Z",
    "is_active": true
  },
  "message": "Пользователь успешно зарегистрирован"
}
```

#### Получение профиля

```http
GET /api/users/profile/
Authorization: Bearer {token}
```

**Ответ (200 OK):**
```json
{
  "id": 1,
  "username": "user123",
  "email": "user@example.com",
  "full_name": "Иван Иванов",
  "phone": "+79001234567",
  "role": "user",
  "date_joined": "2025-12-11T10:00:00Z"
}
```

#### Обновление профиля

```http
PATCH /api/users/profile/
Authorization: Bearer {token}
Content-Type: application/json

{
  "full_name": "Иван Петрович Иванов",
  "phone": "+79009876543"
}
```

#### Смена пароля

```http
POST /api/users/change-password/
Authorization: Bearer {token}
Content-Type: application/json

{
  "old_password": "oldpass123",
  "new_password": "newpass456",
  "new_password2": "newpass456"
}
```

---

### 🏢 Площадки

#### Список площадок

```http
GET /api/venues/
```

**Параметры запроса:**
- `search` - поиск по названию или адресу
- `category` - ID категории
- `capacity_min` - минимальная вместимость
- `capacity_max` - максимальная вместимость
- `price_min` - минимальная цена за час
- `price_max` - максимальная цена за час
- `page` - номер страницы (пагинация)

**Пример:**
```http
GET /api/venues/?search=конференц&category=1&capacity_min=50&price_max=10000
```

**Ответ (200 OK):**
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/venues/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Большой конференц-зал",
      "capacity": 100,
      "price_per_hour": "5000.00",
      "address": "Москва, ул. Примерная, д. 1",
      "main_image": "http://localhost:8000/media/venue_images/hall1.jpg",
      "categories": [
        {"id": 1, "name": "Конференц-зал"}
      ],
      "average_rating": 4.5,
      "reviews_count": 10,
      "is_active": true
    }
  ]
}
```

#### Детали площадки

```http
GET /api/venues/{id}/
```

**Ответ (200 OK):**
```json
{
  "id": 1,
  "owner": 2,
  "owner_name": "Администратор",
  "title": "Большой конференц-зал",
  "description": "Просторный зал для конференций...",
  "capacity": 100,
  "price_per_hour": "5000.00",
  "address": "Москва, ул. Примерная, д. 1",
  "latitude": "55.751244",
  "longitude": "37.618423",
  "created_at": "2025-12-01T10:00:00Z",
  "is_active": true,
  "categories": [
    {"id": 1, "name": "Конференц-зал"}
  ],
  "images": [
    {
      "id": 1,
      "image": "http://localhost:8000/media/venue_images/hall1.jpg",
      "uploaded_at": "2025-12-01T10:00:00Z"
    }
  ],
  "average_rating": 4.5,
  "reviews_count": 10
}
```

#### Создание площадки (Админ)

```http
POST /api/venues/
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "title": "Новая площадка",
  "description": "Описание площадки",
  "capacity": 50,
  "price_per_hour": 3000,
  "address": "Москва, ул. Новая, д. 10",
  "latitude": 55.751244,
  "longitude": 37.618423,
  "is_active": true,
  "category_ids": [1, 2]
}
```

#### Обновление площадки (Админ)

```http
PATCH /api/venues/{id}/
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "title": "Обновленное название",
  "price_per_hour": 4000
}
```

#### Загрузка изображения (Админ)

```http
POST /api/venues/{venue_id}/images/
Authorization: Bearer {admin_token}
Content-Type: multipart/form-data

image: [файл изображения]
```

#### Список категорий

```http
GET /api/venues/categories/
```

**Ответ (200 OK):**
```json
[
  {"id": 1, "name": "Конференц-зал"},
  {"id": 2, "name": "Актовый зал"},
  {"id": 3, "name": "Фотостудия"}
]
```

---

### 📅 Бронирования

#### Список бронирований

```http
GET /api/bookings/
Authorization: Bearer {token}
```

**Ответ (200 OK):**
```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "user": 1,
      "user_name": "Иван Иванов",
      "venue": 1,
      "venue_details": {
        "id": 1,
        "title": "Большой конференц-зал",
        "address": "Москва, ул. Примерная, д. 1",
        "price_per_hour": "5000.00"
      },
      "date_start": "2025-12-15T10:00:00Z",
      "date_end": "2025-12-15T14:00:00Z",
      "status": "confirmed",
      "status_display": "Подтверждено",
      "total_price": "20000.00",
      "created_at": "2025-12-11T10:00:00Z",
      "can_be_cancelled": true
    }
  ]
}
```

#### Создание бронирования

```http
POST /api/bookings/
Authorization: Bearer {token}
Content-Type: application/json

{
  "venue": 1,
  "date_start": "2025-12-15T10:00:00Z",
  "date_end": "2025-12-15T14:00:00Z"
}
```

**Ответ (201 Created):**
```json
{
  "id": 1,
  "venue": 1,
  "date_start": "2025-12-15T10:00:00Z",
  "date_end": "2025-12-15T14:00:00Z",
  "status": "pending",
  "total_price": "20000.00"
}
```

#### Отмена бронирования

```http
POST /api/bookings/{id}/cancel/
Authorization: Bearer {token}
```

**Ответ (200 OK):**
```json
{
  "id": 1,
  "status": "cancelled",
  "message": "Бронирование отменено"
}
```

#### Подтверждение бронирования (Админ)

```http
POST /api/bookings/{id}/confirm/
Authorization: Bearer {admin_token}
```

---

### 💳 Платежи

#### Создание платежа

```http
POST /api/bookings/payments/
Authorization: Bearer {token}
Content-Type: application/json

{
  "booking": 1,
  "payment_method": "card"
}
```

**Доступные способы оплаты:**
- `card` - Банковская карта
- `cash` - Наличные
- `transfer` - Банковский перевод

**Ответ (201 Created):**
```json
{
  "id": 1,
  "booking": 1,
  "amount": "20000.00",
  "status": "pending",
  "payment_method": "card",
  "created_at": "2025-12-11T10:00:00Z"
}
```

#### Обработка платежа

```http
POST /api/bookings/payments/{id}/process/
Authorization: Bearer {token}
```

**Ответ (200 OK):**
```json
{
  "message": "Платеж успешно обработан",
  "payment": {
    "id": 1,
    "booking": 1,
    "amount": "20000.00",
    "status": "paid",
    "payment_method": "card",
    "created_at": "2025-12-11T10:00:00Z"
  }
}
```

---

### ⭐ Отзывы

#### Список отзывов

```http
GET /api/reviews/
```

**Параметры запроса:**
- `venue` - ID площадки
- `rating` - фильтр по рейтингу (1-5)

**Пример:**
```http
GET /api/reviews/?venue=1&rating=5
```

**Ответ (200 OK):**
```json
{
  "count": 15,
  "results": [
    {
      "id": 1,
      "user": 1,
      "user_name": "Иван Иванов",
      "user_username": "user123",
      "venue": 1,
      "venue_title": "Большой конференц-зал",
      "rating": 5,
      "comment": "Отличная площадка, всё понравилось!",
      "created_at": "2025-12-10T10:00:00Z",
      "is_approved": true
    }
  ]
}
```

#### Мои отзывы

```http
GET /api/reviews/my/
Authorization: Bearer {token}
```

#### Создание отзыва

```http
POST /api/reviews/create/
Authorization: Bearer {token}
Content-Type: application/json

{
  "venue": 1,
  "rating": 5,
  "comment": "Отличная площадка!"
}
```

**Ответ (201 Created):**
```json
{
  "message": "Отзыв успешно создан и отправлен на модерацию",
  "review": {
    "id": 1,
    "venue": 1,
    "rating": 5,
    "comment": "Отличная площадка!",
    "is_approved": false
  }
}
```

#### Одобрение отзыва (Админ)

```http
POST /api/reviews/{id}/approve/
Authorization: Bearer {admin_token}
```

#### Отклонение отзыва (Админ)

```http
POST /api/reviews/{id}/disapprove/
Authorization: Bearer {admin_token}
```

#### Отзывы на модерации (Админ)

```http
GET /api/reviews/pending/
Authorization: Bearer {admin_token}
```

---

## Коды ответов

- `200 OK` - успешный запрос
- `201 Created` - ресурс создан
- `204 No Content` - успешно, нет содержимого
- `400 Bad Request` - ошибка валидации
- `401 Unauthorized` - требуется аутентификация
- `403 Forbidden` - недостаточно прав
- `404 Not Found` - ресурс не найден
- `500 Internal Server Error` - ошибка сервера

## Формат ошибок

```json
{
  "field_name": ["Описание ошибки"],
  "another_field": ["Другая ошибка"]
}
```

или

```json
{
  "detail": "Описание общей ошибки"
}
```

## Пагинация

Все списковые эндпоинты возвращают пагинированный ответ:

```json
{
  "count": 100,
  "next": "http://localhost:8000/api/venues/?page=2",
  "previous": null,
  "results": [...]
}
```

Параметры:
- `page` - номер страницы
- `page_size` - количество элементов на странице (по умолчанию 12)

## Swagger UI

Интерактивная документация доступна по адресу:
```
http://localhost:8000/api/docs/
```

## ReDoc

Альтернативная документация:
```
http://localhost:8000/api/redoc/
```

