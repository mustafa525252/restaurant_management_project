from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from decimal import Decimal
from home.models import MenuItem  # 👈 assuming MenuItem exists in home/models.py


# 🧠 Custom Manager for querying by status
class OrderManager(models.Manager):
    def with_status(self, status_name):
        """
        Return all orders that have the given status name.
        Usage: Order.custom_orders.with_status('pending')
        """
        return self.filter(order_status__name__iexact=status_name)

    def pending(self):
        """Shortcut for pending orders."""
        return self.with_status('pending')

    def processing(self):
        """Shortcut for processing orders."""
        return self.with_status('processing')

    def completed(self):
        """Shortcut for completed orders."""
        return self.with_status('completed')


class ActiveOrderManager(models.Manager):
    def get_active_orders(self):
        return self.filter(order_status__name__in=['pending', 'processing'])


class OrderStatus(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    class Meta:
        verbose_name = "Order Status"
        verbose_name_plural = "Order Statuses"
        ordering = ['name']

    def __str__(self):
        return self.name


class Order(models.Model):
    customer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='orders'
    )
    order_date = models.DateTimeField(auto_now_add=True)
    order_status = models.ForeignKey(
        OrderStatus,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders'
    )
    name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    order_id = models.CharField(max_length=12, unique=True, editable=False)

    # ✅ Custom managers
    objects = models.Manager()              # Default manager
    active_orders = ActiveOrderManager()    # Your existing manager
    custom_orders = OrderManager()          # New custom manager for filtering by status

    def save(self, *args, **kwargs):
        from .utils import generate_unique_order_id  # local import to avoid circular imports
        if not self.order_id:
            self.order_id = generate_unique_order_id(Order, field_name="order_id", length=10)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.order_id} - {self.order_status.name if self.order_status else 'No Status'}"

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ['-order_date']

    # 🧮 Method to calculate total cost
    def calculate_total(self):
        """
        Calculate total cost of the order by summing (price * quantity) for each order item.
        """
        total = Decimal('0.00')
        for item in self.items.all():  # related_name='items' from OrderItem
            total += item.price * item.quantity
        return total


# 🧾 OrderItem model
class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='items'
    )
    menu_item = models.ForeignKey(
        MenuItem, on_delete=models.CASCADE, related_name='order_items'
    )
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} × {self.menu_item.name} (Order {self.order.order_id})"

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    is_active = models.BooleanField(default=True)
    valid_form = models.DateField()
    valid_until = models.DateField()

    class Meta:
        verbose_name = "Coupon"
        verbose_name_plural = "Coupons"
        ordering = ['-valid_form']

    def __str__(self):
        return f"{self.code} ({self.discount_percentage}% off)"
    
    def is_valid(self):
        today = timezone.now().date()
        return self.is_active and self.valid_form <= today <= self.valid_until
