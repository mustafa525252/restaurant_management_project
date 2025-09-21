from django.db import models


class MenuCategory(models.Model):
    """
    Represents a category of menu items, such as Breakfast, Lunch, or Dinner.

    This model allow you to group menu items by category so they can easily 
    filter and display in different sections of the menu.
    """
    
    name = models.CharField(max_length=100, unique=True, verbose_name="Category Name")

    class Meta:
        verbose_name = "Menu Category"
        verbose_name_plural = "Menu Categories"
        ordering = ["name"]

    def __str__(self):
        # Return the category name as its string representation.
        return self.name
