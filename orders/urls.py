from django.urls import path
from .views import CouponValidationView, CancelOrderAPIView, OrderDetailAPIView


urlpatterns = [
    path('coupons/validate/', CouponValidationView.as_view(), name="coupon-validate"),
    path('<int:id>/', OrderDetailAPIView.as_view(), name='order_detail'),
    path('orders/<str:order_id>/cancel/', CancelOrderAPIView.as_view(), name='cancel-order'),
]