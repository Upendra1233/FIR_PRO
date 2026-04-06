from django import forms
from .models import DataRecord

class DataRecordForm(forms.ModelForm):
    class Meta:
        model = DataRecord
        fields = ['vin']