from django.db import models
from django.db.models import Sum
import random
from django.contrib.auth.models import User
from datetime import datetime
from datetime import timedelta
from django.db.models import Q
from decimal import Decimal, ROUND_HALF_UP

class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    contact_number = models.CharField(max_length=20)
    operating_days = models.CharField(
        max_length=100,
        help_text="Comma-separated list of days, e.g., 'Mon,Tue,Wed,Thu,Fri,Sat'"
    )
    has_delivery = models.BooleanField(default=False)
    
    # 🕒 New field for opening hours
    opening_hours = models.CharField(
        max_length=100,
        help_text="Enter opening and closing times, e.g. '11:00 AM - 11:00 PM (EST)'",
        default="11:00 AM - 11:00 PM (EST)"
    )

    def __str__(self):
        return self.name

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
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    ingredients = models.ManyToManyField('Ingredient', related_name="menu_items", blank=True)
    is_featured = models.BooleanField(default=False, help_text="Mark as featured dish")
    is_available = models.BooleanField(default=True, help_text="Indicates if the item is currently available")

    # 🆕 New field for discounts
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Discount percentage (0-100)"
    )

    objects = MenuItemManager()  # custom manager, if defined

    def __str__(self):
        return f"{self.name} ({'Available' if self.is_available else 'Unavailable'})"

    # 🧮 New method to calculate final price after discount
    def get_final_price(self):
        """
        Calculate the final price of the menu item after applying discount (if any).
        Returns the price as a float rounded to 2 decimal places.
        """
        if not self.discount_percentage or self.discount_percentage <= 0:
            return float(self.price)

        discount_amount = (self.price * self.discount_percentage) / Decimal('100')
        final_price = self.price - discount_amount
        # Round to 2 decimal places
        return float(final_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))


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
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Menu Category"
        verbose_name_plural = "Menu Categories"
        ordering = ['name']

    def __str__(self):
        return self.name
    
class UserReview(models.Model):
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
    

class Reservation(models.Model):
    customer_name = models.CharField(max_length=100)
    table_number = models.IntegerField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    class Meta:
        ordering = ['start_time']

    def __str__(self):
        return f"{self.customer_name} - Table {self.table_number}"

    @classmethod
    def get_available_slots(cls, start_datetime, end_datetime, table_number, slot_duration=timedelta(hours=1)):
        """
        Returns a list of available time slots for a given table within a time range.
        """
        # Fetch overlapping reservations
        overlapping_reservations = cls.objects.filter(
            table_number=table_number,
            start_time__lt=end_datetime,
            end_time__gt=start_datetime
        ).order_by('start_time')

        available_slots = []
        current_time = start_datetime

        # Check for gaps between reservations
        for reservation in overlapping_reservations:
            if current_time + slot_duration <= reservation.start_time:
                available_slots.append((current_time, reservation.start_time))
            if reservation.end_time > current_time:
                current_time = reservation.end_time

        # Add final slot if available
        if current_time + slot_duration <= end_datetime:
            available_slots.append((current_time, end_datetime))

        return available_slots
    
    
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
    
    
class DailySpecialManager(models.Manager):
    def upcoming(self):
        """
        Returns only the DailySpecials scheduled for today or in the future.
        """
        today = datetime.date.today()
        return self.filter(date__gte=today)