from django.db import models

class UserRole(models.Model):
    role = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=255)

    class Meta:
        db_table = 'accounts_userrole'

    def __str__(self):
        return f"{self.username} ({self.role})"
