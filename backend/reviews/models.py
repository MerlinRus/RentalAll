from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from venues.models import Venue


class Review(models.Model):
    """Отзыв о площадке"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор'
    )
    venue = models.ForeignKey(
        Venue,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Площадка'
    )
    booking = models.OneToOneField(
        'bookings.Booking',
        on_delete=models.CASCADE,
        related_name='review',
        verbose_name='Бронирование',
        null=True,
        blank=True
    )
    rating = models.SmallIntegerField(
        'Оценка',
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField('Комментарий')
    created_at = models.DateTimeField('Дата публикации', auto_now_add=True)
    is_approved = models.BooleanField('Одобрено', default=False)
    
    class Meta:
        db_table = 'reviews'
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']
        # Удалили unique_together для user+venue, теперь один отзыв на бронирование
    
    def __str__(self):
        booking_info = f" (Бронь #{self.booking.id})" if self.booking else ""
        return f"Отзыв от {self.user.username} на {self.venue.title} ({self.rating}/5){booking_info}"

