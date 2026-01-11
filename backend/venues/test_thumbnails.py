"""
Тесты для проверки генерации thumbnails
"""
import logging
import os
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from io import BytesIO

from venues.models import Venue, VenueImage, Category
from venues.image_utils import (
    generate_thumbnail,
    generate_all_thumbnails,
    get_thumbnail_filename,
    THUMBNAIL_SIZES
)

User = get_user_model()
logger = logging.getLogger(__name__)


def create_test_image(width=1000, height=800, format='JPEG'):
    """Создаёт тестовое изображение в памяти"""
    image = Image.new('RGB', (width, height), color='red')
    output = BytesIO()
    image.save(output, format=format)
    output.seek(0)
    return output


@override_settings(
    APPEND_SLASH=False,
    SECURE_SSL_REDIRECT=False,
    SECURE_PROXY_SSL_HEADER=None,
    MEDIA_ROOT='/tmp/test_media/'  # Временная папка для тестов
)
class ThumbnailGenerationTestCase(TestCase):
    """Тесты для проверки генерации thumbnails"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='user@test.com',
            password='testpass123',
            full_name='Test User',
            role='admin'
        )
        
        self.category = Category.objects.create(name='Test Category')
        
        self.venue = Venue.objects.create(
            title='Test Venue',
            description='Test Description',
            address='Test Address',
            latitude=55.7558,
            longitude=37.6173,
            price_per_hour=1000,
            capacity=10,
            owner=self.user,
            is_active=True
        )
        self.venue.categories.add(self.category)
    
    def test_generate_thumbnail_jpeg(self):
        """Проверка генерации JPEG thumbnail"""
        test_image = create_test_image(1000, 800)
        thumbnail = generate_thumbnail(test_image, (300, 300), format='JPEG')
        
        self.assertIsNotNone(thumbnail)
        
        # Проверяем что thumbnail - это ContentFile
        from django.core.files.base import ContentFile
        self.assertIsInstance(thumbnail, ContentFile)
        
        # Проверяем размеры
        img = Image.open(thumbnail)
        self.assertLessEqual(img.width, 300)
        self.assertLessEqual(img.height, 300)
    
    def test_generate_thumbnail_webp(self):
        """Проверка генерации WebP thumbnail"""
        test_image = create_test_image(1000, 800)
        thumbnail = generate_thumbnail(test_image, (300, 300), format='WEBP')
        
        self.assertIsNotNone(thumbnail)
        
        # Проверяем что это WebP
        img = Image.open(thumbnail)
        self.assertEqual(img.format, 'WEBP')
    
    def test_generate_all_thumbnails(self):
        """Проверка генерации всех размеров thumbnails"""
        test_image = create_test_image(2000, 1500)
        thumbnails = generate_all_thumbnails(test_image, 'test.jpg')
        
        # Проверяем что созданы все thumbnails
        expected_keys = ['small', 'medium', 'large', 'small_webp', 'medium_webp', 'large_webp']
        for key in expected_keys:
            self.assertIn(key, thumbnails)
            self.assertIsNotNone(thumbnails[key])
    
    def test_get_thumbnail_filename(self):
        """Проверка генерации имён файлов для thumbnails"""
        filename = get_thumbnail_filename('venue.jpg', 'small', 'jpg')
        self.assertEqual(filename, 'venue_small.jpg')
        
        filename = get_thumbnail_filename('test-image.jpg', 'medium', 'webp')
        self.assertEqual(filename, 'test-image_medium.webp')
    
    def test_thumbnail_sizes(self):
        """Проверка что размеры thumbnails соответствуют ожиданиям"""
        test_image = create_test_image(2000, 1500)
        
        for size_name, size in THUMBNAIL_SIZES.items():
            thumbnail = generate_thumbnail(test_image, size, format='JPEG')
            self.assertIsNotNone(thumbnail)
            
            img = Image.open(thumbnail)
            # Проверяем что изображение не больше заданного размера
            self.assertLessEqual(img.width, size[0])
            self.assertLessEqual(img.height, size[1])
            
            # Сбрасываем указатель для следующей итерации
            test_image.seek(0)


@override_settings(
    APPEND_SLASH=False,
    SECURE_SSL_REDIRECT=False,
    SECURE_PROXY_SSL_HEADER=None,
    MEDIA_ROOT='/tmp/test_media/'
)
class VenueImageModelTestCase(TestCase):
    """Тесты для модели VenueImage с автогенерацией thumbnails"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='user@test.com',
            password='testpass123',
            full_name='Test User',
            role='admin'
        )
        
        self.category = Category.objects.create(name='Test Category')
        
        self.venue = Venue.objects.create(
            title='Test Venue',
            description='Test Description',
            address='Test Address',
            latitude=55.7558,
            longitude=37.6173,
            price_per_hour=1000,
            capacity=10,
            owner=self.user,
            is_active=True
        )
        self.venue.categories.add(self.category)
    
    def test_venue_image_creates_thumbnails_on_save(self):
        """Проверка что thumbnails создаются автоматически при сохранении"""
        # Создаём тестовое изображение
        test_image_file = create_test_image(1500, 1200)
        image_file = SimpleUploadedFile(
            name='test_venue.jpg',
            content=test_image_file.read(),
            content_type='image/jpeg'
        )
        
        # Создаём VenueImage
        venue_image = VenueImage.objects.create(
            venue=self.venue,
            image=image_file
        )
        
        # Перезагружаем из БД
        venue_image.refresh_from_db()
        
        # Проверяем что thumbnails созданы
        self.assertTrue(venue_image.thumbnail_small)
        self.assertTrue(venue_image.thumbnail_medium)
        self.assertTrue(venue_image.thumbnail_large)
        self.assertTrue(venue_image.thumbnail_small_webp)
        self.assertTrue(venue_image.thumbnail_medium_webp)
        self.assertTrue(venue_image.thumbnail_large_webp)
    
    def test_thumbnail_files_exist(self):
        """Проверка что файлы thumbnails физически существуют"""
        test_image_file = create_test_image(1500, 1200)
        image_file = SimpleUploadedFile(
            name='test_venue_2.jpg',
            content=test_image_file.read(),
            content_type='image/jpeg'
        )
        
        venue_image = VenueImage.objects.create(
            venue=self.venue,
            image=image_file
        )
        
        venue_image.refresh_from_db()
        
        # Проверяем что файлы существуют
        # В тестах они будут в /tmp/test_media/
        self.assertTrue(os.path.exists(venue_image.thumbnail_small.path))
        self.assertTrue(os.path.exists(venue_image.thumbnail_medium.path))
        self.assertTrue(os.path.exists(venue_image.thumbnail_large.path))
