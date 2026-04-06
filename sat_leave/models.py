from django.db import models

class LeaveRequest(models.Model):
    engineer = models.CharField(max_length=255)
    request_date = models.DateField()
    category = models.CharField(max_length=255)
    date_of_leave = models.DateField()
    manager = models.CharField(max_length=255)
    approved_by = models.CharField(max_length=255, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    
    # New field to store the action
    action = models.CharField(
        max_length=20,
        choices=[
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('Pending', 'Pending'),
        ],
        default='Pending'
    )
    def __str__(self):
        return f"Leave Request by {self.engineer} on {self.request_date}"
      