from django.db import models
from django.utils.timezone import now

class MappingProcess(models.Model):
    mapping_req_received_date = models.DateTimeField(blank=True, null=True)
    old_psn = models.CharField(max_length=10, blank=True, null=True)
    new_psn = models.CharField(max_length=10, blank=True, null=True)
    vin = models.CharField(max_length=17, blank=True, null=True)
    req_raised_by = models.CharField(max_length=100, blank=True, null=True)
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
    mapping_completed_device = models.CharField(max_length=50, blank=True, null=True)
    warranty_of_the_device = models.DateField(blank=True, null=True)
    manager_approval_status = models.CharField(
        max_length=20, 
        choices=[('Approved', 'Approved'), ('Rejected', 'Rejected'), ('Pending', 'Pending')], 
        default='Pending'
    )  # Manager Approval Status
    manager_approval_time = models.DateTimeField(blank=True, null=True)  # Approval Time

    def __str__(self):
        return f"Mapping Process {self.id}: Old PSN {self.old_psn} -> New PSN {self.new_psn}"
