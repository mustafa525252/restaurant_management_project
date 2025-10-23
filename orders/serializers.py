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


# ✅ Serializer for Updating Order Status
class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    status = serializers.CharField(write_only=True)

    class Meta:
        model = Order
        fields = ['status']

    def validate_status(self, value):
        """Ensure the provided status exists in the database."""
        try:
            status_obj = OrderStatus.objects.get(name__iexact=value)
        except OrderStatus.DoesNotExist:
            raise serializers.ValidationError(f"'{value}' is not a valid order status.")
        return status_obj

    def update(self, instance, validated_data):
        instance.order_status = validated_data['status']
        instance.save()
        return instance
