import secrets
import string
import logging
from django.db.models import Sum
from django.core.mail import send_mail, BadHeaderError
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.conf import settings
from smtplib import SMTPException
from decimal import Decimal, ROUND_HALF_UP,InvalidOperation
from django.db.models import Avg

logger = logging.getLogger(__name__)

COUPON_CHARACTERS = string.ascii_uppercase + string.digits
ORDER_ID_CHARACTERS = string.ascii_uppercase + string.digits


# ----------------------------------------------------------------------
# 1. Generate a Unique Coupon Code
# ----------------------------------------------------------------------
def generate_unique_coupon_code(length=10):
    """
    Generate a random alphanumeric coupon code of the given length.
    """
    return ''.join(secrets.choice(COUPON_CHARACTERS) for _ in range(length))


# ----------------------------------------------------------------------
# 2. Calculate Daily Sales Total
# ----------------------------------------------------------------------
def get_daily_sales_total(date):
    """
    Calculate the total sales for a given date based on Order records.
    """
    from orders.models import Order  # ✅ Lazy import to avoid circular dependency

    orders = Order.objects.filter(order_date__date=date)
    total = orders.aggregate(total_sum=Sum('price'))['total_sum']
    return total or 0


# ----------------------------------------------------------------------
# 3. Generate Unique Order ID
# ----------------------------------------------------------------------
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
    while True:
        new_id = ''.join(secrets.choice(ORDER_ID_CHARACTERS) for _ in range(length))
        if not model.objects.filter(**{field_name: new_id}).exists():
            return new_id


# ----------------------------------------------------------------------
# 4. Reusable Email Utility
# ----------------------------------------------------------------------
def send_email(recipient_email, subject, message_body, from_email=None):
    """
    Reusable utility to send emails using Django's send_mail function.

    Args:
        recipient_email (str): Recipient email address.
        subject (str): Email subject line.
        message_body (str): Plain text email content.
        from_email (str, optional): Sender email address. Defaults to settings.DEFAULT_FROM_EMAIL.

    Returns:
        bool: True if email sent successfully, False otherwise.
    """
    if not recipient_email:
        logger.error("No recipient email provided.")
        return False

    try:
        validate_email(recipient_email)
    except ValidationError:
        logger.error(f"Invalid recipient email address: {recipient_email}")
        return False

    from_email = from_email or getattr(settings, "DEFAULT_FROM_EMAIL", None)

    try:
        send_mail(
            subject=subject,
            message=message_body,
            from_email=from_email,
            recipient_list=[recipient_email],
            fail_silently=False,
        )
        logger.info(f"Email sent successfully to {recipient_email}")
        return True

    except BadHeaderError:
        logger.error("Invalid header found while sending email.")
    except SMTPException as e:
        logger.error(f"SMTP error occurred while sending email: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error occurred while sending email: {e}")

    return False


# ----------------------------------------------------------------------
# 5. Update Order Status Utility
# ----------------------------------------------------------------------
def update_order_status(order_id, new_status_name):
    """
    Update the status of an order given its order ID and new status name.

    Args:
        order_id (str): The unique ID of the order.
        new_status_name (str): The new status name (e.g., 'Pending', 'Processing', 'Completed').

    Returns:
        dict: A dictionary with success status and a message.
    """
    from .models import Order, OrderStatus  # Lazy import to avoid circular imports

    try:
        # Retrieve the order
        order = Order.objects.get(order_id=order_id)
    except Order.DoesNotExist:
        logger.warning(f"Order with ID {order_id} not found.")
        return {"success": False, "message": f"Order with ID {order_id} not found."}

    # Normalize and find or create the status
    new_status_name = new_status_name.strip().capitalize()
    order_status, _ = OrderStatus.objects.get_or_create(name=new_status_name)

    old_status = order.order_status.name if order.order_status else "None"
    order.order_status = order_status
    order.save()

    logger.info(
        f"✅ Order {order_id} status updated from '{old_status}' to '{new_status_name}'."
    )

    return {
        "success": True,
        "message": f"Order {order_id} status updated to '{new_status_name}'."
    }
    
# ----------------------------------------------------------------------
# 6. Calculating the order total
# ----------------------------------------------------------------------

def calculate_order_total(order_items):
    """
    Calculate the total cost of an order.

    Args:
        order_items (list of dict): A list of order items, where each item is a dictionary
            containing 'price' (float or Decimal) and 'quantity' (int).

            Example:
            [
                {"price": 99.99, "quantity": 2},
                {"price": 150.0, "quantity": 1},
            ]

    Returns:
        float: The total cost of all items in the order.
               Returns 0.0 if the list is empty or invalid data is provided.
    """

    # 🧩 Handle empty or invalid inputs gracefully
    if not order_items or not isinstance(order_items, list):
        return 0.0

    total = 0.0

    # 🧮 Iterate through items and calculate total (price * quantity)
    for item in order_items:
        try:
            price = float(item.get("price", 0))
            quantity = int(item.get("quantity", 0))
            total += price * quantity
        except (TypeError, ValueError):
            # Skip invalid items but continue calculation for valid ones
            continue

    return round(total, 2)


def calculate_tip_amount(order_total, tip_percentage):
    """
    Calculate the tip amount for a given order total and tip percentage.

    Args:
        order_total (Decimal or float): The total amount of the order before tip.
        tip_percentage (int or float): The tip percentage (e.g., 10, 15, 20).

    Returns:
        Decimal: The calculated tip amount rounded to two decimal places.
    """
    try:
        # Convert inputs to Decimal for currency precision
        order_total = Decimal(order_total)
        tip_percentage = Decimal(tip_percentage)

        # Ensure non-negative inputs
        if order_total < 0 or tip_percentage < 0:
            raise ValueError("Order total and tip percentage must be non-negative.")

        # Calculate tip amount
        tip_amount = order_total * (tip_percentage / Decimal(100))

        # Round to 2 decimal places (currency format)
        return tip_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    except Exception as e:
        # Log error or handle gracefully if needed
        print(f"Error calculating tip amount: {e}")
        return Decimal('0.00')


def calculate_discount(order_total, discount_percentage):
    """
    Calculate the discount amount for a given order total and discount percentage.

    Args:
        order_total (float | Decimal): The total amount of the order before discount.
        discount_percentage (float | Decimal): The discount percentage (e.g., 10 for 10%).

    Returns:
        Decimal: The calculated discount amount rounded to two decimal places.
                  Returns Decimal('0.00') if inputs are invalid.

    Example:
        >>> calculate_discount(100, 10)
        Decimal('10.00')
    """
    try:
        total = Decimal(order_total)
        percentage = Decimal(discount_percentage)
        if total < 0 or percentage < 0:
            return Decimal('0.00')
        discount_amount = total * (percentage / Decimal('100'))
        return discount_amount.quantize(Decimal('0.01'))
    except (InvalidOperation, TypeError, ValueError):
        # Handles non-numeric or invalid input
        return Decimal('0.00')
    

def calculate_average_rating(reviews_queryset):
    """
    Calculate the average rating from a queryset of reviews.

    Args:
        reviews_queryset (QuerySet): A queryset of Review objects containing a 'rating' field.

    Returns:
        float: The average rating rounded to 2 decimal places, or 0.0 if no reviews exist.
    """
    if not reviews_queryset.exists():
        return 0.0

    average = reviews_queryset.aggregate(avg_rating=Avg('rating'))['avg_rating']
    return round(average or 0.0, 2)