from rest_framework import serializers
from .models import (
    Review,
    Feedback,
)

class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'restaurant_name', 'user_name', 'rating', 'comment', 'created_at']


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = "__all__"