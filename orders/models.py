
from django.db import models
from django.contrib.auth.models import User


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
        User,
        on_delete=models.CASCADE,
        related_name='customer_orders'
    )
    order_date = models.DateTimeField(auto_now_add=True)

    order_status = models.ForeignKey(
        OrderStatus,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='status_orders'
    )

    def __str__(self):
        return f"Order #{self.id} - {self.order_status.name if self.order_status else 'No Status'}"

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ['-order_date']