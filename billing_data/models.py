from django.db import models

class BillingData(models.Model):
    invoice_no = models.CharField(max_length=50, null=True, blank=True)
    invoice_date = models.DateField(null=True, blank=True)
    product = models.CharField(max_length=100, null=True, blank=True)
    qty = models.IntegerField(null=True, blank=True)
    part_sub_category = models.CharField(max_length=100, null=True, blank=True)
    item_sub_category = models.CharField(max_length=100, null=True, blank=True)
    part_no = models.CharField(max_length=100, null=True, blank=True)
    customer_name = models.CharField(max_length=100, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    invoice_value_without_gst = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    total_invoice_value_with_gst = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    credited_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, null=True, blank=True)
    tds_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, null=True, blank=True)
    gap = models.DecimalField(max_digits=15, decimal_places=2, default=0, null=True, blank=True)
    theoretical_payment_due_date = models.DateField(null=True, blank=True)
    grn_no = models.CharField(max_length=100, null=True, blank=True)
    actual_grn_delivery_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    payment_status = models.CharField(max_length=100, null=True, blank=True)
    received_date = models.DateField(null=True, blank=True)
    transporter_name = models.CharField(max_length=100, null=True, blank=True)
    docket_no = models.CharField(max_length=100, null=True, blank=True)
    date_of_shipment = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.invoice_no
