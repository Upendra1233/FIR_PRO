from django.contrib import admin
from .models import DataRecord

@admin.register(DataRecord)
class DataRecordAdmin(admin.ModelAdmin):
    list_display = ('vin',)
