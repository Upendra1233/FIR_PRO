from django.db import models
from django.utils import timezone
from django.utils.timezone import now
import pytz

class SRRequest(models.Model):
    unique_id = models.CharField(max_length=20, unique=True, blank=True)  # Field for the unique ID
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
        choices=[('Pending', 'Pending'), ('Closed', 'Closed')],
        default='Pending'
    )  # Status

    # New fields for manager approval
    manager_approval_status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')],
        default='Pending'
    )  # Manager Approval Status
    manager_approval_datetime = models.DateTimeField(blank=True, null=True)  # Manager Approval Datetime

    # New fields
    old_psn = models.CharField(max_length=10, blank=True, null=True)  # Old PSN
    old_iccid = models.CharField(max_length=20, blank=True, null=True)  # Old ICCID
    old_sim_status = models.TextField(blank=True, null=True)  # Old Sim Status
    old_validity = models.DateTimeField(blank=True, null=True)  # Old Validity

    def save(self, *args, **kwargs):
        if not self.unique_id:  # Generate unique ID only if it doesn't exist
            current_date = now()
            year = current_date.strftime('%y')  # Last two digits of the year
            month = current_date.strftime('%m')  # Two-digit month

            # Find the last entry in the database for the current year and month
            last_entry = SRRequest.objects.filter(unique_id__startswith=f"SR-{year}{month}").order_by('-unique_id').first()

            if last_entry:
                # Extract the last four digits (sequence number) from the last unique ID
                last_sequence_number = int(last_entry.unique_id[-4:])
                sequence_number = last_sequence_number + 1
            else:
                # Start from 0000 if no entries exist for the current year and month
                sequence_number = 0

            # Generate the unique ID in the format SR-YYMMNNNN
            self.unique_id = f"SR-{year}{month}{sequence_number:04d}"

        # Automatically set IST timezone for manager_approval_datetime
        if self.manager_approval_datetime:
            ist = pytz.timezone('Asia/Kolkata')
            self.manager_approval_datetime = self.manager_approval_datetime.astimezone(ist)
        super(SRRequest, self).save(*args, **kwargs)

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
    manager_approval_status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')],
        default='Pending'
    )
    manager_approval_datetime = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"SR Details for Request {self.sr_request.id}"
