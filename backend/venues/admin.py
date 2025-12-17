from django.contrib import admin
from .models import Category, Venue, VenueImage, VenueCategory


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Административная панель для категорий"""
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)


class VenueImageInline(admin.TabularInline):
    """Встроенный редактор фотографий площадки"""
    model = VenueImage
    extra = 1
    fields = ('image', 'uploaded_at')
    readonly_fields = ('uploaded_at',)


class VenueCategoryInline(admin.TabularInline):
    """Встроенный редактор категорий площадки"""
    model = VenueCategory
    extra = 1


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    """Административная панель для площадок"""
    list_display = ('id', 'title', 'capacity', 'price_per_hour', 'address', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at', 'categories')
    search_fields = ('title', 'address', 'description')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    inlines = [VenueImageInline, VenueCategoryInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('owner', 'title', 'description', 'capacity', 'price_per_hour', 'is_active')
        }),
        ('Местоположение', {
            'fields': ('address', 'latitude', 'longitude')
        }),
        ('Системная информация', {
            'fields': ('created_at',)
        }),
    )


@admin.register(VenueImage)
class VenueImageAdmin(admin.ModelAdmin):
    """Административная панель для фотографий площадок"""
    list_display = ('id', 'venue', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('venue__title',)
    readonly_fields = ('uploaded_at',)
    ordering = ('-uploaded_at',)

