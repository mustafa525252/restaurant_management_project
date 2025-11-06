from django.contrib import admin
from .models import Order, Coupon

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
    
    
@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percentage', 'valid_from', 'valid_until', 'is_active')
    list_filter = ('is_active', 'valid_from', 'valid_until')
    search_fields = ('code',)

    # ✅ Allow editing is_active directly from list view
    list_editable = ('is_active',)