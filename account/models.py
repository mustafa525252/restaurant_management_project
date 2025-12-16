from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

CUISINE_CHOICES = (
    ('italian', 'Italian'),
    ('mexican', 'Mexican'),
    ('asian', 'Asian'),
    ('vegetarian', 'Vegetarian'),
)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    preferred_cuisine = models.CharField(
        max_length=20,
        choices=CUISINE_CHOICES,
        blank=True,
        null=True,
        help_text="Select your preferred cuisine"
    )

    def get_full_name(self):
        """
        Returns full name using first_name and last_name from the linked User model.
        Handles missing values gracefully.
        """
        first = self.user.first_name or ""
        last = self.user.last_name or ""

        full_name = f"{first} {last}".strip()
        return full_name if full_name else ""

    def __str__(self):
        return f"{self.user.username}'s Profile"

class CustomerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="customer_profile"
    )
    phone_number = models.CharField(max_length=15)
    delivery_address = models.TextField()

    def __str__(self):
        return f"{self.user.username} - Customer Profile"