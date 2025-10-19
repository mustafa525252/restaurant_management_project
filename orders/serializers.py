from rest_framework import serializers
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product_name','quality','price']

class OrderSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.username', read_only=True)
    order_status = serializers.StringRelatedField()  # displays the status name

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