from django import forms
from .models import LeaveRequest

class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['engineer', 'request_date', 'category', 'date_of_leave', 'manager', 'approved_by', 'remarks']
        widgets = {
            'request_date': forms.DateInput(attrs={'type': 'date'}),
            'date_of_leave': forms.DateInput(attrs={'type': 'date'}),
        }








