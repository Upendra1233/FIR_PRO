from django import forms
from .models import BillVerify
from django.forms import NumberInput, DateInput

CUSTOMER_CHOICES = [
    ("AL M&HCV", "AL M&HCV"),
    ("ALEV", "ALEV"),
    ("ALGS", "ALGS"),
    ("AL LCV", "AL LCV"),
    ("DTIL ENGG-DL548", "DTIL ENGG-DL548"),
    ("DTIL SERVICE-DL548", "DTIL SERVICE-DL548"),
    ("SENSORISE-DL548", "SENSORISE-DL548"),
    ("SENSORISE LCV GS", "SENSORISE LCV GS"),
    ("DTIL ENGG-LCV, GS", "DTIL ENGG-LCV, GS"),
    ("DTIL SERVICE -LCV, GS ", "DTIL SERVICE -LCV, GS "),
    ("PD","PD"),
    ("Switch","Switch")
]

PROFILE_CHOICES = [
    ("AIR TEL", "AIR TEL"),
    ("BSNL", "BSNL"),
    ("DUAL", "DUAL"),
    ("INTL", "INTL"),
    ("Airtel - 5G", "Airtel - 5G"),
    ("Terminated","Terminated"),
    ("Suspended","Suspended"),
    ("AIS140", "AIS140"),
    ("Top - UP", "Top - UP"),
    ("S - D","S - D"),
    ("D - S","D - S"),
    ("BS Extension","BS Extension"),
    ("OTCRSU - 1", "OTCRSU - 1"),
    ("OTCRSU - 3", "OTCRSU - 3"),
    ("Safe Custody","Safe Custody"),
    ("S-D Up Front","S-D Up Front")
]



BILL_YEAR_CHOICES = [
    ("2024-25", "2024-25"),
    ("2025-26", "2025-26"),
    ("2026-27", "2026-27"),
]

class BillVerifyForm(forms.ModelForm):
    customer_name = forms.ChoiceField(
        choices=[("", "Select Customer")] + CUSTOMER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'customer_name'})
    )
    profile_type = forms.ChoiceField(
        choices=[("", "Select Profile")] + PROFILE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'profile_type'})
    )

    bill_year = forms.ChoiceField(
        choices=[("", "Select Billing Year")] + BILL_YEAR_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'bill_year'})
    )

    class Meta:
        model = BillVerify
        fields = '__all__'
        widgets = {
            'unique_id': forms.TextInput(attrs={'readonly': 'readonly'}),
            'customer_price': NumberInput(attrs={'class': 'form-control', 'id': 'customer_price'}),
            'DTIL_price': DateInput(attrs={'class': 'form-control','type': 'date', 'id': 'DTIL_price'}),
            'start_month': DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'start_month'}),
            'end_month': DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'end_month'}),
            'invoice_date': forms.TextInput(attrs={'class': 'form-control', 'id': 'invoice_date'}),
            'invoice_number': forms.TextInput(attrs={'class': 'form-control', 'id': 'invoice_number'}),
            'invoice_qty': forms.TextInput(attrs={'class': 'form-control', 'id': 'invoice_qty'}),
            'tenure': forms.NumberInput(attrs={'class': 'form-control', 'id': 'tenure'}),
            'po_no' : forms.TextInput(attrs={'class': 'form-control', 'id': 'po_no'}),
            'po_date' :  DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'po_date'}),
            'service_activity' : forms.TextInput(attrs={'class': 'form-control', 'id': 'service_activity'}),
            'billed_for' : forms.TextInput(attrs={'class': 'form-control', 'id': 'billed_for'}),

            'service_line' : forms.TextInput(attrs={'class': 'form-control', 'id': 'service_line'}),
            'service_qty' : forms.NumberInput(attrs={'class': 'form-control', 'id': 'service_qty'}),
            'total_po_qty' : forms.NumberInput(attrs={'class': 'form-control', 'id': 'total_po_qty', 'disabled': True,}),
            'unique_id': forms.TextInput(attrs={'class': 'form-control', 'id': 'unique_id'}),
            'total_balance_qty': forms.NumberInput(attrs={'class': 'form-control', 'id': 'total_balance_qty', 'disabled': True}),
            'final_po': forms.TextInput(attrs={'class': 'form-control', 'id': 'final_po'}),
            'sr_month':DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'sr_month'}),
            'validity_date':DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'validity_date'}),
        }
