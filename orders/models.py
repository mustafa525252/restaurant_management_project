from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from decimal import Decimal, ROUND_HALF_UP
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
        'auth.User', on_delete=models.CASCADE, related_name='orders'
    )
    order_date = models.DateTimeField(auto_now_add=True)
    order_status = models.ForeignKey(
        'OrderStatus', on_delete=models.SET_NULL, null=True, blank=True
    )
    order_id = models.CharField(max_length=12, unique=True, editable=False)
    name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def calculate_total(self):
        """
        Calculate total cost of the order by summing (price * quantity) for each order item.
        If a valid coupon/discount applies, apply it using the `calculate_discount` utility.
        """
        total = Decimal('0.00')

        # 1️⃣ Sum up item totals
        for item in self.items.all():  # related_name='items' from OrderItem
            total += item.price * item.quantity

        # 2️⃣ Apply discount if applicable
        try:
            from .utils import calculate_discount  # Lazy import to prevent circular import

            coupon = getattr(self, 'coupon', None)
            if coupon and hasattr(coupon, 'is_valid') and coupon.is_valid():
                total = calculate_discount(total, coupon.discount_percentage)

        except ImportError:
            pass
        except Exception as e:
            print(f"Discount calculation skipped due to: {e}")

        # 3️⃣ Round and return
        return total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def get_unique_item_names(self):
        """
        Returns a list of unique menu item names for this order.
        """
        unique_names = set()

        # Assumes related_name='items' from OrderItem model, and each OrderItem has menu_item FK
        for order_item in self.items.all():
            if hasattr(order_item, 'menu_item') and order_item.menu_item:
                unique_names.add(order_item.menu_item.name)

        return list(unique_names)

    def __str__(self):
        return f"Order {self.order_id} - {self.order_status.name if self.order_status else 'No Status'}"

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
