from django.contrib import admin
from .models import BillingData

@admin.register(BillingData)
class BillingDataAdmin(admin.ModelAdmin):
    list_display = ('invoice_no', 'invoice_date', 'product', 'qty')
    readonly_fields = ('invoice_value_without_gst',)
