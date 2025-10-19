from rest_framework import serializers
from .models import MenuCategory,MenuItemSerializer,Table

class MenuCategorySerializer(serializers.ModelSerializer):
    # Serializer for MenuCategory model
    class Meta:
        model = MenuCategory
        fields = ['id','name']

class MenuItemSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()
    class Meta:
        model = MenuItemSerializer
        fields = ['id','name','description','price','category']
        
class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = ['table_number', 'capacity', 'is_available']