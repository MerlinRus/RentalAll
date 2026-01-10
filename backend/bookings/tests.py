from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient
from rest_framework import status
from datetime import timedelta
from decimal import Decimal
from .models import Booking, Payment
from venues.models import Venue, Category

User = get_user_model()


class BookingValidationTestCase(TestCase):
    """Тесты валидации бронирований"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
            phone='+79001234567'
        )
        
        self.venue = Venue.objects.create(
            owner=self.user,
            title='Тестовая площадка',
            description='Описание',
            capacity=50,
            price_per_hour=Decimal('1000.00'),
            address='ул. Тестовая, д. 1',
            is_active=True
        )
    
    def test_booking_minimum_duration(self):
        """Проверка минимальной длительности бронирования"""
        now = timezone.now()
        start = now + timedelta(hours=1)
        end = start + timedelta(minutes=30)  # 30 минут - меньше минимума
        
        booking = Booking(
            user=self.user,
            venue=self.venue,
            date_start=start,
            date_end=end
        )
        
        with self.assertRaises(ValidationError) as context:
            booking.save()
        
        self.assertIn('date_end', context.exception.message_dict)
    
    def test_booking_maximum_duration(self):
        """Проверка максимальной длительности бронирования"""
        now = timezone.now()
        start = now + timedelta(hours=1)
        end = start + timedelta(hours=25)  # 25 часов - больше максимума
        
        booking = Booking(
            user=self.user,
            venue=self.venue,
            date_start=start,
            date_end=end
        )
        
        with self.assertRaises(ValidationError) as context:
            booking.save()
        
        self.assertIn('date_end', context.exception.message_dict)
    
    def test_booking_valid_duration(self):
        """Проверка корректной длительности бронирования"""
        now = timezone.now()
        start = now + timedelta(hours=1)
        end = start + timedelta(hours=2)  # 2 часа - корректно
        
        booking = Booking(
            user=self.user,
            venue=self.venue,
            date_start=start,
            date_end=end,
            total_price=Decimal('2000.00')
        )
        
        # Не должно быть исключений
        booking.save()
        self.assertIsNotNone(booking.id)
    
    def test_booking_end_before_start(self):
        """Проверка, что дата окончания не может быть раньше начала"""
        now = timezone.now()
        start = now + timedelta(hours=2)
        end = now + timedelta(hours=1)  # Конец раньше начала
        
        booking = Booking(
            user=self.user,
            venue=self.venue,
            date_start=start,
            date_end=end
        )
        
        with self.assertRaises(ValidationError) as context:
            booking.save()
        
        self.assertIn('date_end', context.exception.message_dict)


class BookingAPITestCase(TestCase):
    """Тесты API бронирований"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
            phone='+79001234567'
        )
        
        self.venue = Venue.objects.create(
            owner=self.user,
            title='Тестовая площадка',
            description='Описание',
            capacity=50,
            price_per_hour=Decimal('1000.00'),
            address='ул. Тестовая, д. 1',
            is_active=True
        )
        
        self.client.force_authenticate(user=self.user)
    
    def test_create_booking_minimum_duration_api(self):
        """API: Проверка минимальной длительности через API"""
        now = timezone.now()
        start = now + timedelta(hours=1)
        end = start + timedelta(minutes=30)  # Меньше минимума
        
        response = self.client.post('/api/bookings/', {
            'venue': self.venue.id,
            'date_start': start.isoformat(),
            'date_end': end.isoformat()
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('date_end', response.data)
    
    def test_create_booking_maximum_duration_api(self):
        """API: Проверка максимальной длительности через API"""
        now = timezone.now()
        start = now + timedelta(hours=1)
        end = start + timedelta(hours=25)  # Больше максимума
        
        response = self.client.post('/api/bookings/', {
            'venue': self.venue.id,
            'date_start': start.isoformat(),
            'date_end': end.isoformat()
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('date_end', response.data)
    
    def test_create_booking_past_date_api(self):
        """API: Проверка, что нельзя бронировать в прошлом"""
        now = timezone.now()
        start = now - timedelta(hours=2)  # В прошлом
        end = now - timedelta(hours=1)
        
        response = self.client.post('/api/bookings/', {
            'venue': self.venue.id,
            'date_start': start.isoformat(),
            'date_end': end.isoformat()
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('date_start', response.data)
    
    def test_create_booking_too_far_future_api(self):
        """API: Проверка максимального срока бронирования заранее"""
        now = timezone.now()
        max_advance_days = getattr(settings, 'BOOKING_MAX_ADVANCE_DAYS', 90)
        start = now + timedelta(days=max_advance_days + 1)  # Слишком далеко
        end = start + timedelta(hours=2)
        
        response = self.client.post('/api/bookings/', {
            'venue': self.venue.id,
            'date_start': start.isoformat(),
            'date_end': end.isoformat()
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('date_start', response.data)
    
    def test_create_booking_inactive_venue_api(self):
        """API: Проверка, что нельзя бронировать неактивную площадку"""
        self.venue.is_active = False
        self.venue.save()
        
        now = timezone.now()
        start = now + timedelta(hours=1)
        end = start + timedelta(hours=2)
        
        response = self.client.post('/api/bookings/', {
            'venue': self.venue.id,
            'date_start': start.isoformat(),
            'date_end': end.isoformat()
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('venue', response.data)
    
    def test_create_booking_overlapping_time_api(self):
        """API: Проверка, что нельзя бронировать в занятое время"""
        now = timezone.now()
        start = now + timedelta(hours=1)
        end = start + timedelta(hours=2)
        
        # Создаём первое бронирование
        Booking.objects.create(
            user=self.user,
            venue=self.venue,
            date_start=start,
            date_end=end,
            total_price=Decimal('2000.00'),
            status='confirmed'
        )
        
        # Пытаемся создать перекрывающееся бронирование
        response = self.client.post('/api/bookings/', {
            'venue': self.venue.id,
            'date_start': (start + timedelta(minutes=30)).isoformat(),
            'date_end': (end + timedelta(minutes=30)).isoformat()
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('venue', response.data)
    
    def test_create_booking_valid_api(self):
        """API: Создание корректного бронирования"""
        now = timezone.now()
        start = now + timedelta(hours=1)
        end = start + timedelta(hours=2)
        
        response = self.client.post('/api/bookings/', {
            'venue': self.venue.id,
            'date_start': start.isoformat(),
            'date_end': end.isoformat()
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['venue'], self.venue.id)
    
    def test_calculate_total_price(self):
        """Проверка правильности расчёта стоимости"""
        now = timezone.now()
        start = now + timedelta(hours=1)
        end = start + timedelta(hours=3)  # 3 часа
        
        response = self.client.post('/api/bookings/', {
            'venue': self.venue.id,
            'date_start': start.isoformat(),
            'date_end': end.isoformat()
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # 3 часа * 1000 руб/час = 3000 руб
        self.assertEqual(float(response.data['total_price']), 3000.00)


class BookingPermissionsTestCase(TestCase):
    """Тесты прав доступа к бронированиям"""
    
    def setUp(self):
        self.client = APIClient()
        
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@test.com',
            password='pass123',
            phone='+79001111111'
        )
        
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@test.com',
            password='pass123',
            phone='+79002222222'
        )
        
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='pass123',
            phone='+79003333333',
            role='admin'
        )
        
        self.venue = Venue.objects.create(
            owner=self.user1,
            title='Площадка',
            description='Описание',
            capacity=50,
            price_per_hour=Decimal('1000.00'),
            address='Адрес',
            is_active=True
        )
        
        now = timezone.now()
        self.booking = Booking.objects.create(
            user=self.user1,
            venue=self.venue,
            date_start=now + timedelta(hours=1),
            date_end=now + timedelta(hours=3),
            total_price=Decimal('2000.00')
        )
    
    def test_user_can_view_own_booking(self):
        """Пользователь может видеть своё бронирование"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f'/api/bookings/{self.booking.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_user_cannot_view_others_booking(self):
        """Пользователь не может видеть чужое бронирование"""
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(f'/api/bookings/{self.booking.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_admin_can_view_any_booking(self):
        """Админ может видеть любое бронирование"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(f'/api/bookings/{self.booking.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_anonymous_cannot_create_booking(self):
        """Анонимный пользователь не может создать бронирование"""
        now = timezone.now()
        response = self.client.post('/api/bookings/', {
            'venue': self.venue.id,
            'date_start': (now + timedelta(hours=1)).isoformat(),
            'date_end': (now + timedelta(hours=3)).isoformat()
        }, format='json')
        
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
