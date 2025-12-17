from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Административная панель для отзывов"""
    list_display = ('id', 'user', 'venue', 'rating', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'rating', 'created_at')
    search_fields = ('user__username', 'venue__title', 'comment')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Информация об отзыве', {
            'fields': ('user', 'venue', 'rating', 'comment')
        }),
        ('Модерация', {
            'fields': ('is_approved',)
        }),
        ('Системная информация', {
            'fields': ('created_at',)
        }),
    )
    
    actions = ['approve_reviews', 'disapprove_reviews']
    
    def approve_reviews(self, request, queryset):
        """Одобрить выбранные отзывы"""
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} отзывов одобрено')
    approve_reviews.short_description = 'Одобрить выбранные отзывы'
    
    def disapprove_reviews(self, request, queryset):
        """Отклонить выбранные отзывы"""
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} отзывов отклонено')
    disapprove_reviews.short_description = 'Отклонить выбранные отзывы'

