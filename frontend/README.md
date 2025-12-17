# RentalAll Frontend

## React приложение для системы бронирования площадок

### Технологии
- React 18
- React Router DOM v6
- Axios
- Material-UI
- React DatePicker
- React Toastify

### Установка

1. Установите зависимости:
```bash
npm install
```

2. Создайте файл `.env` в корне frontend:
```env
REACT_APP_API_URL=http://localhost:8000/api
```

3. Запустите сервер разработки:
```bash
npm start
```

Приложение откроется по адресу: http://localhost:3000

### Структура проекта

```
src/
├── components/          # Переиспользуемые компоненты
│   ├── Layout/         # Navbar, Footer
│   └── Auth/           # PrivateRoute, AdminRoute
├── pages/              # Страницы приложения
│   ├── HomePage.js
│   ├── VenueListPage.js
│   ├── VenueDetailPage.js
│   ├── LoginPage.js
│   ├── RegisterPage.js
│   ├── ProfilePage.js
│   ├── BookingsPage.js
│   ├── AdminDashboard.js
│   └── NotFoundPage.js
├── services/           # API сервисы
│   └── api.js
├── context/            # React Context
│   └── AuthContext.js
├── App.js              # Главный компонент
└── index.js            # Точка входа
```

### Маршруты

#### Публичные
- `/` - Главная страница
- `/venues` - Каталог площадок
- `/venues/:id` - Детали площадки
- `/login` - Вход
- `/register` - Регистрация

#### Защищённые (требуют авторизации)
- `/profile` - Профиль пользователя
- `/bookings` - Мои бронирования

#### Админские (требуют роль admin)
- `/admin` - Обзор
- `/admin/venues` - Управление площадками
- `/admin/bookings` - Управление бронированиями
- `/admin/reviews` - Модерация отзывов
- `/admin/users` - Управление пользователями

### API Integration

Все API запросы централизованы в `src/services/api.js`:

```javascript
import { venuesAPI, bookingsAPI, authAPI, reviewsAPI } from './services/api';

// Пример использования
const loadVenues = async () => {
  const response = await venuesAPI.getAll({ category: 1 });
  setVenues(response.data);
};
```

### Аутентификация

Аутентификация реализована через JWT токены и React Context:

```javascript
import { useAuth } from './context/AuthContext';

const { user, login, logout, isAdmin } = useAuth();

// Вход
await login(username, password);

// Проверка роли
if (isAdmin()) {
  // Админские действия
}
```

### Команды

```bash
# Запуск в режиме разработки
npm start

# Создание production сборки
npm run build

# Запуск тестов
npm test

# Проверка линтером
npm run lint
```

### Компоненты и стили

Стили организованы в отдельных CSS файлах для каждого компонента:
- Глобальные стили: `index.css`, `App.css`
- Компонентные стили: рядом с компонентами

### Основные фичи

#### Для всех пользователей
- Просмотр каталога площадок
- Фильтрация по параметрам
- Просмотр деталей площадки
- Просмотр отзывов

#### Для авторизованных пользователей
- Бронирование площадок
- Оплата бронирований
- Отмена бронирований
- Оставление отзывов
- Управление профилем

#### Для администраторов
- Управление площадками
- Подтверждение бронирований
- Модерация отзывов
- Просмотр статистики

### Адаптивность

Приложение полностью адаптивно и корректно отображается на:
- Desktop (1200px+)
- Tablet (768px - 1199px)
- Mobile (< 768px)

### Production Build

Для создания production сборки:

```bash
npm run build
```

Сборка будет создана в папке `build/` и готова к развертыванию на веб-сервере.

