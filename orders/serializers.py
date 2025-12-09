from rest_framework import serializers
from .models import Order, OrderStatus, PaymentMethod, Review, OrderItem
from .models import Table

class OrderStatusSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='order_status.name', read_only=True)

    class Meta:
        model = Order
        fields = ['order_id', 'status']


class OrderSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.username', read_only=True)
    order_status = OrderStatusSerializer(read_only=True)
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id',
            'order_id',
            'customer_name',
            'name',
            'quantity',
            'price',
            'order_status',
            'order_date',
            'total_amount',
        ]

    def get_total_amount(self, obj):
        """
        Returns the total price for the order using the model's calculate_total() method.
        """
        try:
            return obj.calculate_total()
        except Exception:
            # Fallback if there are no items or method error
            return obj.price * obj.quantity


# ✅ Serializer for Updating Order Status
class OrderStatusUpdateSerializer(serializers.Serializer):
    order_id = serializers.CharField()
    status = serializers.CharField()

    def validate(self, data):
        # ✅ Validate order exists
        try:
            order = Order.objects.get(order_id=data['order_id'])
        except Order.DoesNotExist:
            raise serializers.ValidationError({"order_id": "Invalid order ID."})

        # ✅ Validate status exists
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

class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = '__all__'  # ✅ Includes all fields from the model
        
        

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'user_name', 'rating', 'review_text', 'created_at']
        
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'menu_item', 'quantity', 'price']


class OrderSummarySerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(source='items.all', many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    status = serializers.CharField(source='order_status.name', read_only=True)

    class Meta:
        model = Order
        fields = ['order_id', 'status', 'total_price', 'items']

    def get_total_price(self, obj):
        return float(obj.calculate_total())
    
class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = '__all__'