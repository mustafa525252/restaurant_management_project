from rest_framework import serializers
from .models import (
    MenuCategory,
    MenuItemSerializer,
    Table,
    ContactFormSubmission,
    Ingredient,
    Restaurant,
    DailySpecial,
    UserReview,
    Review,
    MenuItem,
    OpeningHour,
    FAQ,
    Cuisine
)

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
        
class DailySpecialSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailySpecial
        fields = ['id', 'name', 'description', 'price', 'is_available', 'created_at']
        
class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = '__all__'
        
class UserReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = UserReview
        fields = ['id', 'user', 'menu_item', 'rating', 'comment', 'review_date']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value
    
class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'user', 'rating', 'text', 'created_at']
        
class MenuItemAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'is_available']
        
class MenuItemSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'image']  # Return only necessary fields
        
class OpeningHourSerializer(serializers.ModelSerializer):
    day_name = serializers.CharField(source='get_day_display', read_only=True)

    class Meta:
        model = OpeningHour
        fields = ['day', 'day_name', 'opening_time', 'closing_time', 'is_closed']


class RestaurantDetailSerializer(serializers.ModelSerializer):
    opening_hours = OpeningHourSerializer(
        many=True, read_only=True, source='openinghour_set'
    )

    class Meta:
        model = Restaurant
        fields = [
            'id', 'name', 'address', 'contact_number',
            'operating_days', 'has_delivery', 'opening_hours'
        ]
        
class MenuItemDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'description', 'price', 'is_available']
        
        
class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ['id', 'question', 'answer', 'created_at']
        
class CuisineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cuisine
        fields = ['id', 'name']