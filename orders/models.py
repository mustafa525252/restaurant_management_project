from django.db import models
from .models import OrderStatus
import django.config.auth.models import User

# Create your models here.

class Order(models.Model):
    customer=models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders'
        )
    order_date=models.DateTimeField(auto_now_add=True)

    status=model.ForeignKey(
        OrderStatus,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders'
    )

    def __str__(self):
        return f"Order #{self.id} - {self.status.name if self.status else 'No Status'}"

    class Meta:
        ordering=['-order_date']