from rest_framework import serializers
from django.contrib.auth.models import User

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']  # Only allow these to be updated
        read_only_fields = ['username']  # Prevent editing username


class UserLoyaltySerializer(serializers.ModelSerializer):
    class Meta:
        model = User  # or your custom UserProfile model
        fields = ['loyalty_points']