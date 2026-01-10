# 🧪 Тестирование модуля Venues

## Запуск всех тестов

```bash
# Все тесты модуля venues
python manage.py test venues

# Конкретный тест-кейс
python manage.py test venues.tests.VenueQueryOptimizationTestCase

# Конкретный тест
python manage.py test venues.tests.VenueQueryOptimizationTestCase.test_venue_list_query_count

# С подробным выводом
python manage.py test venues -v 2
```

## Созданные тест-кейсы

### 1. **VenueQueryOptimizationTestCase** - Оптимизация N+1 queries
- ✅ `test_venue_list_query_count` - проверка количества запросов к БД (должно быть ≤ 5)
- ✅ `test_venue_detail_query_count` - проверка детальной страницы (должно быть ≤ 4)
- ✅ `test_average_rating_annotation` - правильность вычисления среднего рейтинга
- ✅ `test_venue_without_reviews` - площадки без отзывов
- ✅ `test_venue_list_with_filters` - фильтры не увеличивают запросы

### 2. **VenueSerializerTestCase** - Тесты сериализаторов
- ✅ `test_venue_list_serializer_fields` - проверка всех полей в списке
- ✅ `test_venue_detail_serializer_fields` - проверка всех полей в детальной странице

### 3. **VenueAPIPermissionsTestCase** - Права доступа
- ✅ `test_anonymous_can_list_venues` - анонимный может просматривать
- ✅ `test_anonymous_can_view_venue_detail` - анонимный может смотреть детали
- ✅ `test_anonymous_cannot_create_venue` - анонимный не может создавать
- ✅ `test_regular_user_cannot_create_venue` - обычный пользователь не может создавать
- ✅ `test_admin_can_create_venue` - админ может создавать

### 4. **VenueCategoryTestCase** - Категории
- ✅ `test_list_categories` - получение списка категорий
- ✅ `test_category_fields` - проверка полей категории

## Coverage (покрытие)

```bash
# Установить coverage
pip install coverage

# Запустить тесты с coverage
coverage run --source='.' manage.py test venues

# Посмотреть отчёт
coverage report

# HTML отчёт
coverage html
open htmlcov/index.html
```

## Что тестируется

### ✅ Оптимизация производительности
- Количество SQL запросов
- Использование `prefetch_related` и `select_related`
- Аннотации на уровне БД

### ✅ Бизнес-логика
- Вычисление среднего рейтинга
- Подсчёт отзывов
- Фильтрация площадок

### ✅ API endpoints
- GET /api/venues/
- GET /api/venues/{id}/
- POST /api/venues/
- GET /api/venues/categories/

### ✅ Права доступа
- Анонимные пользователи
- Авторизованные пользователи
- Администраторы

## Тестовые данные

Каждый тест создаёт:
- 10 площадок
- 2 категории
- 1 тестовый пользователь
- Отзывы для первых 3 площадок

## Как добавить новый тест

```python
def test_my_new_feature(self):
    """Описание теста"""
    # Arrange (подготовка)
    venue = self.venues[0]
    
    # Act (действие)
    response = self.client.get(f'/api/venues/{venue.id}/')
    
    # Assert (проверка)
    self.assertEqual(response.status_code, 200)
    self.assertIn('title', response.data)
```

## CI/CD Integration

Добавить в `.github/workflows/django-tests.yml`:

```yaml
- name: Run Venue Tests
  run: |
    cd backend
    python manage.py test venues -v 2
```
