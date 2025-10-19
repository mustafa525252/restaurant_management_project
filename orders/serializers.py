from rest_framework import serializers
from .models import Order, OrderStatus


class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatus
        fields = ['name']


class OrderSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.username', read_only=True)
    order_status = OrderStatusSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'customer_name',
            'name',
            'quantity',
            'price',
            'order_status',
            'order_date'
        ]
