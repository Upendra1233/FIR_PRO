from django.contrib import admin
from .models import AIS140Request
from django.utils.timezone import localtime
    
@admin.register(AIS140Request)
class AIS140RequestAdmin(admin.ModelAdmin):
    list_display = [
        # Remove 'date_of_request' from the list
        'customer_name', 'customer_phone', 'dealer_name', 'assigned_to',
    ]

    list_filter = ('completion_status', 'state')
    search_fields = ('customer_name', 'vehicle_no', 'vin_no')











