from django.contrib import admin
from .models import Booking, Payment


class PaymentInline(admin.TabularInline):
    """Встроенный редактор платежей в бронировании"""
    model = Payment
    extra = 0
    readonly_fields = ('created_at',)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Административная панель для бронирований"""
    list_display = ('id', 'user', 'venue', 'date_start', 'date_end', 'status', 'total_price', 'created_at')
    list_filter = ('status', 'created_at', 'date_start')
    search_fields = ('user__username', 'user__full_name', 'venue__title')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    inlines = [PaymentInline]
    
    fieldsets = (
        ('Информация о бронировании', {
            'fields': ('user', 'venue', 'date_start', 'date_end', 'status')
        }),
        ('Финансовая информация', {
            'fields': ('total_price',)
        }),
        ('Системная информация', {
            'fields': ('created_at',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Сделать некоторые поля только для чтения при редактировании"""
        if obj:  # editing an existing object
            return self.readonly_fields + ('user', 'venue')
        return self.readonly_fields


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Административная панель для платежей"""
    list_display = ('id', 'booking', 'amount', 'status', 'payment_method', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('booking__user__username', 'booking__venue__title')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Информация о платеже', {
            'fields': ('booking', 'amount', 'status', 'payment_method')
        }),
        ('Системная информация', {
            'fields': ('created_at',)
        }),
    )

