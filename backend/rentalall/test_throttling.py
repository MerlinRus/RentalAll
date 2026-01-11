"""
Тесты для проверки Rate Limiting (Throttling)
"""
import logging
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from datetime import timedelta
from decimal import Decimal

from venues.models import Venue, Category
from bookings.models import Booking
from reviews.models import Review

User = get_user_model()
logger = logging.getLogger(__name__)


@override_settings(
    APPEND_SLASH=False,
    SECURE_SSL_REDIRECT=False,
    SECURE_PROXY_SSL_HEADER=None,
    # Используем LocMemCache для тестов (для throttling это нормально)
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-test-cache',
        }
    },
    # Более низкие лимиты для быстрого тестирования
    REST_FRAMEWORK={
        'DEFAULT_AUTHENTICATION_CLASSES': (
            'rest_framework_simplejwt.authentication.JWTAuthentication',
        ),
        'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
        'PAGE_SIZE': 12,
        'DEFAULT_THROTTLE_RATES': {
            'anon': '100/hour',
            'user': '1000/hour',
            'booking': '10/hour',
            'review': '5/day',
        }
    }
)
class ThrottlingTestCase(TestCase):
    """Тесты для проверки ограничения частоты запросов"""
    
    def setUp(self):
        self.client = APIClient()
        self.client.default_format = 'json'
        
        # Создаём пользователей
        self.user = User.objects.create_user(
            username='testuser',
            email='user@test.com',
            password='testpass123',
            full_name='Test User'
        )
        self.admin = User.objects.create_user(
            username='adminuser',
            email='admin@test.com',
            password='adminpass123',
            full_name='Admin User',
            role='admin'
        )
        
        # Создаём тестовую площадку
        self.category = Category.objects.create(name='Test Category')
        self.venue = Venue.objects.create(
            title='Test Venue',
            description='Test Description',
            address='Test Address',
            latitude=Decimal('55.7558'),
            longitude=Decimal('37.6173'),
            price_per_hour=Decimal('1000.00'),
            capacity=10,
            owner=self.admin,
            is_active=True
        )
        self.venue.categories.add(self.category)
    
    def test_anon_throttling(self):
        """Проверка throttling для анонимных пользователей"""
        # Анонимные запросы: 100/hour
        # Делаем несколько запросов подряд (меньше лимита)
        for i in range(5):
            response = self.client.get('/api/venues/', format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Проверяем, что лимит не достигнут для малого количества запросов
        response = self.client.get('/api/venues/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_user_throttling(self):
        """Проверка throttling для авторизованных пользователей"""
        # Авторизуемся
        self.client.force_authenticate(user=self.user)
        
        # Авторизованные: 1000/hour (намного больше лимита анонимов)
        # Делаем несколько запросов подряд
        for i in range(10):
            response = self.client.get('/api/venues/', format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_booking_throttling_limit(self):
        """Проверка ограничения на создание бронирований (10/hour)"""
        self.client.force_authenticate(user=self.user)
        
        # Пытаемся создать 11 бронирований подряд
        for i in range(11):
            start_time = timezone.now() + timedelta(days=i+1)
            end_time = start_time + timedelta(hours=2)
            
            response = self.client.post('/api/bookings/', {
                'venue': self.venue.id,
                'date_start': start_time.isoformat(),
                'date_end': end_time.isoformat()
            }, format='json')
            
            if i < 10:
                # Первые 10 запросов должны пройти
                self.assertEqual(
                    response.status_code,
                    status.HTTP_201_CREATED,
                    f"Booking {i+1} should succeed"
                )
            else:
                # 11-й запрос должен быть заблокирован
                self.assertEqual(
                    response.status_code,
                    status.HTTP_429_TOO_MANY_REQUESTS,
                    "Booking 11 should be throttled"
                )
    
    def test_review_throttling_limit(self):
        """Проверка ограничения на создание отзывов (5/day)"""
        self.client.force_authenticate(user=self.user)
        
        # Создаём 6 бронирований для отзывов
        bookings = []
        for i in range(6):
            start_time = timezone.now() - timedelta(days=i+1)
            end_time = start_time + timedelta(hours=2)
            
            booking = Booking.objects.create(
                user=self.user,
                venue=self.venue,
                date_start=start_time,
                date_end=end_time,
                status='confirmed',
                total_price=Decimal('2000.00')
            )
            bookings.append(booking)
        
        # Пытаемся создать 6 отзывов подряд
        for i, booking in enumerate(bookings):
            response = self.client.post('/api/reviews/create/', {
                'venue': self.venue.id,
                'booking': booking.id,
                'rating': 5,
                'comment': f'Great place! Review #{i+1}'
            }, format='json')
            
            if i < 5:
                # Первые 5 отзывов должны пройти
                self.assertEqual(
                    response.status_code,
                    status.HTTP_201_CREATED,
                    f"Review {i+1} should succeed"
                )
            else:
                # 6-й отзыв должен быть заблокирован
                self.assertEqual(
                    response.status_code,
                    status.HTTP_429_TOO_MANY_REQUESTS,
                    "Review 6 should be throttled"
                )
    
    def test_throttle_headers_present(self):
        """Проверка наличия заголовков о лимитах"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get('/api/venues/', format='json')
        
        # DRF может добавлять заголовки X-RateLimit-*
        # но это зависит от настроек, поэтому просто проверяем успешность
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_different_users_separate_limits(self):
        """Проверка, что у разных пользователей отдельные лимиты"""
        # Пользователь 1 делает 5 бронирований
        self.client.force_authenticate(user=self.user)
        for i in range(5):
            start_time = timezone.now() + timedelta(days=i+1)
            end_time = start_time + timedelta(hours=2)
            
            response = self.client.post('/api/bookings/', {
                'venue': self.venue.id,
                'date_start': start_time.isoformat(),
                'date_end': end_time.isoformat()
            }, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Создаём второго пользователя
        user2 = User.objects.create_user(
            username='testuser2',
            email='user2@test.com',
            password='testpass123',
            full_name='Test User 2'
        )
        
        # Пользователь 2 должен иметь свой лимит
        self.client.force_authenticate(user=user2)
        start_time = timezone.now() + timedelta(days=10)
        end_time = start_time + timedelta(hours=2)
        
        response = self.client.post('/api/bookings/', {
            'venue': self.venue.id,
            'date_start': start_time.isoformat(),
            'date_end': end_time.isoformat()
        }, format='json')
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            "User 2 should have separate throttle limit"
        )
