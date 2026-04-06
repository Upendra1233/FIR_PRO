from django.db import models
from django.utils.timezone import now
from django.http import HttpResponse
import csv

class MappingProcess(models.Model):
    mapping_req_received_date = models.DateTimeField(blank=True, null=True)
    req_raised_by = models.CharField(max_length=100, blank=True, null=True)
    old_psn = models.CharField(max_length=20, blank=True, null=True)
    new_psn = models.CharField(max_length=20, blank=True, null=True)
    submitted_by = models.EmailField(blank=True, null=True)
    vin = models.CharField(max_length=17, blank=True, null=True)
    old_device_return_location = models.CharField(max_length=100, blank=True, null=True)
    date_of_old_device_sales = models.DateField(blank=True, null=True)
    first_s_activation_of_old_device = models.DateField(blank=True, null=True)
    first_c_activation_of_old_device = models.DateField(blank=True, null=True)
    old_device_telco_status = models.CharField(max_length=100, blank=True, null=True)
    old_device_validity = models.DateField(blank=True, null=True)
    current_card_status_of_new_device = models.CharField(max_length=50, blank=True, null=True)
    activation_status_of_new_device = models.CharField(max_length=50, blank=True, null=True)
    new_device_telco_status = models.CharField(max_length=100, blank=True, null=True)
    current_validity_status_of_new_device = models.DateField(blank=True, null=True)
    added_validity_for_new_device = models.TextField(blank=True, null=True)
    hod_remarks = models.TextField(blank=True, null=True)
    mapping_completion_date = models.DateField(blank=True, null=True)
    warranty_of_the_device = models.DateField(blank=True, null=True)
    mapping_done_by = models.EmailField(null=True, blank=True)  # Engineer's email
    ticket_id = models.CharField(max_length=20, unique=True, null=True, blank=True)  # Ticket ID

    manager_approval_status = models.CharField(
        max_length=100,
        choices=[('Approved', 'Approved'), ('Rejected', 'Rejected'), ('Pending', 'Pending')],
        default='Pending'
    )
    manager_approval_time = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.ticket_id:  # Generate ticket ID only if it doesn't exist
            current_year = now().strftime('%y')  # Get the last two digits of the year
            current_month = now().strftime('%m')  # Get the two-digit month
            unique_number = f"{MappingProcess.objects.count() + 1:04d}"  # Generate a unique 4-digit number
            self.ticket_id = f"DTILMP-{current_year}{current_month}{unique_number}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Mapping Process: {self.old_psn} -> {self.new_psn}"
