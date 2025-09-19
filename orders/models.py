from django.db import models

# Create your models here.

class OrderStatus(models.Model):
    name=models.CharField(
        max_length=50,
        unique=True
    )
    class Meta:
        verbose_name="Order Status"
        verbose_name_plural = "Order Statuses"
        ordering = ['name']

    def __str__(self):
        return self.name