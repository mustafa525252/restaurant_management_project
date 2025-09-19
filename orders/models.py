from django.db import models

# Create your models here.

from django.db.models.signals import post_migrate
from django.dispatch import receiver

@receiver(post_migrate)
def create_default_order_statuses(sender,**kwargs):
    if sender.name == 'orders':
        for status in ['Pending','Processing','Completed','Cancelled']:
            OrderStatus.objects.get_or_create(name=status)