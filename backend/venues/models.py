from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    """Категория площадки"""
    name = models.CharField('Название категории', max_length=255, unique=True)
    
    class Meta:
        db_table = 'categories'
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Venue(models.Model):
    """Площадка для проведения мероприятий"""
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='owned_venues',
        verbose_name='Владелец'
    )
    title = models.CharField('Название', max_length=255)
    description = models.TextField('Описание')
    capacity = models.PositiveIntegerField('Вместимость', validators=[MinValueValidator(1)])
    price_per_hour = models.DecimalField('Цена за час', max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    address = models.CharField('Адрес', max_length=500)
    latitude = models.DecimalField('Широта', max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField('Долгота', max_digits=9, decimal_places=6, null=True, blank=True)
    created_at = models.DateTimeField('Дата добавления', auto_now_add=True)
    is_active = models.BooleanField('Доступна', default=True)
    categories = models.ManyToManyField(
        Category,
        through='VenueCategory',
        related_name='venues',
        verbose_name='Категории'
    )
    
    class Meta:
        db_table = 'venues'
        verbose_name = 'Площадка'
        verbose_name_plural = 'Площадки'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_average_rating(self):
        """Получить средний рейтинг площадки"""
        from reviews.models import Review
        reviews = Review.objects.filter(venue=self, is_approved=True)
        if reviews.exists():
            return round(reviews.aggregate(models.Avg('rating'))['rating__avg'], 2)
        return 0
    
    def get_reviews_count(self):
        """Получить количество одобренных отзывов"""
        from reviews.models import Review
        return Review.objects.filter(venue=self, is_approved=True).count()


class VenueImage(models.Model):
    """Фотография площадки с автоматической генерацией thumbnails"""
    venue = models.ForeignKey(
        Venue,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Площадка'
    )
    image = models.ImageField('Изображение', upload_to='venue_images/')
    
    # Thumbnails JPEG
    thumbnail_small = models.ImageField(
        'Миниатюра (маленькая)',
        upload_to='venue_images/thumbnails/',
        blank=True,
        null=True
    )
    thumbnail_medium = models.ImageField(
        'Миниатюра (средняя)',
        upload_to='venue_images/thumbnails/',
        blank=True,
        null=True
    )
    thumbnail_large = models.ImageField(
        'Миниатюра (большая)',
        upload_to='venue_images/thumbnails/',
        blank=True,
        null=True
    )
    
    # Thumbnails WebP
    thumbnail_small_webp = models.ImageField(
        'Миниатюра WebP (маленькая)',
        upload_to='venue_images/thumbnails/',
        blank=True,
        null=True
    )
    thumbnail_medium_webp = models.ImageField(
        'Миниатюра WebP (средняя)',
        upload_to='venue_images/thumbnails/',
        blank=True,
        null=True
    )
    thumbnail_large_webp = models.ImageField(
        'Миниатюра WebP (большая)',
        upload_to='venue_images/thumbnails/',
        blank=True,
        null=True
    )
    
    uploaded_at = models.DateTimeField('Дата загрузки', auto_now_add=True)
    
    class Meta:
        db_table = 'venue_images'
        verbose_name = 'Фотография площадки'
        verbose_name_plural = 'Фотографии площадок'
        ordering = ['uploaded_at']
    
    def __str__(self):
        return f"Фото {self.venue.title}"
    
    def save(self, *args, **kwargs):
        """Переопределяем save для автоматической генерации thumbnails"""
        # Если это новое изображение или изображение было изменено
        if self.pk is None or self._state.adding:
            # Импортируем здесь, чтобы избежать циклических импортов
            from .image_utils import generate_all_thumbnails, get_thumbnail_filename
            import logging
            
            logger = logging.getLogger(__name__)
            
            try:
                # Генерируем все thumbnails
                thumbnails = generate_all_thumbnails(self.image.file, self.image.name)
                
                # Сохраняем JPEG thumbnails
                if 'small' in thumbnails:
                    filename = get_thumbnail_filename(self.image.name, 'small', 'jpg')
                    self.thumbnail_small.save(filename, thumbnails['small'], save=False)
                
                if 'medium' in thumbnails:
                    filename = get_thumbnail_filename(self.image.name, 'medium', 'jpg')
                    self.thumbnail_medium.save(filename, thumbnails['medium'], save=False)
                
                if 'large' in thumbnails:
                    filename = get_thumbnail_filename(self.image.name, 'large', 'jpg')
                    self.thumbnail_large.save(filename, thumbnails['large'], save=False)
                
                # Сохраняем WebP thumbnails
                if 'small_webp' in thumbnails:
                    filename = get_thumbnail_filename(self.image.name, 'small', 'webp')
                    self.thumbnail_small_webp.save(filename, thumbnails['small_webp'], save=False)
                
                if 'medium_webp' in thumbnails:
                    filename = get_thumbnail_filename(self.image.name, 'medium', 'webp')
                    self.thumbnail_medium_webp.save(filename, thumbnails['medium_webp'], save=False)
                
                if 'large_webp' in thumbnails:
                    filename = get_thumbnail_filename(self.image.name, 'large', 'webp')
                    self.thumbnail_large_webp.save(filename, thumbnails['large_webp'], save=False)
                
                logger.info(f"Generated thumbnails for image: {self.image.name}")
            
            except Exception as e:
                logger.error(f"Error generating thumbnails for {self.image.name}: {e}")
        
        super().save(*args, **kwargs)


class VenueCategory(models.Model):
    """Связь площадки и категории (многие ко многим)"""
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'venue_categories'
        verbose_name = 'Связь площадки и категории'
        verbose_name_plural = 'Связи площадок и категорий'
        unique_together = ['venue', 'category']
    
    def __str__(self):
        return f"{self.venue.title} - {self.category.name}"

