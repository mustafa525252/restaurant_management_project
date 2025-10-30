from django.contrib import admin
from .models import Order

# Register your models here.


@admin.action(description="Mark selected orders as Processed")
def mark_orders_processed(modeladmin, request, queryset):
    """
    Custom admin action to mark multiple orders as 'Processed'.
    """
    updated_count = queryset.update(status='Processed')
    modeladmin.message_user(
        request,
        f"{updated_count} order(s) successfully marked as Processed."
    )

# Register the Order model with the custom action
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'status', 'created_at')  # adjust as per your model fields
    actions = [mark_orders_processed]