from django.urls import path
from .views import CouponValidationView

urlpatterns = [
    path('coupons/validate/', CouponValidationView.as_view(), name="coupon-validate")
]