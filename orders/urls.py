from django.urls import path
from .views import (
    CouponValidationView,
    CancelOrderAPIView,
    OrderDetailAPIView,
    UpdateOrderStatusView,
    OrderStatusRetrieveView,
    PaymentMethodListAPIView,
    ReviewListView
)

urlpatterns = [
    path('coupons/validate/', CouponValidationView.as_view(), name="coupon-validate"),
    path('<int:id>/', OrderDetailAPIView.as_view(), name='order_detail'),
    path('orders/<str:order_id>/cancel/', CancelOrderAPIView.as_view(), name='cancel-order'),
    path('orders/<str:order_id>/update-status/', UpdateOrderStatusView.as_view(), name='update-order-status'),
    path('api/orders/<str:order_id>/status/', OrderStatusRetrieveView.as_view(), name='order-status'),
    path('api/payment-methods/', PaymentMethodListAPIView.as_view(), name='payment-method-list'),
    path('reviews/', ReviewListView.as_view(), name='review-list'),
]
