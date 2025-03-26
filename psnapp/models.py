from django.db import models
from django.utils import timezone
import uuid
from multiselectfield import MultiSelectField

def generate_unique_number():
    return str(uuid.uuid4())

class PSNEntry(models.Model):
    ENGINEER_NAME_MAX_LENGTH = 100
    ISSUE_MAX_LENGTH = 255

    date_of_complaint = models.DateTimeField(blank=True, null=True)
    customer_raised_issue = models.TextField(null=True, blank=True)
    manager_remarks = models.TextField(null=True, blank=True)
    complaint_raised_by = models.CharField(max_length=20, null=True, blank=True)
    complaint_raised_name = models.CharField(max_length=100, default='')
    contact_number = models.CharField(max_length=10, null=True, blank=True)
    complaint_raised_through = models.CharField(max_length=20,null=True, blank=True)
    service_engineer_name = models.CharField(max_length=20, null=True, blank=True)
    device_model = models.CharField(max_length=20,null=True, blank=True)
    device_PSN = models.CharField(max_length=10, null=True, blank=True)
    VIN_number = models.CharField(max_length=100, null=True, blank=True)
    firmware = models.CharField(max_length=100, null=True, blank=True)
    configuration = models.CharField(max_length=100, null=True, blank=True)
    device_IMEI = models.BigIntegerField(blank=True, null=True)
    device_ICCID = models.CharField(max_length=20)  # Ensure this is a CharField
    date_of_sale_of_device = models.DateField(null=True, blank=True)
    telco_status = models.CharField(max_length=20, null=True, blank=True)
    active_profile = models.CharField(max_length=20, null=True, blank=True)
    vehicle_sale_date = models.DateField(null=True, blank=True)
    s_trigger_date = models.DateTimeField(null=True, blank=True)
    c_trigger_date = models.DateTimeField(null=True, blank=True)
    commercial_expiry_date = models.DateField(null=True, blank=True)
    first_communication_in_darby = models.DateTimeField(null=True, blank=True)
    last_communication_in_darby = models.DateTimeField(null=True, blank=True)
    vehicle_support_date = models.DateTimeField(null=True, blank=True)
    vehicle_type = models.CharField(max_length=20, null=True, blank=True)
    vehicle_running_location = models.CharField(max_length=255, null=True, blank=True)
    vehicle_run = models.CharField(max_length=20, null=True, blank=True)
    kilometers_hours = models.IntegerField(null=True, blank=True, verbose_name="Kilometers/Hours")
    main_battery_voltage = models.FloatField(null=True, blank=True)
    issue_identified = models.CharField(max_length=20, null=True, blank=True)
    issue_analysis = models.CharField(max_length=20, null=True, blank=True)
    EXTERNAL_MODIFICATION_CHOICES = [
        ('--','--'),
        ('Air Horn', 'Air Horn'),
        ('Alternate Cabin', 'Aiternate Cabin'),
        ('Alt-Device', 'Alt-Device'),
        ('Device Modification', 'Device Modification'),
        ('Others', 'Others'),
    ]
    external_modification = MultiSelectField(choices=EXTERNAL_MODIFICATION_CHOICES, blank=True, null=True)
    engineer_recommendation = models.CharField(max_length=20, choices=[
        ('--','--'),
        ('Repair', 'Repair'),
        ('Replace', 'Replace'),
        ('Monitor', 'Monitor'),
        ('Others', 'Others'),
    ], default='Select one')
    RESOLVED_CHOICES = [
        ('Yes', 'Yes'),
        ('No', 'No'),
    ]
    resolved_or_not = models.CharField(max_length=4, choices=RESOLVED_CHOICES, default='Select one')
    unique_id = models.CharField(max_length=10, unique=True, blank=True, null=True)
    dealer_address=models.TextField(null=True, blank=True)
    issue_description = models.TextField(null=True, blank=True)
    engineer_email = models.EmailField(null=True, blank=True)
    manager_remarks = models.TextField(null=True, blank=True)
    manager_email = models.EmailField(null=True, blank=True, default='user_name@example.com',choices=[
        ('kunal@danlawtech.com', 'kunal@danlawtech.com'),
        ('narendrareddyg@danlawtech.com', 'narendrareddyg@danlawtech.com'),
        ('upendram@danlawtech.com', 'upendram@danlawtech.com'),
    ])
    hod_remarks = models.TextField(null=True, blank=True)
    hod_approval_status = models.CharField(max_length=20, choices=[
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ], default='Pending')
    manager_approval_status = models.CharField(max_length=20, choices=[
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ], default='Pending')
    manager_approval_datetime = models.DateTimeField(null=True, blank=True)
    hod_approval_datetime = models.DateTimeField(null=True, blank=True)
    device_to_be_sent = models.CharField(max_length=20, choices=[
        ('--','--'),
        ('Goa', 'Goa'),
        ('Hyderabad', 'Hyderabad'),
        ('Chennai', 'Chennai'),
        ('others', 'Others'),
    ], default='Select one')
    call_status = models.CharField(max_length=20, choices=[
        ('Pending', 'Pending'),
        ('Monitoring', 'Monitoring'),
        ('Closed', 'Closed'),
    ], default='Select one')
    final_action_taken = models.TextField(null=True, blank=True)
    final_call_status = models.CharField(max_length=20, choices=[
        ('--','--'),
        ('Closed', 'Closed'),
        ('Pending', 'Pending'),
    ], default='Select one')
    date_of_closure = models.DateTimeField(null=True, blank=True)
    upload_file = models.FileField(upload_to='uploads/', null=True, blank=True)
    centralised_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    engineer_requested_date = models.DateTimeField(auto_now_add=True)  # Automatically set the current datetime when created

    def __str__(self):
        return self.unique_id if self.unique_id else 'PSN Entry'

# JavaScript code has been moved to a separate file: static/js/external_modification.js