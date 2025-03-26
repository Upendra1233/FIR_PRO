from django.contrib import admin
from .models import MappingProcess

@admin.register(MappingProcess)
class MappingProcessAdmin(admin.ModelAdmin):
    list_display = ('id', 'old_psn', 'new_psn', 'mapping_req_received_date', 'mapping_completion_date')
    search_fields = ('old_psn', 'new_psn', 'vin')
