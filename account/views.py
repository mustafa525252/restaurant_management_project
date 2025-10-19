from rest_framework import viewsets, permissions
from django.contrib.auth.models import User
from .serializers import UserProfileSerializer

class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Users can only view or update their own profile
        return User.objects.filter(id=self.request.user.id)

    def perform_update(self, serializer):
        # Save only for the logged-in user
        serializer.save()
