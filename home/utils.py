from django.core.mail import send_mail, BadHeaderError
from django.core.exceptions import ImproperlyConfigured
from datetime import datetime, time
import logging
from home.models import MenuItem, Cuisine
from decimal import Decimal, InvalidOperation
import re

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

def calculate_discount(original_price, discount_percentage):
    """
    Calculate the discounted price for a menu item.

    Args:
        original_price (float or Decimal): The original price of the item.
        discount_percentage (float): The discount percentage (0–100).

    Returns:
        Decimal: The discounted price rounded to two decimal places.

    Handles:
        - Negative or invalid input values.
        - Discount percentages outside the valid range.
        - Non-numeric values gracefully.
    """
    try:
        # Convert inputs to Decimal for better precision
        original_price = Decimal(str(original_price))
        discount_percentage = Decimal(str(discount_percentage))

        # Validate inputs
        if original_price < 0:
            raise ValueError("Original price cannot be negative.")
        if discount_percentage < 0 or discount_percentage > 100:
            raise ValueError("Discount percentage must be between 0 and 100.")

        # Calculate discount
        discount_amount = (original_price * discount_percentage) / Decimal(100)
        discounted_price = original_price - discount_amount

        # Ensure price doesn't go below zero
        return round(max(discounted_price, Decimal('0.00')), 2)

    except (InvalidOperation, ValueError, TypeError) as e:
        # Handle invalid inputs gracefully
        print(f"⚠️ Error calculating discount: {e}")
        return Decimal('0.00')
    
    
def is_valid_email(email: str) -> bool:
    """
    Validates an email address using a regular expression.
    Returns True if the email format is valid, otherwise False.
    """
    if not isinstance(email, str):
        return False

    # Regular expression for validating email addresses
    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    # Use re.match to check if the pattern matches the input
    if re.match(email_regex, email):
        return True
    return False