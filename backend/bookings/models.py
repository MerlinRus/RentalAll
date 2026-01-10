from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from venues.models import Venue
from django.utils import timezone
from datetime import timedelta


class Booking(models.Model):
    """Бронирование площадки"""
    
    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтверждено'),
        ('cancelled', 'Отменено'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name='Пользователь'
    )
    venue = models.ForeignKey(
        Venue,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name='Площадка'
    )
    date_start = models.DateTimeField('Начало аренды')
    date_end = models.DateTimeField('Конец аренды')
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField('Общая цена', max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    
    class Meta:
        db_table = 'bookings'
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Бронь #{self.id} - {self.venue.title} ({self.get_status_display()})"
    
    def clean(self):
        """Валидация на уровне модели"""
        errors = {}
        
        if self.date_start and self.date_end:
            # Проверка порядка дат
            if self.date_end <= self.date_start:
                errors['date_end'] = 'Дата окончания должна быть после даты начала'
            
            # Проверка длительности
            duration = self.date_end - self.date_start
            duration_hours = duration.total_seconds() / 3600
            
            min_duration = getattr(settings, 'BOOKING_MIN_DURATION_HOURS', 1)
            max_duration = getattr(settings, 'BOOKING_MAX_DURATION_HOURS', 24)
            
            if duration_hours < min_duration:
                errors['date_end'] = f'Минимальная длительность бронирования - {min_duration} ч.'
            
            if duration_hours > max_duration:
                errors['date_end'] = f'Максимальная длительность бронирования - {max_duration} ч.'
        
        if errors:
            raise ValidationError(errors)
    
    def save(self, *args, **kwargs):
        """Переопределение save для вызова валидации"""
        self.full_clean()
        super().save(*args, **kwargs)
    
    def calculate_total_price(self):
        """Вычислить общую стоимость на основе времени аренды"""
        if self.date_start and self.date_end and self.venue:
            duration = self.date_end - self.date_start
            hours = duration.total_seconds() / 3600
            return round(hours * float(self.venue.price_per_hour), 2)
        return 0
    
    def is_past(self):
        """Проверка, прошло ли бронирование"""
        return self.date_end < timezone.now()
    
    def can_be_cancelled(self):
        """Можно ли отменить бронирование"""
        return self.status in ['pending', 'confirmed'] and not self.is_past()
    
    @staticmethod
    def check_availability(venue, date_start, date_end, exclude_booking_id=None):
        """Проверить доступность площадки на указанный период"""
        overlapping = Booking.objects.filter(
            venue=venue,
            status__in=['pending', 'confirmed'],
            date_start__lt=date_end,
            date_end__gt=date_start
        )
        
        if exclude_booking_id:
            overlapping = overlapping.exclude(id=exclude_booking_id)
        
        return not overlapping.exists()


class Payment(models.Model):
    """Платеж за бронирование"""
    
    STATUS_CHOICES = [
        ('pending', 'Ожидает оплаты'),
        ('paid', 'Оплачено'),
        ('failed', 'Ошибка'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('card', 'Банковская карта'),
        ('cash', 'Наличные'),
        ('transfer', 'Банковский перевод'),
    ]
    
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='Бронирование'
    )
    amount = models.DecimalField('Сумма', max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField('Способ оплаты', max_length=50, choices=PAYMENT_METHOD_CHOICES, default='card')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    
    class Meta:
        db_table = 'payments'
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Платеж #{self.id} - {self.amount} руб. ({self.get_status_display()})"

