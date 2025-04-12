from django.contrib import admin
from .models import DirectCall

@admin.register(DirectCall)
class DirectCallAdmin(admin.ModelAdmin):
    list_display = [
        'date_of_complaint',  # Replace 'complaint_raised_name' with valid fields
        'complaint_raised_by',
        'vin',
        'call_status',
        'date_of_closure'
    ]
    search_fields = ['vin', 'psn', 'complaint_raised_by']






