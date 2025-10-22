from django.db import models
from django.db.models import Sum
import random


class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    contact_number = models.CharField(max_length=20)
    operating_days = models.CharField(
        max_length=100,
        help_text="Comma-separated list of days, e.g., 'Mon,Tue,Wed,Thu,Fri,Sat'"
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

    # 🆕 New field
    is_featured = models.BooleanField(default=False, help_text="Mark as featured dish")

    objects = MenuItemManager()  # your custom manager

    def __str__(self):
        return self.name


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
