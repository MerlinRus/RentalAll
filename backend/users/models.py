from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Расширенная модель пользователя
    Роли: user (обычный пользователь) / admin (администратор)
    """
    ROLE_CHOICES = [
        ('user', 'Пользователь'),
        ('admin', 'Администратор'),
    ]
    
    full_name = models.CharField('ФИО', max_length=255, blank=True)
    phone = models.CharField('Телефон', max_length=20, blank=True)
    role = models.CharField('Роль', max_length=20, choices=ROLE_CHOICES, default='user')
    
    class Meta:
        db_table = 'users_user'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-date_joined']
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def is_admin(self):
        """Проверка, является ли пользователь администратором"""
        return self.role == 'admin' or self.is_staff

