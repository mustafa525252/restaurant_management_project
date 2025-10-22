from django.contrib import admin
from .models import Restaurant

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    """
    Custom admin configuration for the Restaurant model
    to make the admin interface more informative and user-friendly.
    """

    # Fields to show in the list view
    list_display = ('name', 'address', 'contact_number', 'operating_days')

    # Enable search by name or address
    search_fields = ('name', 'address')

    # Optional: Add filter if you have an 'is_active' field in the model
    # Example: list_filter = ('is_active',)
    # (Commented out here since your Restaurant model doesn’t have this field yet)

    # Optional: Order results alphabetically by name
    ordering = ('name',)