from django.urls import path
from .views import (
    ReviewListView,
    FeedbackListAPIView,
)

urlpatterns = [
    path('reviews/', ReviewListView.as_view(), name='review-list'),
    path('feedback/', FeedbackListAPIView.as_view(), name='feedback-list'),
]