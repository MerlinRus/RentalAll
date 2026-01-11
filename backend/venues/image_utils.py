"""
Утилиты для обработки изображений: генерация thumbnails, оптимизация, конвертация в WebP
"""
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import os
import logging

logger = logging.getLogger(__name__)

# Размеры thumbnails
THUMBNAIL_SIZES = {
    'small': (300, 300),    # Для карточек в списке
    'medium': (800, 600),   # Для детальной страницы
    'large': (1200, 900),   # Для галереи
}

# Качество сжатия
JPEG_QUALITY = 85
WEBP_QUALITY = 85


def generate_thumbnail(image_file, size, format='JPEG'):
    """
    Генерирует thumbnail заданного размера из изображения.
    
    Args:
        image_file: Django ImageField или file object
        size: tuple (width, height)
        format: 'JPEG' или 'WEBP'
    
    Returns:
        ContentFile с обработанным изображением
    """
    try:
        # Открываем изображение
        img = Image.open(image_file)
        
        # Конвертируем в RGB если нужно (для JPEG)
        if img.mode not in ('RGB', 'RGBA'):
            img = img.convert('RGB')
        
        # Если формат JPEG и изображение с прозрачностью, конвертируем в RGB
        if format == 'JPEG' and img.mode == 'RGBA':
            # Создаём белый фон
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])  # 3 - альфа канал
            img = background
        
        # Вычисляем новые размеры с сохранением пропорций
        img.thumbnail(size, Image.Resampling.LANCZOS)
        
        # Сохраняем в BytesIO
        output = BytesIO()
        
        if format == 'WEBP':
            img.save(output, format='WEBP', quality=WEBP_QUALITY, method=6)
        else:
            img.save(output, format='JPEG', quality=JPEG_QUALITY, optimize=True)
        
        output.seek(0)
        
        return ContentFile(output.read())
    
    except Exception as e:
        logger.error(f"Error generating thumbnail: {e}")
        return None


def generate_all_thumbnails(image_file, base_name):
    """
    Генерирует все размеры thumbnails для изображения.
    
    Args:
        image_file: Django ImageField или file object
        base_name: базовое имя файла (без расширения)
    
    Returns:
        dict с ContentFile для каждого размера:
        {
            'small': ContentFile,
            'medium': ContentFile,
            'large': ContentFile,
            'small_webp': ContentFile,
            'medium_webp': ContentFile,
            'large_webp': ContentFile,
        }
    """
    thumbnails = {}
    
    for size_name, size in THUMBNAIL_SIZES.items():
        # JPEG версия
        thumbnail = generate_thumbnail(image_file, size, format='JPEG')
        if thumbnail:
            thumbnails[size_name] = thumbnail
        
        # WebP версия
        image_file.seek(0)  # Сбрасываем указатель файла
        thumbnail_webp = generate_thumbnail(image_file, size, format='WEBP')
        if thumbnail_webp:
            thumbnails[f'{size_name}_webp'] = thumbnail_webp
    
    return thumbnails


def get_thumbnail_filename(original_filename, size_name, format='jpg'):
    """
    Генерирует имя файла для thumbnail.
    
    Args:
        original_filename: оригинальное имя файла
        size_name: 'small', 'medium', 'large'
        format: 'jpg' или 'webp'
    
    Returns:
        str: новое имя файла
    
    Example:
        'venue.jpg' -> 'venue_small.jpg'
        'venue.jpg' -> 'venue_medium.webp'
    """
    name, ext = os.path.splitext(original_filename)
    return f"{name}_{size_name}.{format}"


def optimize_image(image_file, max_size=(1920, 1080), quality=85):
    """
    Оптимизирует оригинальное изображение (уменьшает размер файла).
    
    Args:
        image_file: Django ImageField или file object
        max_size: максимальные размеры
        quality: качество сжатия (0-100)
    
    Returns:
        ContentFile с оптимизированным изображением
    """
    try:
        img = Image.open(image_file)
        
        # Конвертируем в RGB если нужно
        if img.mode not in ('RGB', 'RGBA'):
            img = img.convert('RGB')
        
        # Уменьшаем только если изображение больше max_size
        if img.width > max_size[0] or img.height > max_size[1]:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Если RGBA, конвертируем в RGB с белым фоном
        if img.mode == 'RGBA':
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            img = background
        
        # Сохраняем с оптимизацией
        output = BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)
        output.seek(0)
        
        return ContentFile(output.read())
    
    except Exception as e:
        logger.error(f"Error optimizing image: {e}")
        return None
