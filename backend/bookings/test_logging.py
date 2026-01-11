"""
Тесты для системы логирования
"""
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, call
from datetime import datetime, timedelta
from django.utils import timezone
from decimal import Decimal

from venues.models import Category, Venue
from bookings.models import Booking, Payment
from reviews.models import Review

User = get_user_model()


@override_settings(APPEND_SLASH=False, SECURE_SSL_REDIRECT=False, SECURE_PROXY_SSL_HEADER=None)
class BookingLoggingTestCase(TestCase):
    """Тесты логирования для bookings"""
    
    def setUp(self):
        self.client = APIClient()
        self.client.default_format = 'json'
        
        # Создаём пользователей
        self.user = User.objects.create_user(
            email='user@test.com',
            password='testpass123',
            full_name='Test User'
        )
        self.admin = User.objects.create_user(
            email='admin@test.com',
            password='adminpass123',
            full_name='Admin User',
            role='admin'
        )
        
        # Создаём площадку
        self.category = Category.objects.create(name='Коворкинг', slug='coworking')
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
    
    @patch('bookings.views.logger')
    def test_booking_creation_logged(self, mock_logger):
        """Проверка логирования создания бронирования"""
        self.client.force_authenticate(user=self.user)
        
        start = timezone.now() + timedelta(hours=1)
        end = start + timedelta(hours=2)
        
        response = self.client.post('/api/bookings/', {
            'venue': self.venue.id,
            'date_start': start.isoformat(),
            'date_end': end.isoformat()
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Проверяем, что logger.info был вызван
        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args[0][0]
        
        self.assertIn('Booking created', call_args)
        self.assertIn('user@test.com', call_args)
        self.assertIn('Test Venue', call_args)
    
    @patch('bookings.views.logger')
    def test_booking_cancellation_logged(self, mock_logger):
        """Проверка логирования отмены бронирования"""
        # Создаём бронирование
        booking = Booking.objects.create(
            venue=self.venue,
            user=self.user,
            date_start=timezone.now() + timedelta(hours=1),
            date_end=timezone.now() + timedelta(hours=3),
            total_price=Decimal('2000.00'),
            status='pending'
        )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.post(f'/api/bookings/{booking.id}/cancel/', format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Проверяем логирование
        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args[0][0]
        
        self.assertIn('Booking cancelled', call_args)
        self.assertIn('user@test.com', call_args)
    
    @patch('bookings.views.logger')
    def test_booking_confirmation_logged(self, mock_logger):
        """Проверка логирования подтверждения бронирования админом"""
        booking = Booking.objects.create(
            venue=self.venue,
            user=self.user,
            date_start=timezone.now() + timedelta(hours=1),
            date_end=timezone.now() + timedelta(hours=3),
            total_price=Decimal('2000.00'),
            status='pending'
        )
        
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(f'/api/bookings/{booking.id}/confirm/', format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Проверяем логирование
        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args[0][0]
        
        self.assertIn('Booking confirmed', call_args)
        self.assertIn('admin@test.com', call_args)
        self.assertIn('user@test.com', call_args)
    
    @patch('bookings.views.logger')
    def test_payment_processing_logged(self, mock_logger):
        """Проверка логирования обработки платежа"""
        booking = Booking.objects.create(
            venue=self.venue,
            user=self.user,
            date_start=timezone.now() + timedelta(hours=1),
            date_end=timezone.now() + timedelta(hours=3),
            total_price=Decimal('2000.00'),
            status='pending'
        )
        
        payment = Payment.objects.create(
            booking=booking,
            amount=Decimal('2000.00'),
            status='pending'
        )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.post(f'/api/bookings/payments/{payment.id}/process/', format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Проверяем логирование
        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args[0][0]
        
        self.assertIn('Payment processed', call_args)
        self.assertIn('user@test.com', call_args)
        self.assertIn('2000', call_args)


@override_settings(APPEND_SLASH=False, SECURE_SSL_REDIRECT=False, SECURE_PROXY_SSL_HEADER=None)
class VenueLoggingTestCase(TestCase):
    """Тесты логирования для venues"""
    
    def setUp(self):
        self.client = APIClient()
        self.client.default_format = 'json'
        
        self.admin = User.objects.create_user(
            email='admin@test.com',
            password='adminpass123',
            full_name='Admin User',
            role='admin'
        )
        
        self.category = Category.objects.create(name='Коворкинг', slug='coworking')
    
    @patch('venues.views.logger')
    def test_venue_creation_logged(self, mock_logger):
        """Проверка логирования создания площадки"""
        self.client.force_authenticate(user=self.admin)
        
        response = self.client.post('/api/venues/', {
            'title': 'New Venue',
            'description': 'Test description',
            'address': 'Test Address',
            'latitude': '55.751244',
            'longitude': '37.618423',
            'capacity': 20,
            'price_per_hour': '1500.00',
            'categories': [self.category.id],
            'is_active': True
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Проверяем логирование
        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args[0][0]
        
        self.assertIn('Venue created', call_args)
        self.assertIn('New Venue', call_args)
        self.assertIn('admin@test.com', call_args)
        self.assertIn('1500', call_args)
    
    @patch('venues.views.logger')
    def test_venue_update_logged(self, mock_logger):
        """Проверка логирования обновления площадки"""
        venue = Venue.objects.create(
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
        
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(f'/api/venues/{venue.id}/', {
            'title': 'Updated Venue'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Проверяем логирование
        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args[0][0]
        
        self.assertIn('Venue updated', call_args)
        self.assertIn('admin@test.com', call_args)
    
    @patch('venues.views.logger')
    def test_venue_deletion_logged(self, mock_logger):
        """Проверка логирования удаления площадки"""
        venue = Venue.objects.create(
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
        
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f'/api/venues/{venue.id}/', format='json')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Проверяем логирование
        mock_logger.warning.assert_called_once()
        call_args = mock_logger.warning.call_args[0][0]
        
        self.assertIn('Venue deleted', call_args)
        self.assertIn('admin@test.com', call_args)


@override_settings(APPEND_SLASH=False, SECURE_SSL_REDIRECT=False, SECURE_PROXY_SSL_HEADER=None)
class ReviewLoggingTestCase(TestCase):
    """Тесты логирования для reviews"""
    
    def setUp(self):
        self.client = APIClient()
        self.client.default_format = 'json'
        
        self.user = User.objects.create_user(
            email='user@test.com',
            password='testpass123',
            full_name='Test User'
        )
        self.admin = User.objects.create_user(
            email='admin@test.com',
            password='adminpass123',
            full_name='Admin User',
            role='admin'
        )
        
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
        
        self.booking = Booking.objects.create(
            venue=self.venue,
            user=self.user,
            date_start=timezone.now() - timedelta(days=1),
            date_end=timezone.now() - timedelta(hours=22),
            total_price=Decimal('2000.00'),
            status='completed'
        )
    
    @patch('reviews.views.logger')
    def test_review_creation_logged(self, mock_logger):
        """Проверка логирования создания отзыва"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.post('/api/reviews/create/', {
            'venue': self.venue.id,
            'booking': self.booking.id,
            'rating': 5,
            'comment': 'Great place!'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Проверяем логирование
        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args[0][0]
        
        self.assertIn('Review created', call_args)
        self.assertIn('user@test.com', call_args)
        self.assertIn('Test Venue', call_args)
        self.assertIn('Rating=5', call_args)
    
    @patch('reviews.views.logger')
    def test_review_approval_logged(self, mock_logger):
        """Проверка логирования одобрения отзыва"""
        review = Review.objects.create(
            venue=self.venue,
            user=self.user,
            booking=self.booking,
            rating=5,
            comment='Great!',
            is_approved=False
        )
        
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(f'/api/reviews/{review.id}/approve/', format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Проверяем логирование
        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args[0][0]
        
        self.assertIn('Review approved', call_args)
        self.assertIn('admin@test.com', call_args)
        self.assertIn('user@test.com', call_args)


@override_settings(APPEND_SLASH=False, SECURE_SSL_REDIRECT=False, SECURE_PROXY_SSL_HEADER=None)
class UserLoggingTestCase(TestCase):
    """Тесты логирования для users"""
    
    def setUp(self):
        self.client = APIClient()
        self.client.default_format = 'json'
    
    @patch('users.views.logger')
    def test_user_registration_logged(self, mock_logger):
        """Проверка логирования регистрации пользователя"""
        response = self.client.post('/api/users/register/', {
            'email': 'newuser@test.com',
            'password': 'newpass123',
            'password2': 'newpass123',
            'full_name': 'New User',
            'phone': '+79991234567'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Проверяем логирование
        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args[0][0]
        
        self.assertIn('User registered', call_args)
        self.assertIn('newuser@test.com', call_args)
        self.assertIn('New User', call_args)
    
    @patch('users.views.security_logger')
    def test_password_change_logged(self, mock_security_logger):
        """Проверка логирования смены пароля"""
        user = User.objects.create_user(
            email='user@test.com',
            password='oldpass123',
            full_name='Test User'
        )
        
        self.client.force_authenticate(user=user)
        response = self.client.post('/api/users/change-password/', {
            'old_password': 'oldpass123',
            'new_password': 'newpass123',
            'new_password2': 'newpass123'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Проверяем логирование
        mock_security_logger.info.assert_called_once()
        call_args = mock_security_logger.info.call_args[0][0]
        
        self.assertIn('Password changed', call_args)
        self.assertIn('user@test.com', call_args)
    
    @patch('users.views.security_logger')
    def test_failed_password_change_logged(self, mock_security_logger):
        """Проверка логирования неудачной смены пароля"""
        user = User.objects.create_user(
            email='user@test.com',
            password='oldpass123',
            full_name='Test User'
        )
        
        self.client.force_authenticate(user=user)
        response = self.client.post('/api/users/change-password/', {
            'old_password': 'wrongpass',
            'new_password': 'newpass123',
            'new_password2': 'newpass123'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Проверяем логирование
        mock_security_logger.warning.assert_called_once()
        call_args = mock_security_logger.warning.call_args[0][0]
        
        self.assertIn('Failed password change attempt', call_args)
        self.assertIn('user@test.com', call_args)
        self.assertIn('Wrong old password', call_args)


@override_settings(APPEND_SLASH=False, SECURE_SSL_REDIRECT=False, SECURE_PROXY_SSL_HEADER=None)
class SecurityLoggingTestCase(TestCase):
    """Тесты логирования security событий"""
    
    def setUp(self):
        self.client = APIClient()
        self.client.default_format = 'json'
        
        self.user = User.objects.create_user(
            email='user@test.com',
            password='testpass123',
            full_name='Test User'
        )
    
    @patch('rentalall.middleware.security_logger')
    def test_unauthorized_access_logged(self, mock_security_logger):
        """Проверка логирования неавторизованного доступа (401)"""
        # Попытка доступа без аутентификации
        response = self.client.get('/api/bookings/', format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Проверяем логирование
        mock_security_logger.warning.assert_called()
        call_args = mock_security_logger.warning.call_args[0][0]
        
        self.assertIn('Unauthorized access attempt', call_args)
        self.assertIn('/api/bookings/', call_args)
    
    @patch('rentalall.middleware.security_logger')
    def test_forbidden_access_logged(self, mock_security_logger):
        """Проверка логирования запрещённого доступа (403)"""
        self.client.force_authenticate(user=self.user)
        
        # Попытка создать площадку обычным пользователем (только админ)
        response = self.client.post('/api/venues/', {
            'title': 'New Venue',
            'description': 'Test',
            'address': 'Test',
            'latitude': '55.751244',
            'longitude': '37.618423',
            'capacity': 10,
            'price_per_hour': '1000.00'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Проверяем логирование
        mock_security_logger.warning.assert_called()
        call_args = mock_security_logger.warning.call_args[0][0]
        
        self.assertIn('Forbidden access attempt', call_args)
        self.assertIn('/api/venues/', call_args)
        self.assertIn('user@test.com', call_args)
