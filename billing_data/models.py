from django.db import models
from decimal import Decimal
from django.utils.timezone import now

class BillingData(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Received', 'Received'),
    ]
    unique_id = models.CharField(max_length=30, unique=True, null=True, blank=True) 
    invoice_no = models.CharField(max_length=50, null=True, blank=True)
    invoice_date = models.DateField(null=True, blank=True)
    product = models.CharField(max_length=100, null=True, blank=True)
    qty = models.IntegerField(null=True, blank=True)
    category = models.CharField(max_length=100, null=True, blank=True)
    part_sub_category = models.CharField(max_length=100, null=True, blank=True)
    item_sub_category = models.CharField(max_length=100, null=True, blank=True)
    part_no = models.CharField(max_length=100, null=True, blank=True)
    customer_name = models.CharField(max_length=100, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    invoice_value_without_gst = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    total_invoice_value_with_gst = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    credited_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, null=True, blank=True)
    tds_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, null=True, blank=True)
    gap = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, null=True, blank=True)
    theoretical_payment_due_date = models.DateField(null=True, blank=True)
    grn_no = models.CharField(max_length=100, null=True, blank=True)
    actual_grn_delivery_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    payment_status = models.CharField(max_length=100, choices=PAYMENT_STATUS_CHOICES, null=True, blank=True)
    received_date = models.DateField(null=True, blank=True)
    transporter_name = models.CharField(max_length=100, null=True, blank=True)
    docket_no = models.CharField(max_length=100, null=True, blank=True)
    date_of_shipment = models.DateField(null=True, blank=True)
    due_emails = models.TextField(blank=True, null=True)
    shipment_emails = models.TextField(blank=True, null=True)    
    group_name = models.CharField(max_length=100, null=True, blank=True)
    category = models.CharField(max_length=100, null=True, blank=True)
    po_no = models.CharField(max_length=100, null=True, blank=True)
    po_date = models.DateField(null=True, blank=True)
    vendor_code = models.CharField(max_length=100, null=True, blank=True)
    customer_code = models.CharField(max_length=100, null=True, blank=True)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    gst = models.CharField(max_length=10, null=True, blank=True)
    freight_scope = models.CharField(max_length=100, null=True, blank=True)
    freight_scope_value = models.CharField(max_length=100, null=True, blank=True)
    contact_person_name = models.CharField(max_length=100, null=True, blank=True)
    contact_details = models.CharField(max_length=100, null=True, blank=True)
    contact_mail_id = models.EmailField(null=True, blank=True)
    engineer = models.CharField(max_length=100, null=True, blank=True)
    order = models.ForeignKey('OrderDetail', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.invoice_no if self.invoice_no else "No Invoice Number"

    def get_email_mapping(self):
        # (customer_name, location): (due_emails, shipment_emails)
        email_map = {
            ("Switch", "Chennai"): (
                "Lakshmanan.p@switchmobilityev.co ;karthikpandy.p@switchmobilityev.co",
                "Lakshmanan.p@switchmobilityev.co ;karthikpandy.p@switchmobilityev.co"
            ),
            ("Switch", "Hosur"): (
                "Lakshmanan.p@switchmobilityev.co ;karthikpandy.p@switchmobilityev.co",
                "Lakshmanan.p@switchmobilityev.co ;karthikpandy.p@switchmobilityev.co"
            ),
            ("Surin", "Chennai"): (
                "accounts2.chennai@surinauto.co ; purchase3.chennai@surinauto.co ; accounts2.pkm@surinauto.co ;",
                "purchase3.chennai@surinauto.co ;"
            ),
            ("Surin", "Pant Nagar"): (
                "accounts4.utk@surinauto.co ; prakash.kandpal@surinauto.co ; dheeresh@surinauto.co ; gayadharm@danlawtech.co",
                "prakash.kandpal@surinauto.co ; gayadharm@danlawtech.co"
            ),
            ("Prabha", "Chennai"): (
                "munusamy.s@prabhaengineers.co; ganesh.r@prabhaengineers.co",
                "munusamy.s@prabhaengineers.co; srikanth.n@prabhaengineers.co"
            ),
            ("Prabha", "Hosur"): (
                "balamurugan@prabhaengineers.co; sankar.s@prabhaengineers.co; eliyasp@danlawtech.co",
                "balamurugan@prabhaengineers.co; eliyasp@danlawtech.co"
            ),
            ("Prabha", "Pant Nagar"): (
                "jeevan.singh@prabhaengineers.co; ankit@prabhaengineers.co ; gayadharm@danlawtech.co",
                "ankit@prabhaengineers.co ; gayadharm@danlawtech.co"
            ),
            ("NeelMetal", "Pant Nagar"): (
                "dinesh.satyawali@jbmgroup.co ; manoj.joshi@jbmgroup.co; gayadharm@danlawtech.co",
                "janam.singh@jbmgroup.co ; n10b.purchase@jbmgroup.co ; gayadharm@danlawtech.co"
            ),
            ("Motherson", "Chennai"): (
                "balagopal.mathivanan@motherson.co ; varadarajan.narayanan@motherson.co",
                "varadarajan.narayanan@motherson.co"
            ),
            ("SMS", "Chennai"): (
                "sales@smsautoline.in",
                "sales@smsautoline.in"
            ),
        }
        key = (self.customer_name, self.location)
        return email_map.get(key, ("", ""))

    def save(self, *args, **kwargs):
        # Unique ID logic (keep your existing code)
        if not self.unique_id:
            current_year = now().strftime('%y')
            current_month = now().strftime('%m')
            last_entry = BillingData.objects.filter(
                unique_id__startswith=f"DTILBL-{current_year}{current_month}"
            ).order_by('-unique_id').first()
            if last_entry and last_entry.unique_id[-4:].isdigit():
                last_unique_number = int(last_entry.unique_id[-4:])
                unique_number = f"{last_unique_number + 1:04d}"
            else:
                unique_number = "1001"
            generated_unique_id = f"DTILBL-{current_year}{current_month}{unique_number}"
            while BillingData.objects.filter(unique_id=generated_unique_id).exists():
                unique_number = f"{int(unique_number) + 1:04d}"
                generated_unique_id = f"DTILBL-{current_year}{current_month}{unique_number}"
            self.unique_id = generated_unique_id

        # Auto-populate due_emails and shipment_emails if not set
        if not self.due_emails or not self.shipment_emails:
            due_emails, shipment_emails = self.get_email_mapping()
            if not self.due_emails:
                self.due_emails = due_emails
            if not self.shipment_emails:
                self.shipment_emails = shipment_emails

        super().save(*args, **kwargs)




class OrderDetail(models.Model):
    group_name = models.CharField(max_length=100)  # <-- changed from 'group'
    item_sub_category = models.CharField(max_length=100)
    part_sub_category = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    part_no = models.CharField(max_length=100)
    po_no = models.CharField(max_length=100)
    po_date = models.DateField()       
    customer_name = models.CharField(max_length=100) 
    location = models.CharField(max_length=100)
    vendor_code = models.CharField(max_length=100)
    customer_code = models.CharField(max_length=100)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    gst = models.CharField(max_length=10)
    freight_scope = models.CharField(max_length=100)
    freight_scope_value = models.CharField(max_length=100)
    transporter_name = models.CharField(max_length=100)
    contact_person_name = models.CharField(max_length=100)
    contact_details = models.CharField(max_length=100)
    contact_mail_id = models.EmailField()
    engineer = models.CharField(max_length=100)
    def __str__(self):
        return f"{self.po_no} - {self.customer_name}"