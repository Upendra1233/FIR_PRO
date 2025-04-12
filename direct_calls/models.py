from django.db import models
from django.utils.timezone import now
from django.core.validators import RegexValidator
from django import forms


class DirectCall(models.Model):
    # PART A: Manager's form fields
    unique_id = models.CharField(max_length=20, unique=True, blank=True, null=True)  # Unique ID field

    date_of_complaint = models.DateTimeField(default=now, blank=True)
    complaint_raised_from_location = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Complaint Raised Location"
    )
    customer_raised_issue = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Customer Voice"
    )
    complaint_raised = models.CharField(max_length=50, null=True, blank=True)

    complaint_raised_by = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Complaint Raised By"
    )
    contact_number = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message="Contact Number must be exactly 10 digits."
            )
        ],
        verbose_name="Contact Number"
    )
    customer_mail_id = models.EmailField(null=True, blank=True)
    complaint_raised_through = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Complaint Raised Through"
    )
    complaint_received_by = models.CharField(max_length=50, null=True, blank=True)
    vin = models.CharField(
        max_length=17,
        null=True,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^[A-HJ-NPR-Z0-9]{17}$',
                message="VIN must be exactly 17 characters long and can only contain uppercase letters (A-H, J-N, P-R, Z) and digits."
            )
        ],
        verbose_name="VIN"
    )
    complaint_assigned_to = models.CharField(max_length=50, null=True, blank=True)
    submitted_to_email = models.EmailField(
        null=True,
        blank=True,
        verbose_name="Submitted To Email"
    )
    engineer_contact_number = models.CharField(max_length=10, null=True, blank=True)
    upload_file = models.FileField(
        upload_to='uploads/',
        null=True,
        blank=True,
        verbose_name="Upload File"
    )
    call_type = models.CharField(max_length=50, choices=[('Direct Call', 'Direct Call'), ('I Alert Call', 'I Alert Call')], blank=True, null=True)
    ticket_no = models.CharField(max_length=50, blank=True, null=True)

    # PART B: Engineer's form fields
    psn = models.CharField(max_length=10, null=True, blank=True, verbose_name="PSN")
    device_model = models.CharField(max_length=100, null=True, blank=True)
    telco_status = models.CharField(max_length=50, null=True, blank=True)
    active_profile = models.CharField(max_length=50, null=True, blank=True)
    activation_start_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Activation Start Date"
    )
    activation_end_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Activation End Date"
    )
    vehicle_sale_date = models.DateField(null=True, blank=True)
    first_communication_in_darby = models.DateTimeField(null=True, blank=True)
    last_communication_in_darby = models.DateTimeField(null=True, blank=True)
    vehicle_type = models.CharField(max_length=50, null=True, blank=True)
    vehicle_run = models.CharField(max_length=50, null=True, blank=True)
    kilometers_hours = models.IntegerField(null=True, blank=True)
    main_battery_voltage = models.FloatField(null=True, blank=True)
    vehicle_running_location = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    region = models.CharField(max_length=50, null=True, blank=True)
    contact_person_name = models.CharField(max_length=100, null=True, blank=True, verbose_name="Contact Person Name")
    contact_person_number = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message="Contact Person Number must be exactly 10 digits."
            )
        ],
        verbose_name="Contact Person Number"
    )
    contact_category = models.CharField(max_length=50, null=True, blank=True, verbose_name="Contact Category")
    issue_identified = models.CharField(max_length=100, null=True, blank=True)
    issue_analysis = models.CharField(max_length=100, null=True, blank=True)
    exist_software = models.CharField(max_length=100, null=True, blank=True, verbose_name="Existing Software")
    updated_software = models.CharField(max_length=100, null=True, blank=True, verbose_name="Updated Software")
    final_action_taken = models.TextField(null=True, blank=True)
    finalised_issue_category = models.CharField(max_length=100, null=True, blank=True, verbose_name="Finalised Issue Category")
    upload_file_01 = models.FileField(
        upload_to='uploads/',
        null=True,
        blank=True,
        verbose_name="Upload File"
    )
    call_status = models.CharField(max_length=20, null=True, blank=True)
    hod_comment = models.TextField(null=True, blank=True)
    date_of_closure = models.DateTimeField(null=True, blank=True)


    # Additional fields

    # New fields
 
    def save(self, *args, **kwargs):
        # Ensure complaint_raised_from_location is stored in uppercase
        if self.complaint_raised_from_location:
            self.complaint_raised_from_location = self.complaint_raised_from_location.upper()
        
        # Generate unique ID only if it doesn't exist
        if not self.unique_id:
            current_year = now().strftime('%y')  # Get the last two digits of the year
            current_month = now().strftime('%m')  # Get the two-digit month
            unique_number = f"{DirectCall.objects.count() + 1:04d}"  # Generate a unique 4-digit number
            self.unique_id = f"DTILDC-{current_year}{current_month}{unique_number}"
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Complaint by {self.complaint_raised_by} - VIN: {self.vin} (ID: {self.unique_id})"

class MappingProcess(models.Model):
    unique_id = models.CharField(max_length=20, unique=True, blank=True, null=True)  # Unique ID field

