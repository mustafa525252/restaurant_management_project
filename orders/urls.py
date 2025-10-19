from django.urls import path
from .views import CouponValidationView
from .views import OrderDetailAPIView

urlpatterns = [
    path('coupons/validate/', CouponValidationView.as_view(), name="coupon-validate"),
    path('<int:id>/', OrderDetailAPIView.as_view(), name='order_detail'),
]