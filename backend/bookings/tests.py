from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError
from django.test.utils import override_settings
from django.db import transaction
from rest_framework.test import APIClient
from rest_framework import status
from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch
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


@override_settings(
    APPEND_SLASH=False,
    SECURE_SSL_REDIRECT=False,
    SECURE_PROXY_SSL_HEADER=None
)
class BookingAPITestCase(TestCase):
    """Тесты API бронирований"""
    
    def setUp(self):
        self.client = APIClient()
        self.client.default_format = 'json'
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


@override_settings(
    APPEND_SLASH=False,
    SECURE_SSL_REDIRECT=False,
    SECURE_PROXY_SSL_HEADER=None
)
class BookingPermissionsTestCase(TestCase):
    """Тесты прав доступа к бронированиям"""
    
    def setUp(self):
        self.client = APIClient()
        self.client.default_format = 'json'
        
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
        
        # DRF может вернуть 403 (если объект найден но доступ запрещён) или 404 (если queryset не содержит объект)
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])
    
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


@override_settings(
    APPEND_SLASH=False,
    SECURE_SSL_REDIRECT=False,
    SECURE_PROXY_SSL_HEADER=None
)
class BookingTransactionTestCase(TestCase):
    """Тесты для проверки транзакций при операциях с бронированиями"""
    
    def setUp(self):
        self.client = APIClient()
        self.client.default_format = 'json'
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='pass123',
            phone='+79001111111'
        )
        
        self.venue = Venue.objects.create(
            owner=self.user,
            title='Площадка',
            description='Описание',
            capacity=50,
            price_per_hour=Decimal('1000.00'),
            address='Адрес',
            is_active=True
        )
        
        now = timezone.now()
        self.booking = Booking.objects.create(
            user=self.user,
            venue=self.venue,
            date_start=now + timedelta(hours=1),
            date_end=now + timedelta(hours=3),
            total_price=Decimal('2000.00'),
            status='pending'
        )
        
        self.payment = Payment.objects.create(
            booking=self.booking,
            amount=self.booking.total_price,
            payment_method='card',
            status='pending'
        )
        
        self.client.force_authenticate(user=self.user)
    
    def test_payment_process_atomic(self):
        """Проверка атомарности обработки платежа"""
        # Обработка платежа должна обновить и платёж, и бронирование
        response = self.client.post(f'/api/bookings/payments/{self.payment.id}/process/', format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Проверяем что оба объекта обновлены
        self.payment.refresh_from_db()
        self.booking.refresh_from_db()
        
        self.assertEqual(self.payment.status, 'paid')
        self.assertEqual(self.booking.status, 'confirmed')
    
    # NOTE: Следующие тесты закомментированы, так как они требуют PostgreSQL
    # SQLite не полностью поддерживает select_for_update и транзакции в многопоточности
    
    # @patch('bookings.models.Booking.save')
    # def test_payment_process_rollback_on_booking_error(self, mock_save):
    #     """Проверка отката транзакции при ошибке сохранения бронирования"""
    #     mock_save.side_effect = Exception('Database error')
    #     response = self.client.post(f'/api/bookings/payments/{self.payment.id}/process/', format='json')
    #     self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
    #     self.payment.refresh_from_db()
    #     self.assertEqual(self.payment.status, 'pending')
    
    def test_booking_cancel_with_payment_update(self):
        """Проверка что при отмене бронирования отменяются неоплаченные платежи"""
        response = self.client.post(f'/api/bookings/{self.booking.id}/cancel/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Проверяем что бронирование отменено
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, 'cancelled')
        
        # Проверяем что неоплаченный платёж также отменён
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, 'failed')
    
    # NOTE: Тест на race conditions требует настоящую БД (PostgreSQL)
    # SQLite не поддерживает полноценные блокировки для select_for_update в потоках
    
    # def test_concurrent_payment_processing(self):
    #     """Проверка защиты от race conditions при параллельной обработке платежа"""
    #     from threading import Thread
    #     results = []
    #     
    #     def process_payment():
    #         try:
    #             client = APIClient()
    #             client.default_format = 'json'
    #             client.force_authenticate(user=self.user)
    #             response = client.post(f'/api/bookings/payments/{self.payment.id}/process/', format='json')
    #             results.append(response.status_code)
    #         except Exception as e:
    #             results.append(str(e))
    #     
    #     thread1 = Thread(target=process_payment)
    #     thread2 = Thread(target=process_payment)
    #     thread1.start()
    #     thread2.start()
    #     thread1.join()
    #     thread2.join()
    #     
    #     self.assertIn(status.HTTP_200_OK, results)
    #     self.assertIn(status.HTTP_400_BAD_REQUEST, results)
    #     self.payment.refresh_from_db()
    #     self.assertEqual(self.payment.status, 'paid')

