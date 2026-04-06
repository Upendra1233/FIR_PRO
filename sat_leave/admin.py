from django.contrib import admin
from .models import LeaveRequest

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('engineer', 'request_date', 'category', 'date_of_leave', 'manager', 'action')
    list_filter = ('action', 'manager', 'category')
    search_fields = ('engineer', 'manager', 'category')