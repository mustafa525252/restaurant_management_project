from django.db import models

class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    contact_number = models.CharField(max_length=20)

    # 🆕 New field for operating days
    operating_days = models.CharField(
        max_length=100,
        help_text="Comma-separated list of days, e.g., 'Mon,Tue,Wed,Thu,Fri,Sat'"
    )

    def __str__(self):
        return self.name