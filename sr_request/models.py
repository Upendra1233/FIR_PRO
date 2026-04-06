from django.db import models
from django.utils import timezone
from django.utils.timezone import now
import pytz

from django.db import IntegrityError, transaction
class SRRequest(models.Model):
    unique_id = models.CharField(max_length=20, unique=True, blank=True)  # Field for the unique ID
    new_software=models.CharField(max_length=100, blank=True, null=True)  # New Software
    New_sw_sch_date=models.DateTimeField(blank=True, null=True)  # New Software Scheduled Date
    New_sw_success_date=models.DateTimeField(blank=True, null=True)  # New Software Success Date
    approved_by_HOD=models.CharField(max_length=100, blank=True, null=True)  # Approved by HOD
    date = models.DateTimeField(default=timezone.now, blank=True, null=True)  # Request Date
    category = models.CharField(max_length=50, blank=True, null=True)  # Category
    psn = models.CharField(max_length=10, blank=True, null=True)  # PSN
    old_software = models.CharField(max_length=100, blank=True, null=True)  # Old Software
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
        if not self.unique_id:
            current_date = now()
            year = current_date.strftime('%y')  # Last two digits of the year
            month = current_date.strftime('%m')  # Two-digit month
            base_id = f"SW-{year}{month}"

            # Loop to find an unused unique_id
            for i in range(10000):  # Allows up to 9999 entries per month
                candidate_id = f"{base_id}{i:04d}"
                if not SRRequest.objects.filter(unique_id=candidate_id).exists():
                    self.unique_id = candidate_id
                    break
            else:
                raise Exception("Unable to generate a unique_id after 9999 attempts.")

        # Convert manager_approval_datetime to IST if present
        if self.manager_approval_datetime:
            ist = pytz.timezone('Asia/Kolkata')
            self.manager_approval_datetime = self.manager_approval_datetime.astimezone(ist)

        # Save inside an atomic transaction
        try:
            with transaction.atomic():
                super(SRRequest, self).save(*args, **kwargs)
        except IntegrityError:
            raise IntegrityError("Duplicate unique_id detected. Please try again.")

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
