from django.contrib import admin
from .models import Restaurant, MenuItem

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
    
@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'is_available', 'is_featured', 'discount_percentage')
    list_filter = ('is_available', 'is_featured')
    search_fields = ('name', 'description')

    # ✅ Custom Action
    @admin.action(description="Mark selected items as unavailable")
    def make_unavailable(self, request, queryset):
        """
        Custom admin action to mark selected menu items as unavailable.
        """
        updated_count = queryset.update(is_available=False)
        self.message_user(request, f"{updated_count} menu item(s) marked as unavailable.")

    # ✅ Register the action
    actions = ['make_unavailable']