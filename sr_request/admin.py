# filepath: c:\Users\Admin\Desktop\FIR_PRO\sr_request\admin.py
from django.contrib import admin
from .models import SRRequest

class SRRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'engineer', 'category', 'psn', 'icicid', 'plan')  # Ensure 'engineer' is correct
    search_fields = ('engineer', 'category', 'psn', 'icicid')  # Add search functionality
    list_filter = ('category', 'plan', 'billing_to')  # Add filters for better usability

admin.site.register(SRRequest, SRRequestAdmin)
