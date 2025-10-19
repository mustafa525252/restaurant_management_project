from django.urls import path
from .views import OrderDetailAPIView

urlpatterns = [
    path('orders/<int:id>/', OrderDetailAPIView.as_view(), name='order_detail'),
]
