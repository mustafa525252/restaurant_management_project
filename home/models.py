
from django.db import models

# Create your models here.

class MenuCategory(models.Model):
    name=models.CharField(max_length=100,unique=True)
    class Meta:
        verbose_name = "Menu Category"
        verbose_name_plural = "Menu Categories"
        ordering = ["name"]
        
    def __str__(self):
        """
        Return a human-readable string representation of the category.
        This will display as the category name in admin and Django Shell.
        """
        return self.name