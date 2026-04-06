from django.contrib import admin
from .models import BillVerify
from django.utils.timezone import localtime

@admin.register(BillVerify)
# Register your models here.
class BillVerifyAdmin(admin.ModelAdmin):
    list_display = [
        'customer_name', 'profile_type', 'customer_price', 'DTIL_price', 'tenure',
        'bill_year', 'start_month', 'end_month', 'invoice_number', 'invoice_date', 'invoice_qty'
    ]
    list_filter = ('profile_type', 'bill_year')
    search_fields = ('customer_name', 'invoice_number')