from django.urls import path
from .views import (
    ReviewListView,
    UserReviewListView,
    ReviewCreateView,
    ReviewDetailView,
    ReviewApproveView,
    ReviewDisapproveView,
    PendingReviewsView
)

urlpatterns = [
    # Отзывы
    path('', ReviewListView.as_view(), name='review_list'),
    path('my/', UserReviewListView.as_view(), name='user_review_list'),
    path('create/', ReviewCreateView.as_view(), name='review_create'),
    path('<int:pk>/', ReviewDetailView.as_view(), name='review_detail'),
    
    # Модерация (только для администраторов)
    path('pending/', PendingReviewsView.as_view(), name='pending_reviews'),
    path('<int:pk>/approve/', ReviewApproveView.as_view(), name='review_approve'),
    path('<int:pk>/disapprove/', ReviewDisapproveView.as_view(), name='review_disapprove'),
]

