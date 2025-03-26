from django.db import models
from django.utils import timezone

class SRRequest(models.Model):
    date = models.DateTimeField(default=timezone.now, blank=True, null=True)  # Request Date
    category = models.CharField(max_length=50, blank=True, null=True)  # Category
    psn = models.CharField(max_length=10, blank=True, null=True)  # PSN
    icicid = models.CharField(max_length=20, blank=True, null=True)  # ICICID
    plan = models.CharField(max_length=50, blank=True, null=True)  # Plan
    engineer = models.CharField(max_length=50, blank=True, null=True)  # Engineer
    requestor_comments = models.TextField(blank=True, null=True)  # Requestor Comments
    sim_status_during_request = models.TextField(blank=True, null=True)  # SIM Status During Request
    existing_validity = models.DateTimeField(blank=True, null=True)  # Existing Validity
    requestor_validity_start_date = models.DateTimeField(blank=True, null=True)  # Requestor Validity Start Date
    requestor_validity_end_date = models.DateTimeField(blank=True, null=True)  # Requestor Validity End Date
    billing_to = models.CharField(max_length=50, blank=True, null=True)  # Billing To
    remarks = models.TextField(blank=True, null=True)  # Remarks
    hod_remarks = models.TextField(blank=True, null=True)  # HOD Remarks
    engineer_email = models.EmailField(max_length=255, blank=True, null=True)
    # New Fields
    new_sr_no = models.CharField(max_length=20, blank=True, null=True)  # New SR No
    sr_date = models.DateTimeField(blank=True, null=True)  # SR Date
    sr_success_date = models.DateTimeField(blank=True, null=True)  # SR Success Date
    status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'),('Closed', 'Closed')],
        default='Pending'
    )  # Status

    def __str__(self):
        return f"SR Request {self.id} - {self.psn}"

class SRDetails(models.Model):
    sr_request = models.OneToOneField('SRRequest', on_delete=models.CASCADE, related_name='details')
    new_sr_no = models.CharField(max_length=20, blank=True, null=True)
    sr_date = models.DateTimeField(blank=True, null=True)
    sr_success_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[('Closed', 'Closed'), ('Pending', 'Pending')],
        blank=True,
        null=True
    )

    def __str__(self):
        return f"SR Details for Request {self.sr_request.id}"
