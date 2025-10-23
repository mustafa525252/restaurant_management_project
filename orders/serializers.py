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
class OrderStatusUpdateSerializer(serializers.Serializer):
    order_id = serializers.CharField()
    status = serializers.CharField()

    def validate(self, data):
        # Validate order exists
        try:
            order = Order.objects.get(order_id=data['order_id'])
        except Order.DoesNotExist:
            raise serializers.ValidationError({"order_id": "Invalid order ID."})

        # Validate status
        try:
            status_obj = OrderStatus.objects.get(name__iexact=data['status'])
        except OrderStatus.DoesNotExist:
            raise serializers.ValidationError({"status": "Invalid status name."})

        data['order'] = order
        data['status_obj'] = status_obj
        return data

    def update(self, instance, validated_data):
        instance.order_status = validated_data['status_obj']
        instance.save()
        return instance
