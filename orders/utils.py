import secrets
import string
from django.db import models
from django.db.models import Sum  # ✅ You forgot to import this
from orders.models import Order  # OK, but can be lazy imported if circular imports occur

COUPON_CHARACTERS = string.ascii_uppercase + string.digits


def generate_unique_coupon_code(length=10):
    """
    Generate a random alphanumeric coupon code of the given length.
    """
    return ''.join(secrets.choice(COUPON_CHARACTERS) for _ in range(length))


def get_daily_sales_total(date):
    """
    Calculate the total sales for a given date based on Order records.
    """
    # ✅ Your Order model uses 'order_date', not 'created_at'
    orders = Order.objects.filter(order_date__date=date)
    total = orders.aggregate(total_sum=Sum('price'))['total_sum']
    return total or 0


def generate_unique_order_id(model, field_name="order_id", length=8):
    """
    Generate a unique alphanumeric ID for an order.

    Args:
        model (models.Model): The Django model class to check for uniqueness.
        field_name (str): The model field name where the ID is stored (default: "order_id").
        length (int): The desired length of the ID (default: 8).

    Returns:
        str: A unique alphanumeric string.
    """
    characters = string.ascii_uppercase + string.digits  # A-Z, 0-9

    while True:
        new_id = ''.join(secrets.choice(characters) for _ in range(length))
        if not model.objects.filter(**{field_name: new_id}).exists():
            return new_id
