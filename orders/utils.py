import secrets
import string
import logging
from django.db.models import Sum
from django.core.mail import send_mail, BadHeaderError
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.conf import settings
from smtplib import SMTPException

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