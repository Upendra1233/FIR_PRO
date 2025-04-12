from django import forms
from .models import SRRequest, SRDetails
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class SRRequestForm(forms.ModelForm):
    class Meta:
        model = SRRequest
        exclude = ['unique_id']  # Exclude unique_id from the form
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'existing_validity': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'requestor_validity_start_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'requestor_validity_end_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'requestor_comments': forms.Textarea(attrs={'rows': 1, 'class': 'form-control', 'placeholder': 'Enter your comments'}),
            'sim_status_during_request': forms.Textarea(attrs={'rows': 1, 'class': 'form-control', 'placeholder': 'SIM status during request'}),
            'remarks': forms.Textarea(attrs={'rows': 1, 'class': 'form-control', 'placeholder': 'Enter remarks'}),
            'hod_remarks': forms.Textarea(attrs={'rows': 1, 'class': 'form-control', 'placeholder': 'Enter HOD remarks'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'billing_to': forms.Select(attrs={'class': 'form-control'}),
            'plan': forms.Select(attrs={'class': 'form-control'}),
            'engineer': forms.Select(attrs={'class': 'form-control'}),
            'psn': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter PSN'}),
            'icicid': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter ICICID'}),
            'new_sr_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter New SR No'}),
            'sr_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'sr_success_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'engineer_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter Engineer Email'}),
            'old_psn': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Old PSN'}),  # Old PSN
            'old_iccid': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Old ICCID'}),  # Old ICCID
            'old_sim_status': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Old Sim Status', 'rows': 1}),  # Old Sim Status
            'old_validity': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),  # Old Validity
        }

    def __init__(self, *args, **kwargs):
        super(SRRequestForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False  # Make all fields optional
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Submit'))

class SRDetailsForm(forms.ModelForm):
    class Meta:
        model = SRRequest
        fields = ['new_sr_no', 'sr_date', 'sr_success_date', 'status']
        widgets = {
            'new_sr_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter New SR No'}),
            'sr_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'sr_success_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

class NewSRDetailsForm(forms.ModelForm):
    class Meta:
        model = SRRequest
        fields = ['new_sr_no', 'sr_date', 'sr_success_date', 'status']
        widgets = {
            'new_sr_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter New SR No'}),
            'sr_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'sr_success_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }