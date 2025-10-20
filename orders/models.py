from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings

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
    order_id = models.CharField(max_length=12, unique=True, editable=False)  # 👈 new field

    objects = models.Manager()
    active_orders = ActiveOrderManager()

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
