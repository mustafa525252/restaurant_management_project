from rest_framework import serializers
from .models import MenuCategory,MenuItemSerializer,Table
from .models import ContactFormSubmission, Ingredient

class MenuCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuCategory
        fields = ['id', 'name']


class MenuItemSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()
    class Meta:
        model = MenuItemSerializer
        fields = ['id','name','description','price','category']
        
class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = ['table_number', 'capacity', 'is_available']
        
class ContactFormSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactFormSubmission
        fields = ['id', 'name', 'email', 'message', 'submitted_at']
        read_only_fields = ['id', 'submitted_at']
        
class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name']