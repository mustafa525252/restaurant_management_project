from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class OrderStatus(models.Model):
    name=models.CharField(max_length=50,unique=True)
    
    class Meta:
        verbose_name="Order Status"
        verbose_name_plural="Order Statuses"

    def __str__(self):
        return self.name

class Order(models.Model):
    customer=model.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders'
        )
    order_date=models.DateTimeField(auto_now_add=True)

    order_status=model.ForeignKey(
        "OrderStatus",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders'
    )

    def __str__(self):
        return f"Order #{self.id} - {self.order_status.name if self.status else 'No Status'}"

    class Meta:
        ordering=['-order_date']