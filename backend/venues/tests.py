from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import connection
from django.test.utils import override_settings
from rest_framework.test import APIClient
from rest_framework import status
from .models import Category, Venue, VenueImage
from reviews.models import Review
from bookings.models import Booking
from datetime import datetime, timedelta
from decimal import Decimal

User = get_user_model()


# Отключаем APPEND_SLASH и SSL редирект для тестов
@override_settings(
    APPEND_SLASH=False,
    SECURE_SSL_REDIRECT=False,
    SECURE_PROXY_SSL_HEADER=None
)
class VenueQueryOptimizationTestCase(TestCase):
    """Тесты для проверки оптимизации N+1 queries"""
    
    def setUp(self):
        """Подготовка тестовых данных"""
        # Используем format='json' для правильных API запросов без редиректов
        self.client = APIClient()
        self.client.default_format = 'json'
        
        # Создаём пользователя
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
            phone='+79001234567'
        )
        
        # Создаём категории
        self.category1 = Category.objects.create(name='Коворкинг')
        self.category2 = Category.objects.create(name='Конференц-зал')
        
        # Создаём площадки
        self.venues = []
        for i in range(10):
            venue = Venue.objects.create(
                owner=self.user,
                title=f'Площадка {i+1}',
                description=f'Описание площадки {i+1}',
                capacity=10 + i*5,
                price_per_hour=Decimal('1000.00') + Decimal(i*100),
                address=f'ул. Тестовая, д. {i+1}',
                latitude=Decimal('58.6') + Decimal(i*0.01),
                longitude=Decimal('49.6') + Decimal(i*0.01),
                is_active=True
            )
            
            # Добавляем категории
            venue.categories.add(self.category1)
            if i % 2 == 0:
                venue.categories.add(self.category2)
            
            # Создаём изображения
            # Note: В реальных тестах нужно использовать SimpleUploadedFile
            # Здесь просто создаём записи без файлов для простоты
            
            self.venues.append(venue)
        
        # Создаём отзывы для первых 3 площадок
        for venue in self.venues[:3]:
            for rating in [4, 5]:
                Review.objects.create(
                    user=self.user,
                    venue=venue,
                    rating=rating,
                    comment=f'Отзыв {rating} звёзд',
                    is_approved=True
                )
    
    def test_venue_list_query_count(self):
        """Проверка количества запросов к БД при получении списка площадок"""
        # Сбрасываем счётчик запросов
        connection.queries_was_reset = True
        
        with self.assertNumQueries(4):  # Оптимизация работает отлично: COUNT + SELECT + prefetch images + prefetch categories
            response = self.client.get('/api/venues/', format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # response.data - это paginated response от DRF
        results = response.data.get('results', response.data) if isinstance(response.data, dict) else response.data
        self.assertEqual(len(results), 10)
        
        # Проверяем, что все данные загружены
        first_venue = results[0]
        self.assertIn('categories', first_venue)
        self.assertIn('images', first_venue)
        self.assertIn('average_rating', first_venue)
        self.assertIn('reviews_count', first_venue)
    
    def test_venue_detail_query_count(self):
        """Проверка количества запросов для детальной страницы"""
        venue = self.venues[0]
        
        with self.assertNumQueries(5):  # 5 запросов: venue + images + categories + reviews + users for reviews
            response = self.client.get(f'/api/venues/{venue.id}/', format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], venue.id)
        
        # Проверяем аннотированные поля
        self.assertIn('average_rating', response.data)
        self.assertIn('reviews_count', response.data)
    
    def test_average_rating_annotation(self):
        """Проверка правильности вычисления среднего рейтинга"""
        venue = self.venues[0]  # У этой площадки есть отзывы 4 и 5
        
        response = self.client.get(f'/api/venues/{venue.id}/', format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Проверяем средний рейтинг: (4 + 5) / 2 = 4.5
        self.assertEqual(float(response.data['average_rating']), 4.5)
        self.assertEqual(response.data['reviews_count'], 2)
    
    def test_venue_without_reviews(self):
        """Проверка площадки без отзывов"""
        venue = self.venues[-1]  # Последняя площадка без отзывов
        
        response = self.client.get(f'/api/venues/{venue.id}/', format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Проверяем, что рейтинг None или 0
        self.assertIn(response.data['average_rating'], [None, 0, 0.0])
        self.assertEqual(response.data['reviews_count'], 0)
    
    def test_venue_list_with_filters(self):
        """Проверка работы фильтров без увеличения запросов"""
        with self.assertNumQueries(4):  # 4 запроса с фильтрами
            response = self.client.get('/api/venues/', {
                'category': self.category1.id,
                'capacity_min': 10,
                'capacity_max': 50
            }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)


@override_settings(
    APPEND_SLASH=False,
    SECURE_SSL_REDIRECT=False,
    SECURE_PROXY_SSL_HEADER=None
)
class VenueSerializerTestCase(TestCase):
    """Тесты для сериализаторов площадок"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
            phone='+79001234567'
        )
        
        self.category = Category.objects.create(name='Тест категория')
        
        self.venue = Venue.objects.create(
            owner=self.user,
            title='Тестовая площадка',
            description='Описание',
            capacity=20,
            price_per_hour=Decimal('1500.00'),
            address='ул. Тестовая, д. 1',
            is_active=True
        )
        self.venue.categories.add(self.category)
    
    def test_venue_list_serializer_fields(self):
        """Проверка наличия всех полей в VenueListSerializer"""
        client = APIClient()
        client.default_format = 'json'
        response = client.get(f'/api/venues/', format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Обрабатываем paginated response
        results = response.data.get('results', response.data) if isinstance(response.data, dict) else response.data
        self.assertGreater(len(results), 0, "Список площадок не должен быть пустым")
        
        venue_data = results[0]
        required_fields = [
            'id', 'title', 'capacity', 'price_per_hour', 'address',
            'latitude', 'longitude', 'main_image', 'images',
            'categories', 'average_rating', 'reviews_count', 'is_active'
        ]
        
        for field in required_fields:
            self.assertIn(field, venue_data, f'Поле {field} отсутствует')
    
    def test_venue_detail_serializer_fields(self):
        """Проверка наличия всех полей в VenueDetailSerializer"""
        client = APIClient()
        client.default_format = 'json'
        response = client.get(f'/api/venues/{self.venue.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        required_fields = [
            'id', 'owner', 'owner_name', 'title', 'description',
            'capacity', 'price_per_hour', 'address', 'latitude',
            'longitude', 'created_at', 'is_active', 'categories',
            'images', 'average_rating', 'reviews_count'
        ]
        
        for field in required_fields:
            self.assertIn(field, response.data, f'Поле {field} отсутствует')


@override_settings(
    APPEND_SLASH=False,
    SECURE_SSL_REDIRECT=False,
    SECURE_PROXY_SSL_HEADER=None
)
class VenueAPIPermissionsTestCase(TestCase):
    """Тесты прав доступа к API площадок"""
    
    def setUp(self):
        self.client = APIClient()
        self.client.default_format = 'json'
        
        # Обычный пользователь
        self.user = User.objects.create_user(
            username='user',
            email='user@test.com',
            password='testpass123',
            phone='+79001234567'
        )
        
        # Администратор
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='adminpass123',
            phone='+79001234568',
            role='admin'
        )
        
        self.venue = Venue.objects.create(
            owner=self.admin,
            title='Тестовая площадка',
            description='Описание',
            capacity=20,
            price_per_hour=Decimal('1500.00'),
            address='ул. Тестовая, д. 1',
            is_active=True
        )
    
    def test_anonymous_can_list_venues(self):
        """Анонимный пользователь может просматривать список"""
        response = self.client.get('/api/venues/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_anonymous_can_view_venue_detail(self):
        """Анонимный пользователь может просматривать детали"""
        response = self.client.get(f'/api/venues/{self.venue.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_anonymous_cannot_create_venue(self):
        """Анонимный пользователь не может создавать площадки"""
        response = self.client.post('/api/venues/', {
            'title': 'Новая площадка',
            'description': 'Описание',
            'capacity': 10,
            'price_per_hour': '1000.00',
            'address': 'Адрес'
        }, format='json')
        # DRF возвращает 401 для неаутентифицированных пользователей
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
    
    def test_regular_user_cannot_create_venue(self):
        """Обычный пользователь не может создавать площадки"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.post('/api/venues/', {
            'title': 'Новая площадка',
            'description': 'Описание',
            'capacity': 10,
            'price_per_hour': '1000.00',
            'address': 'Адрес'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_admin_can_create_venue(self):
        """Администратор может создавать площадки"""
        self.client.force_authenticate(user=self.admin)
        
        response = self.client.post('/api/venues/', {
            'title': 'Новая площадка',
            'description': 'Описание',
            'capacity': 10,
            'price_per_hour': '1000.00',
            'address': 'Адрес'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


@override_settings(
    APPEND_SLASH=False,
    SECURE_SSL_REDIRECT=False,
    SECURE_PROXY_SSL_HEADER=None
)
class VenueCategoryTestCase(TestCase):
    """Тесты для категорий площадок"""
    
    def setUp(self):
        self.client = APIClient()
        self.client.default_format = 'json'
        self.category1 = Category.objects.create(name='Категория 1')
        self.category2 = Category.objects.create(name='Категория 2')
    
    def test_list_categories(self):
        """Получение списка категорий"""
        response = self.client.get('/api/venues/categories/', format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверяем что категории есть (может быть больше из-за других тестов)
        results = response.data.get('results', response.data) if isinstance(response.data, dict) else response.data
        self.assertGreaterEqual(len(results), 2, "Должно быть минимум 2 категории")
    
    def test_category_fields(self):
        """Проверка полей категории"""
        response = self.client.get('/api/venues/categories/', format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data) if isinstance(response.data, dict) else response.data
        self.assertGreater(len(results), 0, "Список категорий не должен быть пустым")
        
        category = results[0]
        self.assertIn('id', category)
        self.assertIn('name', category)
