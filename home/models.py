from django.db import models
from django.db.models import Sum 
import random
from django.contrib.auth.models import User
from datetime import datetime
from datetime import timedelta
from django.db.models import Q
from decimal import Decimal, ROUND_HALF_UP
from django.utils import timezone
from home.utils import generate_reservation_confirmation_number


class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    contact_number = models.CharField(max_length=20)
    operating_days = models.CharField(
        max_length=100,
        help_text="Comma-separated list of days, e.g., 'Mon,Tue,Wed,Thu,Fri,Sat'"
    )
    has_delivery = models.BooleanField(default=False)

    # 🕒 Opening hours
    opening_hours = models.CharField(
        max_length=100,
        help_text="Enter opening and closing times, e.g. '11:00 AM - 11:00 PM (EST)'",
        default="11:00 AM - 11:00 PM (EST)"
    )

    # 👤 Maximum seating capacity
    capacity = models.IntegerField(
        default=0,
        help_text="Maximum number of guests the restaurant can accommodate."
    )

    def __str__(self):
        return self.name

    def get_total_menu_items(self):
        """
        Returns the total number of menu items available in the database.
        Useful for showing restaurant summary info.
        """
        from home.models import MenuItem  # local import to prevent circular import
        return MenuItem.objects.count()


class Table(models.Model):
    table_number = models.CharField(max_length=10, unique=True)
    capacity = models.PositiveIntegerField()
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"Table {self.table_number} - Capacity: {self.capacity}"


class ContactFormSubmission(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Contact Form Submission"
        verbose_name_plural = "Contact Form Submissions"
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.name} - {self.email}"


class Ingredient(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# 🧩 Custom Manager for MenuItem
class MenuItemManager(models.Manager):
    def get_top_selling_items(self, num_items=5):
        """
        Returns the top 'num_items' MenuItems based on how many times they've appeared in orders.
        """
        return (
            self.get_queryset()
            .annotate(total_sold=Sum('order_items__quantity'))
            .order_by('-total_sold')[:num_items]
        )


# ✅ Single correct MenuItem model
class MenuItem(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    # Ingredient relation
    ingredients = models.ManyToManyField(
        'Ingredient',
        related_name="menu_items",
        blank=True
    )

    # Featured item
    is_featured = models.BooleanField(
        default=False,
        help_text="Mark as featured dish"
    )

    # Availability
    is_available = models.BooleanField(
        default=True,
        help_text="Indicates if the item is currently available"
    )

    # Cuisine category
    cuisine = models.ForeignKey(
        'Cuisine',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='menu_items',
        help_text="Select the cuisine category for this dish"
    )

    # Discount
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Discount percentage (0–100)"
    )

    # Calories
    calories = models.IntegerField(
        null=True,
        blank=True,
        help_text="Calorie count (optional)"
    )

    # Allergens
    allergens = models.TextField(
        blank=True,
        null=True,
        help_text="Comma-separated allergens (e.g., gluten, nuts, dairy)"
    )

    # Gluten-free
    is_gluten_free = models.BooleanField(
        default=False,
        help_text="Indicates if the menu item is gluten-free."
    )

    objects = MenuItemManager()  # custom manager

    def __str__(self):
        if self.allergens:
            return f"{self.name} ({'Available' if self.is_available else 'Unavailable'}) - Allergens: {self.allergens}"
        return f"{self.name} ({'Available' if self.is_available else 'Unavailable'})"

    # Final price after discount
    def get_final_price(self):
        if not self.discount_percentage or self.discount_percentage <= 0:
            return float(self.price)

        discount_amount = (self.price * self.discount_percentage) / Decimal('100')
        final_price = self.price - discount_amount
        return float(final_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

    # Filter items by cuisine
    @classmethod
    def get_items_by_cuisine(cls, cuisine_type):
        return cls.objects.filter(
            cuisine__name__iexact=cuisine_type,
            is_available=True
        )

    # Check if item is today's daily special
    def is_daily_special(self):
        today = timezone.now().date()
        return DailySpecial.objects.filter(menu_item=self, date=today).exists()


class DailySpecial(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @staticmethod
    def get_random_special():
        """
        Returns a random available DailySpecial instance.
        If no specials exist, returns None.
        """
        specials = DailySpecial.objects.filter(is_available=True)
        if not specials.exists():
            return None
        return specials.order_by('?').first()

class MenuCategory(models.Model):
    name = models.CharField(max_length=150, unique=True)

    class Meta:
        verbose_name = "Menu Category"
        verbose_name_plural = "Menu Categories"
        ordering = ['name']

    def __str__(self):
        return self.name
    
class UserReviews(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField()
    comment = models.TextField()
    review_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'menu_item')  # Prevents multiple reviews from the same user for one item
        ordering = ['-review_date']  # Latest reviews first

    def __str__(self):
        return f"{self.user.username} - {self.menu_item.name} ({self.rating}/5)"
        
    
class Review(models.Model):
    """
    Model to store user reviews with ratings and text.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        help_text="Rating value between 1 (worst) and 5 (best)"
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "User Review"
        verbose_name_plural = "User Reviews"
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.user.username} ({self.rating}/5)"
    
class OpeningHour(models.Model):
    DAY_CHOICES = [
        ('Mon', 'Monday'),
        ('Tue', 'Tuesday'),
        ('Wed', 'Wednesday'),
        ('Thu', 'Thursday'),
        ('Fri', 'Friday'),
        ('Sat', 'Saturday'),
        ('Sun', 'Sunday'),
    ]

    day = models.CharField(max_length=10, choices=DAY_CHOICES, unique=True)
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    is_closed = models.BooleanField(default=False, help_text="Mark if the restaurant is closed on this day")

    class Meta:
        ordering = ['day']
        verbose_name = "Opening Hour"
        verbose_name_plural = "Opening Hours"

    def __str__(self):
        if self.is_closed:
            return f"{self.get_day_display()}: Closed"
        return f"{self.get_day_display()}: {self.opening_time.strftime('%I:%M %p')} - {self.closing_time.strftime('%I:%M %p')}"

    # ✅ Add this static method below
    @staticmethod
    def get_today_hours():
        """
        Returns today's opening hours as a string.
        Example: 'Monday: 10:00 AM - 9:00 PM' or 'Closed'
        """
        today = datetime.now().strftime('%a')  # e.g., 'Mon', 'Tue'
        today_hours = OpeningHour.objects.filter(day=today).first()

        if not today_hours:
            return "No data available"
        if today_hours.is_closed:
            return f"{today_hours.get_day_display()}: Closed"

        return f"{today_hours.get_day_display()}: {today_hours.opening_time.strftime('%I:%M %p')} - {today_hours.closing_time.strftime('%I:%M %p')}"
    
class NutritionalInformation(models.Model):
    """
    Stores detailed nutritional data for each menu item.
    """
    menu_item = models.ForeignKey(
        'MenuItem',
        on_delete=models.CASCADE,
        related_name='nutritional_info',
        help_text="Menu item associated with this nutritional information"
    )
    calories = models.IntegerField(help_text="Total calories in kcal")
    protein_grams = models.DecimalField(max_digits=5, decimal_places=2, help_text="Protein content (g)")
    fat_grams = models.DecimalField(max_digits=5, decimal_places=2, help_text="Fat content (g)")
    carbohydrate_grams = models.DecimalField(max_digits=5, decimal_places=2, help_text="Carbohydrate content (g)")

    class Meta:
        verbose_name = "Nutritional Information"
        verbose_name_plural = "Nutritional Information"

    def __str__(self):
        return f"{self.menu_item.name} - {self.calories} kcal"

def DailySpecialManager():
    raise NotImplementedError
    
    
class DailySpecial(models.Model):
    menu_item = models.ForeignKey(
        'MenuItem',
        on_delete=models.CASCADE,
        related_name='daily_specials'
    )
    date = models.DateField()

    # Attach your custom manager
    objects = DailySpecialManager()

    class Meta:
        unique_together = (('menu_item', 'date'),)
        verbose_name = "Daily Special"
        verbose_name_plural = "Daily Specials"

    def __str__(self):
        return f"{self.menu_item.name} - Special for {self.date}"

    
class ReservationManager(models.Manager):
    def get_upcoming_reservations(self):
        now = timezone.now()
        return self.filter(start_time__gt=now)


class Reservation(models.Model):
    customer_name = models.CharField(max_length=100)
    table_number = models.IntegerField()
    num_people = models.PositiveIntegerField(default=1)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    special_requests = models.TextField(blank=True, null=True)

    # 🆕 Add confirmation number
    confirmation_number = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        help_text="Unique reservation confirmation code"
    )

    # Attach custom manager
    objects = ReservationManager()

    class Meta:
        ordering = ['start_time']

    def __str__(self):
        return f"{self.customer_name} - Table {self.table_number} ({self.start_time.strftime('%Y-%m-%d %H:%M')})"

    # 🆕 Auto-generate confirmation number
    def save(self, *args, **kwargs):
        if not self.confirmation_number:
            self.confirmation_number = generate_reservation_confirmation_number()
        super().save(*args, **kwargs)

    @classmethod
    def get_available_slots(cls, start_datetime, end_datetime, table_number, slot_duration=timedelta(hours=1)):
        """
        Returns a list of available time slots for a given table within a time range.
        Avoids overlapping with existing reservations.
        """
        overlapping_reservations = cls.objects.filter(
            table_number=table_number,
            start_time__lt=end_datetime,
            end_time__gt=start_datetime
        ).order_by('start_time')

        available_slots = []
        current_time = start_datetime

        for reservation in overlapping_reservations:
            if current_time + slot_duration <= reservation.start_time:
                available_slots.append((current_time, reservation.start_time))
            if reservation.end_time > current_time:
                current_time = reservation.end_time

        if current_time + slot_duration <= end_datetime:
            available_slots.append((current_time, end_datetime))

        return available_slots
    
    
class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']  # Newest first
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

    def __str__(self):
        return self.question
    
class Table(models.Model):
    table_number = models.IntegerField(unique=True)
    capacity = models.IntegerField()
    max_seats = models.IntegerField(
        default=4,
        help_text="Maximum number of customers that can sit at this table"
    )
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"Table {self.table_number} (Capacity: {self.capacity}, Max Seats: {self.max_seats})"

    
class Cuisine(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class DeliveryZone(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Name of the delivery zone (e.g., Downtown, Northside)"
    )

    min_order_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Minimum order value required for delivery in this zone"
    )

    delivery_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Delivery fee for this zone"
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Whether this delivery zone is currently active"
    )

    def __str__(self):
        return self.name
    
    
class Ingredient(models.Model):
    name = models.CharField(max_length=100, unique=True)
    unit_of_measure = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    
