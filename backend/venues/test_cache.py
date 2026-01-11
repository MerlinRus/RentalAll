"""
Тесты для кэширования рейтингов
"""
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APIClient
from rest_framework import status
from datetime import timedelta
from django.utils import timezone
from decimal import Decimal

from venues.models import Category, Venue
from bookings.models import Booking
from reviews.models import Review
from venues.cache_utils import (
    get_venue_rating_from_cache,
    invalidate_venue_rating_cache,
    get_cache_key
)

User = get_user_model()


@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'test-cache',
        }
    },
    APPEND_SLASH=False,
    SECURE_SSL_REDIRECT=False,
    SECURE_PROXY_SSL_HEADER=None
)
class VenueRatingCacheTestCase(TestCase):
    """Тесты кэширования рейтингов площадок"""
    
    def setUp(self):
        self.client = APIClient()
        self.client.default_format = 'json'
        cache.clear()  # Очищаем кэш перед каждым тестом
        
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
        
        # Создаём площадку
        self.category = Category.objects.create(name='Коворкинг')
        self.venue = Venue.objects.create(
            title='Test Venue',
            description='Test',
            address='Test Address',
            latitude='55.751244',
            longitude='37.618423',
            capacity=10,
            price_per_hour=Decimal('1000.00'),
            owner=self.admin,
            is_active=True
        )
        
        # Создаём бронирование для отзыва
        self.booking = Booking.objects.create(
            venue=self.venue,
            user=self.user,
            date_start=timezone.now() - timedelta(days=2),
            date_end=timezone.now() - timedelta(days=2, hours=-2),
            total_price=Decimal('2000.00'),
            status='confirmed'
        )
    
    def test_cache_miss_calculates_rating(self):
        """Проверка что при cache MISS вычисляется рейтинг"""
        # Создаём одобренный отзыв
        Review.objects.create(
            venue=self.venue,
            user=self.user,
            booking=self.booking,
            rating=5,
            comment='Отлично!',
            is_approved=True
        )
        
        # Кэш пустой, должен вычислить
        rating_data = get_venue_rating_from_cache(self.venue.id)
        
        self.assertEqual(rating_data['average_rating'], 5.0)
        self.assertEqual(rating_data['reviews_count'], 1)
    
    def test_cache_hit_returns_cached_data(self):
        """Проверка что при cache HIT возвращаются кэшированные данные"""
        # Создаём отзыв
        Review.objects.create(
            venue=self.venue,
            user=self.user,
            booking=self.booking,
            rating=5,
            comment='Отлично!',
            is_approved=True
        )
        
        # Первый вызов - cache MISS
        rating_data_1 = get_venue_rating_from_cache(self.venue.id)
        
        # Добавляем ещё отзыв (но не инвалидируем кэш)
        Review.objects.create(
            venue=self.venue,
            user=self.admin,
            rating=3,
            comment='Нормально',
            is_approved=True
        )
        
        # Второй вызов - cache HIT, должен вернуть старые данные
        rating_data_2 = get_venue_rating_from_cache(self.venue.id)
        
        # Данные должны быть одинаковыми (из кэша)
        self.assertEqual(rating_data_1, rating_data_2)
        self.assertEqual(rating_data_2['reviews_count'], 1)  # Всё ещё 1, не 2
    
    def test_cache_invalidation_on_review_creation(self):
        """Проверка инвалидации кэша при создании отзыва"""
        # Создаём первый отзыв
        Review.objects.create(
            venue=self.venue,
            user=self.user,
            booking=self.booking,
            rating=5,
            comment='Отлично!',
            is_approved=True
        )
        
        # Кэшируем
        get_venue_rating_from_cache(self.venue.id)
        
        # Проверяем что кэш есть
        cache_key = get_cache_key(self.venue.id, 'rating_data')
        self.assertIsNotNone(cache.get(cache_key))
        
        # Создаём новый отзыв через API (должна сработать инвалидация)
        self.client.force_authenticate(user=self.admin)
        response = self.client.post('/api/reviews/create/', {
            'venue': self.venue.id,
            'rating': 3,
            'comment': 'Нормально'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Кэш должен быть инвалидирован
        self.assertIsNone(cache.get(cache_key))
    
    def test_cache_invalidation_on_review_approval(self):
        """Проверка инвалидации кэша при одобрении отзыва"""
        # Создаём неодобренный отзыв
        review = Review.objects.create(
            venue=self.venue,
            user=self.user,
            booking=self.booking,
            rating=5,
            comment='Отлично!',
            is_approved=False
        )
        
        # Кэшируем (рейтинг должен быть 0, так как отзыв не одобрен)
        rating_data = get_venue_rating_from_cache(self.venue.id)
        self.assertEqual(rating_data['reviews_count'], 0)
        
        # Одобряем отзыв через API
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(f'/api/reviews/{review.id}/approve/', format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Кэш должен быть инвалидирован
        cache_key = get_cache_key(self.venue.id, 'rating_data')
        self.assertIsNone(cache.get(cache_key))
        
        # При повторном запросе должны получить обновлённые данные
        new_rating_data = get_venue_rating_from_cache(self.venue.id)
        self.assertEqual(new_rating_data['reviews_count'], 1)
        self.assertEqual(new_rating_data['average_rating'], 5.0)
    
    def test_cache_invalidation_on_review_delete(self):
        """Проверка инвалидации кэша при удалении отзыва"""
        # Создаём отзыв
        review = Review.objects.create(
            venue=self.venue,
            user=self.user,
            booking=self.booking,
            rating=5,
            comment='Отлично!',
            is_approved=True
        )
        
        # Кэшируем
        get_venue_rating_from_cache(self.venue.id)
        cache_key = get_cache_key(self.venue.id, 'rating_data')
        self.assertIsNotNone(cache.get(cache_key))
        
        # Удаляем отзыв через API
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f'/api/reviews/{review.id}/', format='json')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Кэш должен быть инвалидирован
        self.assertIsNone(cache.get(cache_key))
    
    def test_manual_cache_invalidation(self):
        """Проверка ручной инвалидации кэша"""
        # Создаём отзыв
        Review.objects.create(
            venue=self.venue,
            user=self.user,
            booking=self.booking,
            rating=5,
            comment='Отлично!',
            is_approved=True
        )
        
        # Кэшируем
        get_venue_rating_from_cache(self.venue.id)
        cache_key = get_cache_key(self.venue.id, 'rating_data')
        self.assertIsNotNone(cache.get(cache_key))
        
        # Инвалидируем вручную
        invalidate_venue_rating_cache(self.venue.id)
        
        # Кэш должен быть пуст
        self.assertIsNone(cache.get(cache_key))
    
    def test_cache_for_venue_without_reviews(self):
        """Проверка кэширования для площадки без отзывов"""
        rating_data = get_venue_rating_from_cache(self.venue.id)
        
        self.assertEqual(rating_data['average_rating'], 0.0)
        self.assertEqual(rating_data['reviews_count'], 0)
        
        # Проверяем что результат был закэширован
        cache_key = get_cache_key(self.venue.id, 'rating_data')
        cached_data = cache.get(cache_key)
        self.assertIsNotNone(cached_data)
        self.assertEqual(cached_data, rating_data)
