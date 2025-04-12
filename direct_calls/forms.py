from django import forms
from django.core.validators import RegexValidator
from .models import DirectCall

class DirectCallForm(forms.ModelForm):
    class Meta:
        model = DirectCall 
        fields = '__all__'  # Include all fields, including `submitted_to_email` and `upload_file_01`
        widgets = {
            'date_of_complaint': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'date_of_sale_of_device': forms.DateInput(attrs={'type': 'date'}),
            'vehicle_sale_date': forms.DateInput(attrs={'type': 'date'}),
            'customer_raised_issue': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter customer voice'}),  # Changed to TextInput
            'first_communication_in_darby': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'last_communication_in_darby': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'final_action_taken': forms.Textarea(attrs={'rows': 1, 'class': 'form-control'}),
            'date_of_closure': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date_of_complaint'].widget.attrs['readonly'] = True

class ManagerForm(forms.ModelForm):
    contact_number = forms.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message="Contact number must be exactly 10 digits."
            )
        ],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter 10-digit contact number'})
    )

    class Meta:
        model = DirectCall
        fields = [
            'date_of_complaint', 'complaint_raised_from_location', 'customer_raised_issue', 'complaint_raised',
            'complaint_raised_by', 'contact_number', 'customer_mail_id', 'complaint_raised_through',
            'complaint_received_by', 'vin','psn', 'complaint_assigned_to', 'submitted_to_email',
            'engineer_contact_number', 'upload_file','call_type', 'ticket_no'
        ]
        widgets = {
            'date_of_complaint': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'},
                format='%Y-%m-%dT%H:%M'  # Match the browser's datetime-local format
            ),
            'customer_raised_issue': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter customer voice'}),  # Changed to TextInput
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date_of_complaint'].input_formats = ['%Y-%m-%dT%H:%M']  # Accept browser format

class EngineerForm(forms.ModelForm):
    class Meta:
        model = DirectCall
        fields = [
            'psn',  # Include the psn field
            'region',
            'vehicle_type',
            'vehicle_running_location',
            'state',
            'device_model',
            'telco_status',
            'active_profile',
            'activation_start_date',
            'activation_end_date',
            'vehicle_sale_date',
            'first_communication_in_darby',
            'last_communication_in_darby',
            'vehicle_run',
            'kilometers_hours',
            'main_battery_voltage',
            'issue_identified',
            'issue_analysis',
            'final_action_taken',
            'call_status',
            'date_of_closure',
            'contact_person_name',
            'contact_person_number',
            'contact_category',
            'exist_software',
            'updated_software',
            'finalised_issue_category',
            'upload_file_01',
            'call_status',
            'hod_comment',
            'date_of_closure'
        ]
        widgets = {
            'psn': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter PSN'}),
            'region': forms.Select(attrs={'class': 'form-control'}),
            'vehicle_type': forms.Select(attrs={'class': 'form-control'}),
            'vehicle_running_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Vehicle Running Location'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter State'}),
            'device_model': forms.Select(attrs={'class': 'form-control'}),
            'date_of_sale_of_device': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'telco_status': forms.Select(attrs={'class': 'form-control'}),
            'active_profile': forms.Select(attrs={'class': 'form-control'}),
            'activation_start_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'activation_end_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'vehicle_sale_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'first_communication_in_darby': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'last_communication_in_darby': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'vehicle_run': forms.Select(attrs={'class': 'form-control'}),
            'kilometers_hours': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Kilometers/Hours'}),
            'main_battery_voltage': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Main Battery Voltage'}),
            'issue_identified': forms.Select(attrs={'class': 'form-control'}),
            'issue_analysis': forms.Select(attrs={'class': 'form-control'}),
            'final_action_taken': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Final Action Taken', 'rows': 1}),
            'call_status': forms.Select(attrs={'class': 'form-control'}),
            'date_of_closure': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'contact_person_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Contact Person Name'}),
            'contact_person_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Contact Person Number'}),
            'contact_category': forms.Select(attrs={'class': 'form-control'}),
            'exist_software': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Existing Software'}),
            'updated_software': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Updated Software'}),
            'finalised_issue_category': forms.Select(attrs={'class': 'form-control'}),
            'upload_file_01': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }