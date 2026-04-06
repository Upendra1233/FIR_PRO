from django.db import models

# Create your models here.

class DataRecord(models.Model):
    vin = models.CharField(max_length=50)
    def __str__(self):
        return f"{self.vin}"

