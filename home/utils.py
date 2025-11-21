from django.core.mail import send_mail, BadHeaderError
from django.core.exceptions import ImproperlyConfigured
from datetime import datetime, time
import logging
from home.models import MenuItem, Cuisine
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import re
from home.models import DailyOperatingHours
from home.models import Table
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
        # Convert inputs to Decimal for precise arithmetic
        original_price = Decimal(str(original_price))
        discount_percentage = Decimal(str(discount_percentage))

        # Validate inputs
        if original_price < 0:
            raise ValueError("Original price cannot be negative.")
        if not (0 <= discount_percentage <= 100):
            raise ValueError("Discount percentage must be between 0 and 100.")

        # Calculate discount
        discount_amount = (original_price * discount_percentage) / Decimal("100")
        discounted_price = original_price - discount_amount

        # Prevent negative prices, round to two decimals
        final_price = max(discounted_price, Decimal("0.00"))
        return final_price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    except (InvalidOperation, ValueError, TypeError) as e:
        print(f"⚠️ Error calculating discount: {e}")
        return Decimal("0.00")
    
    
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

def get_today_operating_hours():
    """
    Retrieve the restaurant's operating hours for the current day.

    Returns:
        tuple: (open_time, close_time) if available,
               otherwise (None, None) if the restaurant is closed or entry missing.
    """
    # 1️⃣ Get current day name (e.g., "Monday")
    today = datetime.now().strftime('%A')

    # 2️⃣ Query for today's operating hours
    today_hours = DailyOperatingHours.objects.filter(day__iexact=today).first()

    # 3️⃣ Return operating hours if found, else (None, None)
    if today_hours:
        return today_hours.open_time, today_hours.close_time
    return (None, None)

def is_valid_phone_number(phone_number):
    """
    Validate a phone number string.

    Args:
        phone_number (str): The phone number to validate.

    Returns:
        bool: True if the phone number matches a basic valid format, False otherwise.
    
    A valid phone number:
    - May start with an optional '+' followed by country code (e.g., +1, +91)
    - Can contain digits, spaces, or hyphens
    - Must have 10 to 12 digits total
    """
    if not phone_number:
        return False

    # Regular expression pattern for validating phone numbers
    pattern = r'^\+?\d[\d\s\-]{8,14}\d$'

    # Use fullmatch to ensure the entire string matches the pattern
    return bool(re.fullmatch(pattern, phone_number))

def format_phone_number(phone_number: str) -> str:
    """
    Format a phone number into a consistent format: (XXX) XXX-XXXX
    Example: '9876543210' → '(987) 654-3210'
    
    Handles invalid input gracefully by returning the original string.
    """

    try:
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', phone_number)

        # Validate length (assuming 10-digit format)
        if len(digits) == 10:
            formatted = f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
            return formatted

        # Handle country code (like +91 for India)
        elif len(digits) == 12 and digits.startswith('91'):
            formatted = f"+91 {digits[2:7]}-{digits[7:]}"
            return formatted

        else:
            # If unexpected length, return as-is
            return phone_number

    except Exception as e:
        # Graceful fallback in case of invalid input
        print(f"Error formatting phone number: {e}")
        return phone_number
    
def calculate_average_rating(reviews_queryset):
    """
    Calculate the average rating from a QuerySet of reviews.

    Args:
        reviews_queryset (QuerySet): A Django QuerySet of review objects that have a 'rating' field.

    Returns:
        float: The average rating, or 0.0 if there are no reviews.
    """
    try:
        total_reviews = reviews_queryset.count()
        if total_reviews == 0:
            return 0.0

        total_rating = sum(review.rating for review in reviews_queryset)
        average = total_rating / total_reviews
        return round(float(average), 2)

    except Exception as e:
        # Log the error in real projects (e.g., using logging)
        print(f"Error calculating average rating: {e}")
        return 0.0
    
def is_valid_reservation_time(reservation_datetime: datetime) -> bool:
    weekday = reservation_datetime.weekday()

    try:
        hours = DailyOperatingHours.objects.get(day_of_week=weekday)
    except DailyOperatingHours.DoesNotExist:
        return False

    requested_time = reservation_datetime.time()

    return hours.opening_time < requested_time < hours.closing_time

def get_available_tables_by_capacity(num_guests):
    """
    Returns a QuerySet of tables that are:
    - Available (is_available=True)
    - Have capacity >= num_guests
    """
    return Table.objects.filter(is_available=True, capacity__gte=num_guests)