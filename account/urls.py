from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserProfileViewSet, MyLoyaltyPointsView  # import the view

router = DefaultRouter()
router.register(r'profile', UserProfileViewSet, basename='user-profile')

urlpatterns = [
    path('api/', include(router.urls)),

    # New API endpoint for loyalty points
    path('api/my-loyalty-points/', MyLoyaltyPointsView.as_view(), name='my-loyalty-points'),
]
