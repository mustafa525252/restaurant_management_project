from rest_framework import serializers
from .models import MenuCategory

class MenuCategorySerializer(serializers.ModelSerializer):
    # Serializer for MenuCategory model
    class Meta:
        model = MenuCategory
        fields = ['id','name']