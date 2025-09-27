from rest_framework import serializers
from .models import Item,MenuItem

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'

class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
    
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidateError("Price must be positive number.")
        return value
