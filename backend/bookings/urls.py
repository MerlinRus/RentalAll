from django.urls import path
from .views import (
    BookingListCreateView,
    BookingDetailView,
    BookingCancelView,
    BookingConfirmView,
    PaymentListCreateView,
    PaymentDetailView,
    PaymentProcessView,
    OccupiedSlotsView
)

urlpatterns = [
    # Бронирования
    path('', BookingListCreateView.as_view(), name='booking_list'),
    path('occupied-slots/', OccupiedSlotsView.as_view(), name='occupied_slots'),
    path('<int:pk>/', BookingDetailView.as_view(), name='booking_detail'),
    path('<int:pk>/cancel/', BookingCancelView.as_view(), name='booking_cancel'),
    path('<int:pk>/confirm/', BookingConfirmView.as_view(), name='booking_confirm'),
    
    # Платежи
    path('payments/', PaymentListCreateView.as_view(), name='payment_list'),
    path('payments/<int:pk>/', PaymentDetailView.as_view(), name='payment_detail'),
    path('payments/<int:pk>/process/', PaymentProcessView.as_view(), name='payment_process'),
]

