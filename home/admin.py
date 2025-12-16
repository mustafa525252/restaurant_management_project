from django.contrib import admin
from .models import Restaurant, MenuItem, Table, DailyOperatingHours

# ------------------------------------------
# Restaurant Admin
# ------------------------------------------
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

    # ⭐ Optional: If Restaurant has created/updated timestamps
    # readonly_fields = ('created_at', 'updated_at')

    # Optional: Order results alphabetically by name
    ordering = ('name',)

# ------------------------------------------
# MenuItem Admin
# ------------------------------------------
@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'is_available', 'is_featured', 'discount_percentage')
    list_filter = ('is_available', 'is_featured')
    search_fields = ('name', 'description')

    # ⭐ Optional: editable fields directly in list view
    list_editable = ('is_available', 'is_featured')

    # ✅ Custom Action
    @admin.action(description="Mark selected items as unavailable")
    def make_unavailable(self, request, queryset):
        """
        Custom admin action to mark selected menu items as unavailable.
        """
        updated_count = queryset.update(is_available=False)
        self.message_user(request, f"{updated_count} menu item(s) marked as unavailable.")

    # Register the action
    actions = ['make_unavailable']

# ------------------------------------------
# Table Admin
# ------------------------------------------
@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ("table_number", "capacity", "is_available")
    list_filter = ("is_available", "capacity")
    search_fields = ("table_number",)

    # Optional: ordering for easier viewing
    ordering = ("table_number",)

    # ⭐ Optional: make availability editable from list view
    # list_editable = ("is_available",)


admin.site.register(DailyOperatingHours)