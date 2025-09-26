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

class MenuItem(models.Model):
    category = models.ForeignKey(
        MenuCategory,
        on_delete = models.CASCADE,
        related_name = "menu_items"
    )

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name