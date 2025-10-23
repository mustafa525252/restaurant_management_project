from django.core.mail import send_mail, BadHeaderError
from django.core.exceptions import ImproperlyConfigured
from datetime import datetime, time
import logging
from home.models import MenuItem, Cuisine


def send_order_confirmation_email(order_id, customer_email, customer_name, order_items, total_amount):
    """
    Sends an order confirmation email to the customer.
    
    Args:
        order_id (str): The unique order ID.
        customer_email (str): Customer's email address.
        customer_name (str): Customer's name.
        order_items (list): List of ordered items.
        total_amount (float): Total amount for the order.
    
    Returns:
        bool: True if sent successfully, False otherwise.
    """
    subject = f"Order Confirmation - #{order_id}"
    message = (
        f"Dear {customer_name},\n\n"
        f"Thank you for your order!\n\n"
        f"Order ID: {order_id}\n"
        f"Items: {', '.join(order_items)}\n"
        f"Total Amount: ₹{total_amount}\n\n"
        f"We're preparing your order and will notify you once it’s ready.\n\n"
        f"Best regards,\n"
        f"The Restaurant Team"
    )

    from_email = None  # Uses DEFAULT_FROM_EMAIL from settings

    try:
        send_mail(subject, message, from_email, [customer_email], fail_silently=False)
        logger.info(f"Order confirmation email sent to {customer_email} for order {order_id}")
        return True
    except BadHeaderError:
        logger.error(f"Invalid header found while sending email to {customer_email}")
        return False
    except (ImproperlyConfigured, Exception) as e:
        logger.error(f"Failed to send order confirmation email to {customer_email}: {e}")
        return False
    
logger = logging.getLogger(__name__)
OPENING_HOURS = {
    'Monday':(time(9, 0), time(22, 0)),
    'Tuesday':(time(9, 0), time(22, 0)),
    'Wednesday':(time(9, 0), time(22, 0)),
    'Thursday':(time(9, 0), time(22, 0)),
    'Friday':(time(9, 0), time(23, 0)),
    'Saturday':(time(9, 0), time(23, 0)),
    'Sunday':(time(9, 0), time(21, 0)),
}

def is_restaurant_open():
    now = datetime.now()
    current_day = now.strftime('%A')
    current_time = now.time()

    hours = OPENING_HOURS.get(current_day)

    if not hours:
        return False

    open_time, close_time = hours
    return open_time <= current_time <= close_time

def get_distinct_cuisines():
    """
    Retrieve a list of all unique cuisine names currently available across menu items.
    
    This function uses Django ORM to efficiently fetch distinct cuisine names
    linked to MenuItem objects. It’s useful for dynamic filters or displaying
    available cuisines on the website.
    """
    cuisines = (
        MenuItem.objects
        .values_list('cuisine__name', flat=True)
        .distinct()
    )
    return list(cuisines)