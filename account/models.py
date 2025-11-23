from django.db import models
from django.contrib.auth.models import User

# Create your models here.

CUISINE_CHOICES = (
    ('italian', 'Italian'),
    ('mexican', 'Mexican'),
    ('asian', 'Asian'),
    ('vegetarian', 'Vegetarian'),
)


class UserProfile(models.Model):
    # Link each profile to a User
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    # Preferred cuisine option
    preferred_cuisine = models.CharField(
        max_length=20,
        choices=CUISINE_CHOICES,
        blank=True,
        null=True,
        help_text="Select your preferred cuisine"
    )

    def __str__(self):
        return f"{self.user.username}'s Profile"