from django.urls import path
from .views import (
    CategoryListView,
    VenueListView,
    VenueDetailView,
    VenueImageUploadView
)

urlpatterns = [
    # Категории
    path('categories/', CategoryListView.as_view(), name='category_list'),
    
    # Площадки
    path('', VenueListView.as_view(), name='venue_list'),
    path('<int:pk>/', VenueDetailView.as_view(), name='venue_detail'),
    
    # Фотографии
    path('<int:venue_id>/images/', VenueImageUploadView.as_view(), name='venue_image_upload'),
    path('<int:venue_id>/images/<int:image_id>/', VenueImageUploadView.as_view(), name='venue_image_delete'),
]

