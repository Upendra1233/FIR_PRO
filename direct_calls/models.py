from django.db import models
from django.utils.timezone import now
from django.core.validators import RegexValidator
from django import forms
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

class DirectCall(models.Model):
    unique_id = models.CharField(max_length=20, unique=True, blank=True, null=True)  # Unique ID field
    date_of_complaint = models.DateTimeField(default=timezone.now)

    complaint_raised_from_location = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Complaint Raised Location"
    )
    customer_raised_issue = models.CharField(
        max_length=700,
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
        max_length=40,
        null=True,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^[0-9;\-\s]+$',
                message="Contact Number must be exactly 10 digits."
            )
        ],
        verbose_name="Contact Number"
    )
    customer_mail_id = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="Multiple emails separated by semicolon (e.g., email1@example.com;email2@example.com)"
    )
    vehicle_avl_in_workshop = models.CharField(
        max_length=3,  # 'Yes' or 'No' are 3 characters long
        # Dropdown options
        null=True,
        blank=True,
        verbose_name="Vehicle Available in Workshop"
    )
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
    complaint_assigned_to = models.CharField(max_length=50, null=True, blank=True,verbose_name="Engineer Responsible")
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
    call_type = models.CharField(
        max_length=50,
        # Remove choices=... here
        verbose_name="Call Type"
    )
    ticket_no = models.CharField(max_length=50, blank=True, null=True)
    ialert_remarks=models.TextField(max_length=1000, null=True, blank=True, verbose_name="IAlert Remarks")
    updated_contact_no=models.CharField(max_length=1400, null=True, blank=True)
    ialert_tk_timestamp=models.DateTimeField(default=timezone.now,blank=True, null=True)
    # PART B: Engineer's form fields
    psn = models.CharField(max_length=10, null=True, blank=True, verbose_name="Faulty Device PSN number")
    end_customer_mail_id = models.EmailField(
        null=True,
        blank=True,
        verbose_name="End Customer Mail ID"
    )
    veh_reg_no= models.CharField(max_length=100, null=True, blank=True)
    support_required=models.CharField(max_length=100, null=True, blank=True)
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
    S_trigger_date = models.DateTimeField(null=True, blank=True)
    s_trigger_completion_date = models.DateTimeField(null=True, blank=True)
    C_trigger_date = models.DateTimeField(null=True, blank=True)
    vehicle_type = models.CharField(max_length=100, null=True, blank=True)
    engine_type = models.CharField(max_length=100, null=True, blank=True, verbose_name="Engine Type")
    vehicle_run = models.CharField(max_length=50, null=True, blank=True)
    kilometers_hours = models.IntegerField(null=True, blank=True)
    main_battery_voltage = models.FloatField(null=True, blank=True, default=0)
    veh_model = models.CharField(max_length=100, null=True, blank=True, verbose_name="Veh Model")
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
    owner_contact_no=models.CharField(max_length=12, null=True, blank=True, verbose_name="Contact Category")
    customer_contact_no=models.CharField(max_length=12, null=True, blank=True, verbose_name="Owner Contact No(Darby)")
    al_mfg_plant = models.CharField(max_length=100, blank=True, null=True)
    nrd_category = models.CharField(max_length=100, blank=True, null=True)
    card_status = models.CharField(max_length=100, blank=True, null=True)
    exist_software = models.CharField(max_length=100, null=True, blank=True, verbose_name="Existing Software")
    updated_software = models.CharField(max_length=100, null=True, blank=True, verbose_name="Updated Software")
    issue_identified = models.CharField(max_length=100, null=True, blank=True)
    issue_analysis = models.CharField(max_length=200,null=True, blank=True)
    issue_analysis_01 = models.CharField(max_length=200, null=True, blank=True)
    dealer_name = models.CharField(max_length=200, null=True, blank=True)
    call_closure_cat = models.CharField(max_length=100, null=True, blank=True, verbose_name="Call Closure Category")
    D1 = models.TextField(max_length=200, null=True, blank=True, verbose_name="D1 Comments")
    D1_closure_date = models.DateTimeField(null=True, blank=True, verbose_name="D1 Closure Date")
    D1_engineer = models.CharField(max_length=50, null=True, blank=True,verbose_name="D1 Engineer")
    D2 = models.TextField(max_length=200, null=True, blank=True, verbose_name="D2 Comments")
    D2_closure_date = models.DateTimeField(null=True, blank=True, verbose_name="D2 Closure Date")
    D2_engineer = models.CharField(max_length=50, null=True, blank=True, verbose_name="D2 Engineer")
    D2_exp_date = models.DateField(null=True, blank=True)
    D3_Engineer = models.CharField(max_length=50, null=True, blank=True, verbose_name="D3 Engineer")
    D3_exp_date = models.DateField(null=True, blank=True)
    D3_closure_date = models.DateTimeField(null=True, blank=True, verbose_name="D3 Closure Date")
    D3 = models.TextField(max_length=200, null=True, blank=True, verbose_name="D3 Comments")
    Latest_update=models.TextField(max_length=200, null=True, blank=True, verbose_name="Latest Update")
    D1_remark = models.TextField(max_length=200, null=True, blank=True)
    D2_remark = models.TextField(max_length=200, null=True, blank=True)
    D3_remark = models.TextField(max_length=200, null=True, blank=True)
    d1_d2_d3_ialert=models.CharField(max_length=50, null=True, blank=True,verbose_name="I Alert Remarks")

    remarks_in_ialert=models.TextField(max_length=204, null=True, blank=True, verbose_name="IAlert Comments")
    ialert_comments = models.TextField(blank=True, null=True)
    V_packet_3_months = models.TextField(max_length=100,null=True, blank=True,verbose_name="V Packet Last 3 Months")
    Latency_3_months = models.TextField(max_length=100,null=True, blank=True,verbose_name="Latency Last 3 Months")
    V_packet_7_days = models.TextField(max_length=100,null=True, blank=True,verbose_name="V Packet Last 7 Days")
    analysis = models.TextField(max_length=200, null=True, blank=True, verbose_name="Final Analysis")
    Latency_7_days = models.TextField(max_length=100,null=True, blank=True,verbose_name="Latency Last 7 Days")
    final_action_taken = models.TextField(max_length=204,null=True, blank=True,verbose_name="Final Action Taken")
    finalised_issue_category = models.CharField(max_length=100, null=True, blank=True, verbose_name="Finalised Issue Category")
    upload_file_01 = models.FileField(
        upload_to='uploads/',
        null=True,
        blank=True,
        verbose_name="Upload File"
    )
    call_status = models.CharField(
        max_length=50,
        choices=[
            ('Pending', 'Pending'),
            ('FIR-Resolved', 'FIR-Resolved'),
            ('Cancelled', 'Cancelled'),
            ('D1 Done','D1 Done'),
            ('D2 Done','D2 Done'),
            ('D3 Done','D3 Done'),
            ('Resolved', 'Resolved'),
            ('Closed', 'Closed'),
            ('Closed-CI', 'Closed-CI'),
            ('Reject', 'Reject'),
            ('Resale', 'Resale'),
            ('Hold', 'Hold'),
            ('D1-D2-D3 Completed', 'D1-D2-D3 Completed'),
            ('Auto Resolved', 'Auto Resolved'),
            ('FIR-For Approval', 'FIR-For Approval'),
            ('FIR-Repair', 'FIR-Repair'),
            ('FIR-Replace', 'FIR-Replace'),
            ('FIR-Replace_Repair', 'FIR-Replace_Repair'),
        ],
        blank=True,
        null=True
    )
    clean_call_status = models.CharField(max_length=50, blank=True, null=True)
    no_of_complaint_received = models.CharField(max_length=50, blank=True, null=True)
    engineer_recommendation = models.CharField(
        max_length=40,
        choices=[
            ('--', '--'),
            ('Repair', 'Repair'),
            ('Replace', 'Replace'),
            ('Replace_Repair', 'Replace_Repair')
        ],
        default='--',
        blank=True,
        null=True,
        verbose_name="Engineer Recommendation"
    )
    chargable_or_not=models.CharField(
        max_length=40,
        choices=[
            ('--', '--'),
            ('Yes', 'Yes'),
            ('No', 'No')
        ],
        default='--',
        blank=True,
        null=True,
        verbose_name="Chargable or Not"
    )
    manager_comments = models.TextField(null=True, blank=True,verbose_name="Issue Cateogry")
    issue_category =models.TextField(null=True, blank=True,verbose_name="Issue Cateogry")
    hod_comment = models.TextField(null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)
    date_of_closure = models.DateTimeField(null=True, blank=True)
    last_updated = models.DateTimeField(default=now, blank=True)  # Add this field
    confirmation = models.CharField(
        max_length=20,

        null=True,
        blank=True,
        verbose_name="Customer Confirmation"
    )
    feedback = models.CharField(
        max_length=20,

        null=True,
        blank=True,
        verbose_name="Customer Feedback"
    )
    rating = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Customer Rating"
    )
    customer_feedback = models.TextField(
        null=True,
        blank=True,
        verbose_name="Additional Feedback"
    )
    feedback_submitted_datetime=models.DateTimeField(null=True,blank=True)
    called_date=models.DateTimeField(null=True, blank=True,verbose_name="Actual Review Date")
    engineer_name=models.CharField(max_length=100, null=True, blank=True,verbose_name="Reviewed By")
    latency_for_last_7_days_cc=models.CharField(max_length=20, null=True, blank=True,verbose_name="Lat for Last 7 Days(After Close)")
    vpacket_for_last_7_days_cc=models.CharField(max_length=20, null=True, blank=True,verbose_name="VPak for Last 7 Days(After Close)")
    remarks_03=models.CharField(max_length=100, null=True, blank=True, verbose_name="Remarks")
    final_conclusion=models.TextField(max_length=100, null=True, blank=True)
    final_status=models.CharField(max_length=50, null=True, blank=True,choices=[('Closed','Closed'),('Pending','Pending')])
    call_closed_by = models.CharField(max_length=100, null=True, blank=True)
    exp_review_date = models.DateField(null=True, blank=True)
    customer_feedback_eng_review = models.TextField(null=True, blank=True, verbose_name="Customer Feedback")
    device_IMEI = models.CharField(max_length=15, blank=True, null=True)
    device_ICCID = models.CharField(max_length=20, blank=True, null=True)
    d1_tat = models.CharField(max_length=20, blank=True, null=True)
    d2_tat = models.CharField(max_length=20, blank=True, null=True)
    tat = models.CharField(max_length=20, blank=True, null=True)
    external_modification = models.TextField(blank=True, null=True)
    device_to_be_sent = models.CharField(max_length=50, blank=True, null=True,verbose_name="Faulty Device Sent to Location:")
    dealer_address = models.TextField(blank=True, null=True)
    engineer_name=models.CharField(max_length=100, null=True, blank=True)
    latency_for_last_7_days_cc=models.CharField(max_length=20, null=True, blank=True,verbose_name="Lat for Last 7 Days(After Close)")
    vpacket_for_last_7_days_cc=models.CharField(max_length=20, null=True, blank=True,verbose_name="VPak for Last 7 Days(After Close)")
    centralised_id = models.CharField(max_length=20, blank=True, null=True, unique=True)
    tat = models.TextField(null=True, blank=True)  # Ensure this is not a generated column
    D1_resp=models.TextField(null=True, blank=True)
    D2_resp=models.TextField(null=True, blank=True)
    D3_resp=models.TextField(null=True, blank=True)
    # New fields
    alt_device_working_status = models.CharField(
        max_length=50,
        choices=[
            ('A Packet & Latency Ok', 'A Packet & Latency Ok'),
            ('A Packet Ok', 'A Packet Ok'),
            ('Latency Ok', 'Latency Ok'),
            ('Not Working', 'Not Working')
        ],
        null=True, blank=True,
        verbose_name="ALT Device Working Status"
    )
    faulty_device_shipped_date = models.DateField(null=True, blank=True,verbose_name="Faulty Device Shipped Date")
    faulty_device_shipped_thru = models.CharField(max_length=100, null=True, blank=True,verbose_name="Faulty Device Shipped Thru")
    faulty_device_shipped_lr_details = models.CharField(max_length=100, null=True, blank=True,verbose_name="Faulty Device Shipped LR Details")
    faulty_device_reached_date = models.DateField(null=True, blank=True,verbose_name="Faulty Device Reached Date")
    faulty_device_confirmation_from_destination = models.CharField(max_length=100, null=True, blank=True,verbose_name="Faulty Device Confirmation from Destination")
    grn_no_for_faulty_device = models.CharField(max_length=100, null=True, blank=True, verbose_name="GRN No for Faulty Device")
    faulty_device_psn_number_fetch = models.CharField(max_length=100, null=True, blank=True,verbose_name="Faulty Device PSN Number Fetch")
    engineer_responsible_fetch = models.CharField(max_length=100, null=True, blank=True,verbose_name="Engineer Responsible Fetch")
    device_taken_for_repair = models.DateField(null=True, blank=True,verbose_name="Device Taken for Repair")
    device_reached_date = models.DateField(null=True, blank=True,verbose_name="Device Reached Date")
    device_repaired = models.DateField(null=True, blank=True,verbose_name="Device Repaired")
    copq_labour = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0.00, verbose_name="CoPQ Labour")
    copq_matl = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0.00, verbose_name="CoPQ Material")
    matls_used = models.CharField(
        max_length=10,
        choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')],
        null=True, blank=True,verbose_name="Materials Used"
    )
    device_shipped_to_location = models.CharField(max_length=100, null=True, blank=True,verbose_name="Device Shipped to Location")
    device_shipped_to_engineer = models.CharField(max_length=100, null=True, blank=True,verbose_name="Device Shipped to Engineer")
    sim_validity = models.DateField(null=True, blank=True,verbose_name="SIM Validity")
    device_shipped_date = models.DateField(null=True, blank=True,verbose_name="Device Shipped Date")
    device_shipped_through = models.CharField(max_length=100, null=True, blank=True,verbose_name="Device Shipped Through")
    device_delivered_to_customer = models.CharField(max_length=100, null=True, blank=True,verbose_name="Device Delivered to Customer")
    device_shipped_lr_no = models.CharField(max_length=100, null=True, blank=True, verbose_name="Device Shipped LR No")
    device_delivered_to_engineer = models.CharField(max_length=100, null=True, blank=True, verbose_name="Device Delivered to Engineer")
    device_fitted_by = models.CharField(max_length=100, null=True, blank=True, verbose_name="Device Fitted By")
    device_working_status = models.CharField(max_length=100, null=True, blank=True, verbose_name="Device Working Status",choices=[
            ('A Packet & Latency Ok', 'A Packet & Latency Ok'),
            ('A Packet Ok', 'A Packet Ok'),
            ('Latency Ok', 'Latency Ok'),
            ('Not Working', 'Not Working')
        ])
    device_reached_for_repair = models.DateField(null=True, blank=True, verbose_name="Device Reached for Repair")
    device_reached_after_repair = models.DateField(null=True, blank=True, verbose_name="Device Reached After Repair")
    acknowledge_date = models.DateField(null=True, blank=True, verbose_name="Acknowledge Date")
    grn_no_for_faulty_device = models.CharField(max_length=100, null=True, blank=True, verbose_name="GRN No for Faulty Device")
    payment_status = models.CharField(
        max_length=10,
        choices=[('--', '--'), ('Paid', 'Paid'), ('Not paid', 'Not paid')],
        blank=True,
        verbose_name="Payment Status"
    )
    # Add missing fields
    alt_device_fitted_date = models.DateField(null=True, blank=True,verbose_name="ALT Device Fitted Date")
    alt_device_psn = models.CharField(max_length=100, null=True, blank=True,verbose_name="ALT Device PSN")
    validity_of_old_device = models.DateField(null=True, blank=True, verbose_name="Validity of Old Device")
    alt_device_sent_to_customer_from_location = models.CharField(max_length=100, null=True, blank=True, verbose_name="ALT Device Sent From Location")
    alt_device_sent_by = models.CharField(max_length=100, null=True, blank=True,        choices=[('--', '--'), ('Arun Maity', 'Arun Maity'), ('Arun G', 'Arun G'),('Eliyas', 'Eliyas'), ('Gayadhar', 'Gayadhar'), ('Kunal', 'Kunal'),('Rishwanth', 'Rishwanth'), ('Siva', 'Siva'), ('Swamy', 'Swamy')],
 verbose_name="ALT Device Sent By")
    date_of_alt_device_delivered_to_customer = models.DateField(null=True, blank=True, verbose_name="Date of ALT Device Delivered to Customer")
    alt_device_fitted_by = models.CharField(max_length=100, null=True, blank=True, verbose_name="ALT Device Fitted By")
    faulty_device_psn_number = models.CharField(max_length=100, null=True, blank=True, verbose_name="Faulty Device PSN Number")
    validity_from_old_to_new_yes_done_by = models.CharField(max_length=100, null=True, blank=True, verbose_name="Validity from Old to New Yes Done By")
    alt_device_shipped_lr_no = models.CharField(max_length=100, null=True, blank=True, verbose_name="ALT Device Shipped LR No")
    alt_device_mapping_completion_date = models.DateField(null=True, blank=True, verbose_name="ALT Device Mapping Completion Date")
    alt_device_shipped_through = models.CharField(max_length=100, null=True, blank=True, verbose_name="ALT Device Shipped Through")
    alt_device_shipped_date = models.DateField(null=True, blank=True, verbose_name="ALT Device Shipped Date")
    validity_of_alt_device = models.DateField(null=True, blank=True, verbose_name="Validity of ALT Device")
    engineer_responsible = models.CharField(max_length=100, null=True, blank=True,verbose_name="Engineer Responsible")
    validity_transfer_from_old_device = models.CharField(max_length=100, null=True, blank=True, choices=[('Yes', 'Yes'), ('No', 'No')],verbose_name="Validity Transfer from Old Device")
    updated_validity_of_alt_device = models.DateField(null=True, blank=True, verbose_name="Updated Validity of ALT Device")
    SIM_STATUS_CHOICES = [
        ('Commercial Active', 'Commercial Active'),
        ('Bootstrap Active', 'Bootstrap Active'),
        ('Others', 'Others'),
    ]
    al_dev_sim_status = models.CharField(max_length=20,
        choices=SIM_STATUS_CHOICES,
        null=True,
        blank=True,
        verbose_name="Alt Device SIM Status")
    alt_device_validity_status = models.DateField(null=True, blank=True, verbose_name="ALT Device Validity Status")
    old_device_sent_to_location = models.CharField(max_length=100, null=True, blank=True,verbose_name="Faulty Device Sent to Location")
    plant_analysis = models.TextField(null=True, blank=True, verbose_name="Plant Analysis")
    plant_conclusion = models.TextField(null=True, blank=True, verbose_name="Plant Conclusion")
    def save(self, *args, **kwargs):

        if self.complaint_raised_from_location:
            self.complaint_raised_from_location = self.complaint_raised_from_location.upper()

        # Generate unique ID only if it doesn't exist
        if not self.unique_id:
            current_year = now().strftime('%y')  # Get the last two digits of the year
            current_month = now().strftime('%m')  # Get the two-digit month
            last_entry = DirectCall.objects.filter(unique_id__startswith=f"DTILDC-{current_year}{current_month}").order_by('-unique_id').first()
            if last_entry:
                last_unique_number = int(last_entry.unique_id[-4:])  # Extract the last 4 digits
                unique_number = f"{last_unique_number + 1:04d}"  # Increment the last 4 digits
            else:
                unique_number = "1073"  # Start from 1025 if no entries exist for this month

            generated_unique_id = f"DTILDC-{current_year}{current_month}{unique_number}"

            while DirectCall.objects.filter(unique_id=generated_unique_id).exists():
                unique_number = f"{int(unique_number) + 1:04d}"  # Increment the number
                generated_unique_id = f"DTILDC-{current_year}{current_month}{unique_number}"
            self.unique_id = generated_unique_id
        super().save(*args, **kwargs)
    def __str__(self):
        return f"Complaint by {self.complaint_raised_by} - VIN: {self.vin} (ID: {self.unique_id})"

class MappingProcess(models.Model):
    unique_id = models.CharField(max_length=20, unique=True, blank=True, null=True)  # Unique ID field








