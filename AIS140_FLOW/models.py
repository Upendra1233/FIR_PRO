from django.db import models
from django.utils.timezone import now
from django.utils.timezone import localtime
from django.core.exceptions import ValidationError
from django.utils import timezone
class AIS140Request(models.Model):


    TELECO_STATUS = [
        ('--', 'Please Select'),
        ('Bootstrap', 'Bootstrap'),
        ('Commercial', 'Commercial'),
    ]
    TELECO_TYPE = [
        ('--', 'Please Select'),
        ('Single', 'Single'),
        ('Dual', 'Dual'),
    ]


    VEHICLE_RUNNING_LOCATION = [
        ('--', 'Please Select'),
        ('Live', 'Live'),
        ('NRD', 'NRD'),
        ('Main Battery Disconnected', 'Main Battery Disconnected'),
    ]
    CONTACT_PERSON_CHOICES = [
        ('--', 'Please Select'),
        ('Dealer', 'Dealer'),
        ('Owner', 'Owner'),
        ('Driver', 'Driver'),
    ]
    PLAN_CHOICES = [
        ('--', 'Please Select'),  # Default empty choice
        ('Dual 12', 'Dual 12'),
        ('Dual 24', 'Dual 24'),
        ('Dual 25', 'Dual 25'),
        ('Top-Up Requested', 'Top-Up Requested'),
        ('Others', 'Others'),
    ]
    CURRENT_SIM_STATUS_CHOICES = [
        ('--', 'Please Select'),
        ('BS ACTIVE', 'BS ACTIVE'),
        ('SINGLE AIR TEL', 'SINGLE AIR TEL'),
        ('DUAL', 'DUAL'),
        ('BS EXPIRED', 'BS EXPIRED'),
        ('C EXPIRED', 'C EXPIRED'),
        ('BS SUSPENDED', 'BS SUSPENDED'),
        ('OTHERS', 'OTHERS'),
    ]

    # Fields for manager_form.html
    date_of_request = models.DateTimeField(verbose_name="AL Assigned Date")
    Customer_assigned_date = models.DateTimeField(
        verbose_name="Assigned to Engineer Date"
    )
    reupdated_request_al = models.DateTimeField(
        verbose_name="=Updated To DTIL",
        null=True, blank=True,
    )
    AL_assigned_date = models.DateTimeField(
        verbose_name="A.L Assigned Date",
        null=True, blank=True,
    )
    AL_remarks =models.CharField(max_length=150, null=True, blank=True)  # New field for User ID
    AL_comments  =models.CharField(max_length=150, null=True, blank=True)  # New field for User ID

    user_id = models.CharField(max_length=50, null=True, blank=True)  # New field for User ID
    subscription_raised_by = models.CharField(max_length=50, choices=[('API', 'API'), ('Manual', 'Manual')], null=True, blank=True)  # New field for Subscription Raised By
    tat_sws_swsch = models.CharField(max_length=50, null=True, blank=True)  # New field for TAT- SWS-SWSCH
    customer_name = models.CharField(max_length=100, null=True, blank=True, verbose_name="Customer Name")
    customer_phone = models.CharField(max_length=15, null=True, blank=True, verbose_name="Customer Phone")
    dealer_name = models.CharField(max_length=100, null=True, blank=True, verbose_name="Dealer Name")
    assigned_to = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    TSM_mail = models.CharField(max_length=50,null=True, blank=True, verbose_name="TSM Mail ID")
    rto_code = models.CharField(max_length=50, null=True, blank=True,verbose_name="RTO Code")
    rto_name = models.CharField(max_length=100, null=True, blank=True,verbose_name="RTO Name")
    vehicle_available_in_workshop = models.BooleanField(default=False, null=True, blank=True)
    assigned_engineer_email = models.CharField(max_length=100,null=True, blank=True)
    device_mode = models.CharField(max_length=50,  null=True, blank=True)
    request_type = models.CharField(max_length=50, default="Please Select", null=True, blank=True)
    request_id=models.CharField(max_length=50, null=True, blank=True)
    vin_no = models.CharField(max_length=50, null=True, blank=True,verbose_name="Chassis No")
    psn = models.CharField(max_length=50, null=True, blank=True,verbose_name="PSN No")
    aadhar_card = models.CharField(max_length=50, null=True, blank=True,verbose_name="AADHAR No")
    teleco_status = models.CharField(max_length=50, choices=TELECO_STATUS, null=True, blank=True)
    teleco_type = models.CharField(max_length=50, choices=TELECO_TYPE, null   =True, blank=True)
    validity_expiry_date = models.DateField(null=True, blank=True)
    pan_card = models.CharField(max_length=50, null=True, blank=True,verbose_name="PAN No")
    manufacturing_year = models.CharField(max_length=50,null=True, blank=True, verbose_name="Manufacturing Year")
    ticket_through = models.CharField(max_length=50,null=True, blank=True, verbose_name="Ticket Through")

    engine = models.CharField(max_length=50, null=True, blank=True,verbose_name="Engine No")
    vehicle_no = models.CharField(max_length=50, null=True, blank=True,verbose_name="Vehicle Regn No")
    vehicle_model = models.CharField(max_length=100, null=True, blank=True,verbose_name="Vehicle Model")
    owner_name = models.CharField(max_length=100, null=True, blank=True)
    owner_phone = models.CharField(max_length=15, null=True, blank=True)
    ao_name = models.CharField(max_length=100, null=True, blank=True, verbose_name="AO Name")
    ro = models.CharField(max_length=100, null=True, blank=True, verbose_name="RO Name")
    zone = models.CharField(max_length=100, null=True, blank=True)
    sim_activation_manual = models.BooleanField(default=False, null=True, blank=True)
    sim_activation_service = models.BooleanField(default=False, null=True, blank=True)
    request_sent_by_email = models.EmailField(null=True, blank=True)
    icicid_no = models.CharField(max_length=20, null=True, blank=True)
    imei_no = models.CharField(max_length=17, null=True, blank=True)
    AIS140_Type=models.CharField(max_length=50, null=True, blank=True, verbose_name="AIS140 Type")
    Cust_veh_Regn_Pincode=models.CharField(max_length=50, null=True, blank=True, verbose_name="AIS140 Type")
    Customer_mobile_number = models.CharField(max_length=15, null=True, blank=True)
    Customer_Alternate_number= models.CharField(max_length=15, null=True, blank=True,verbose_name="Cust Alt Contact No")
    Customer_Email_ID= models.EmailField(null=True, blank=True)
    additional_email_id=models.EmailField(null=True, blank=True)
    temp_raised_by= models.CharField(max_length=100, null=True, blank=True, verbose_name="Temparary Raised By")
    perm_raised_by= models.CharField(max_length=100, null=True, blank=True, verbose_name="Permanent Raised By")
    Cust_veh_Regn_Address= models.TextField(null=True, blank=True, verbose_name="Cust Veh Regn Address")
    Dealer_Contact= models.CharField(max_length=15, null=True, blank=True)
    Dealer_Location= models.CharField(max_length=100, null=True, blank=True)
    Dealer_Email_ID= models.EmailField(null=True, blank=True)
    Ialert_Email_ID= models.EmailField(null=True, blank=True)
    current_sim_status = models.CharField(
        max_length=50,
        choices=CURRENT_SIM_STATUS_CHOICES,
        null=True,
        blank=True,
        verbose_name="Current SIM Status"
    )
    dealer_code = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Dealer Code"
    )
    category = models.CharField(
        max_length=50,
        default='--',
        null=True,
        blank=True,
        verbose_name="Category"
    )
    requested_by = models.CharField(max_length=100, null=True, blank=True, verbose_name="Requested By")
    requested_name = models.CharField(max_length=100, null=True, blank=True, verbose_name="Requestor Email ID")
    requested_phone_number = models.CharField(max_length=10, null=True, blank=True, verbose_name="Requestor Phone Number")
    existing_plan_start_date = models.DateTimeField(null=True, blank=True)
    existing_plan_end_date = models.DateTimeField(null=True, blank=True)
    reqd_plan_start_date = models.DateTimeField(null=True, blank=True)
    reqd_plan_end_date = models.DateTimeField(null=True, blank=True)
    plan_reqd = models.CharField(max_length=50, choices=PLAN_CHOICES, null=True, blank=True)
    top_up_reqd_for = models.TextField(null=True, blank=True)
    sr_req_no = models.CharField(max_length=50, null=True, blank=True)
    sr_req_date = models.DateTimeField(null=True, blank=True)
    sr_success_date = models.DateTimeField(null=True, blank=True)
    tat_sr_s_sr_r = models.CharField(max_length=100, null=True, blank=True)
    existing_sw = models.CharField(max_length=100, null=True, blank=True)
    sch_sw = models.CharField(max_length=100, null=True, blank=True)
    sw_sch_date = models.DateTimeField(null=True, blank=True)
    sw_success_date = models.DateTimeField(null=True, blank=True)
    veh_status = models.CharField(max_length=50, choices=[
        ('In BB Location', 'In BB Location'),
        ('BB Completed', 'BB Completed')
    ], null=True, blank=True)
    certification_start_date = models.DateField(null=True, blank=True, verbose_name="Certification Start Date")
    certification_end_date = models.DateField(null=True, blank=True, verbose_name="Certification End Date")
    bb_completed_date = models.DateField(null=True, blank=True)
    sos_fitment = models.CharField(max_length=20, choices=[
        ('Done', 'Done'),
        ('Not Done', 'Not Done')
    ], null=True, blank=True)
    sos_fitment_date = models.DateTimeField(null=True, blank=True)
    sos_verification_reqd = models.CharField(max_length=10, choices=[
        ('Yes', 'Yes'),
        ('No', 'No')
    ], null=True, blank=True)
    sos_verified_date = models.DateTimeField(null=True, blank=True)
    data_posting_verification = models.CharField(max_length=10, choices=[
        ('Yes', 'Yes'),
        ('No', 'No')
    ], null=True, blank=True)
    data_verified_date = models.DateTimeField(null=True, blank=True)
    otp_generated_date = models.DateTimeField(null=True, blank=True)
    otp_updated_date = models.DateTimeField(null=True, blank=True)
    TEMP_CERT_CHOICES = [
        ('Yes', 'Yes'),
        ('No', 'No'),
    ]
    temp_cert_reqd = models.CharField(
        max_length=10,
        choices=TEMP_CERT_CHOICES,
        default='No',  # Set a valid default value
        verbose_name="Temporary Certificate Required"
    )
    temp_cert_date = models.DateTimeField(null=True, blank=True)
    permanent_certificate = models.TextField(null=True, blank=True)
    permanent_cert_date = models.DateTimeField(null=True, blank=True)
    responsibility = models.TextField(null=True, blank=True)
    completion_status = models.CharField(
        max_length=50,
        default='Pending',
        null=True,
        blank=True
    )
    completion_date = models.DateTimeField(null=True, blank=True)
    upload_certificate_in_ialert = models.FileField(
    upload_to='certificates/',
    null=True,
    blank=True,
    verbose_name="Upload Certificate in iAlert"
    )
    upload_certificate_in_ialert_01 = models.FileField(
    upload_to='certificates/',
    null=True,
    blank=True,
    verbose_name="Upload Second Certificate"
    )
    upload_certificate_in_ialert_02 = models.FileField(
    upload_to='certificates/',
    null=True,
    blank=True,
    verbose_name="Upload Third Certificate"
    )
    mail_to_customer = models.CharField(max_length=250,null=True, blank=True)
    Dealer_mail = models.CharField(max_length=250,null=True, blank=True)
    upload_certificate_in_danlaw_server = models.TextField(null=True, blank=True)
    total_tat = models.CharField(max_length=100, null=True, blank=True)
    engr_to_monitor = models.EmailField(null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)
    # Fields for engineer_form.html
    d1 = models.TextField(blank=True, null=True)
    D1_comments = models.TextField(blank=True, null=True)
    D1_engineer = models.CharField(max_length=255, blank=True, null=True)
    D1_closure= models.DateTimeField(null=True, blank=True)
    D2_engineer = models.CharField(max_length=255, blank=True, null=True)
    d2 = models.TextField(blank=True, null=True)
    D2_comments= models.TextField(blank=True, null=True)
    D2_closure= models.DateTimeField(null=True, blank=True)
    d3 = models.TextField(blank=True, null=True)
    communication_status = models.CharField(max_length=100, null=True, blank=True)
    vehicle_running_location = models.CharField(
        max_length=50,
        choices=VEHICLE_RUNNING_LOCATION,
        default='Live',
        null=True,
        blank=True
    )
    contact_person = models.CharField(
        max_length=30,
        choices=CONTACT_PERSON_CHOICES,
        default='Dealer'
    )
    contact_person_phone = models.CharField(max_length=15, null=True, blank=True)
    sw_flashed_version = models.CharField(max_length=50, null=True, blank=True)
    sw_flashed_date = models.DateField(null=True, blank=True)
    SOS_VERIFICATION = [
    ('', 'Please Select'),  # empty string as placeholder
    ('Yes', 'Yes'),
    ('No', 'No'),
    ]
    remarks_02 = models.TextField(null=True, blank=True,verbose_name="Remarks")
    Update_to_AL_API=models.CharField(max_length=250, null=True, blank=True, verbose_name="Update to AL API")

    sos_verification = models.CharField(
    max_length=30,
    choices=SOS_VERIFICATION,
    null=True,
    blank=True
    )

    unique_id = models.CharField(
    max_length=20,
    unique=True,
    blank=True,
    null=True,
    editable=False,          # hide from forms/admin
)

    def save(self, *args, **kwargs):
        if self.pk:                                       # updating
            orig = AIS140Request.objects.filter(pk=self.pk).only('request_id').first()
            if orig:
                self.request_id = orig.request_id        # ignore any change
        else:
            # first save, maybe set request_id from incoming data
            pass

        if not self.unique_id:
            current_date = now()
            year = current_date.strftime('%y')  # e.g., "25"
            month = current_date.strftime('%m')  # e.g., "05"

            # Start looking for the latest ID with the DTILAIS prefix for this year+month
            prefix = f"DTILAIS-{year}{month}"
            last_entry = (
                AIS140Request.objects
                .filter(unique_id__startswith=prefix)
                .order_by('-unique_id')
                .first()
            )

            if last_entry:
                try:
                    last_number = int(last_entry.unique_id[-4:])
                except ValueError:
                    last_number = 0
                next_number = last_number + 1
            else:
                next_number = 1025  # Start from 1025 or any starting number you prefer

            # Generate a unique ID and ensure it's not duplicated
            while True:
                candidate_id = f"{prefix}{next_number:04d}"
                if not AIS140Request.objects.filter(unique_id=candidate_id).exists():
                    break
                next_number += 1

            self.unique_id = candidate_id

        super().save(*args, **kwargs)

    def __str__(self):
        date_str = self.date_of_request.isoformat() if self.date_of_request else "No Date"
        return f"AIS140Request {self.id} - {date_str}"
    def clean(self):
        if self.date_of_request is None:
            raise ValidationError("Date of Request cannot be null.")

