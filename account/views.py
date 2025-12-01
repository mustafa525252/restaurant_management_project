from rest_framework import viewsets, permissions
from django.contrib.auth.models import User
from .serializers import (
    UserProfileSerializer,
    UserLoyaltySerializer,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView




class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Users can only view or update their own profile
        return User.objects.filter(id=self.request.user.id)

    def perform_update(self, serializer):
        # Save only for the logged-in user
        serializer.save()


class MyLoyaltyPointsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserLoyaltySerializer(request.user)
        return Response(serializer.data)