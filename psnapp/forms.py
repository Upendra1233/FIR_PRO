# filepath: psnapp/forms.py
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from .models import PSNEntry
import re

class PSNEntryForm(forms.ModelForm):
    class Meta:
        model = PSNEntry
        fields = '__all__'
        widgets = {
            'date_of_complaint': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'date_of_sale_of_device': forms.DateInput(attrs={'type': 'date'}),
            'vehicle_sale_date': forms.DateInput(attrs={'type': 'date'}),
            's_trigger_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'c_trigger_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'commercial_expiry_date': forms.DateInput(attrs={'type': 'date'}),
            'first_communication_in_darby': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'last_communication_in_darby': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'vehicle_support_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'date_of_closure': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'vehicle_type': forms.Select(attrs={'class': 'form-control select2'}),
            'issue_description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description...', 'rows': 1, 'cols': 5}),
            'manager_remarks': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Manager Remarks...', 'rows': 1, 'cols': 5}),
            'hod_remarks': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'HOD Remarks...', 'rows': 1, 'cols': 5}),
            'final_action_taken': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Final Action...', 'rows': 1, 'cols': 5}),
            'customer_raised_issue':forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Issue...', 'rows': 1, 'cols': 5}),
        }

    def __init__(self, *args, **kwargs):
        super(PSNEntryForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Submit'))
        for field in self.fields.values():
            field.required = False

    def clean_firmware(self):
        firmware = self.cleaned_data.get('firmware')
        if firmware:
            return firmware.upper()
        return firmware

    def clean_device_imei(self):
        device_imei = self.cleaned_data.get('device_IMEI')
        if device_imei and (not str(device_imei).isdigit() or len(str(device_imei)) != 15):
            raise forms.ValidationError("IMEI must be exactly 15 digits.")
        return device_imei

    def clean_device_iccid(self):
        device_iccid = self.cleaned_data.get('device_ICCID')
        if device_iccid and (not str(device_iccid).isdigit() or len(str(device_iccid)) == 20):
            raise forms.ValidationError("ICCID must be exactly 20 digits.")
        return device_iccid

    def clean_vehicle_running_location(self):
        vehicle_running_location = self.cleaned_data.get('vehicle_running_location')
        # Updated regex to allow spaces
        if vehicle_running_location and not re.match(r'^[A-Z0-9!@#$%^&*()_+=\- ]*$', vehicle_running_location):
            raise forms.ValidationError("Vehicle Running Location must contain only capital letters, special characters, numbers, and spaces.")
        return vehicle_running_location

    def clean_contact_number(self):
        contact_number = self.cleaned_data.get('contact_number')
        if contact_number and (not contact_number.isdigit() or len(contact_number) != 10):
            raise forms.ValidationError("Contact number must be exactly 10 digits.")
        return contact_number

    def clean_device_psn(self):
        device_psn = self.cleaned_data.get('device_PSN')
        if device_psn and len(device_psn) != 10:
            raise forms.ValidationError("Device PSN must be exactly 10 characters.")
        return device_psn

    def clean(self):
        cleaned_data = super().clean()
        complaint_raised_through = cleaned_data.get('complaint_raised_through')
        complaint_raised_through_other = self.data.get('complaint_raised_through_other')  # Get the raw data
        service_engineer_name = cleaned_data.get('service_engineer_name')
        service_engineer_name_other = self.data.get('service_engineer_name_other')  # Get raw data

        # Handle "Complaint Raised Through"
        if complaint_raised_through == 'others' and complaint_raised_through_other:
            cleaned_data['complaint_raised_through'] = complaint_raised_through_other

        # Handle "Service Engineer Name"
        if service_engineer_name == 'others' and service_engineer_name_other:
            cleaned_data['service_engineer_name'] = service_engineer_name_other

        fields_with_others = [
            'device_model',
            'configuration',
            'telco_status',
            'active_profile',
            'vehicle_type',
            'vehicle_run',
            'issue_identified',
            'issue_analysis',
            'device_to_be_sent'
        ]

        for field in fields_with_others:
            dropdown_value = cleaned_data.get(field)
            other_value = self.data.get(f'{field}_other')  # Get raw data from the request

            if dropdown_value == 'others' and other_value:
                # Replace the dropdown value with the custom value
                cleaned_data[field] = other_value

        external_modification = cleaned_data.get('external_modification')
        external_modification_other = self.data.get('external_modification_other')  # Get raw data

        if external_modification and 'Others' in external_modification and external_modification_other:
            # Append the custom value to the external_modification list
            external_modification.append(external_modification_other)
            cleaned_data['external_modification'] = external_modification

        return cleaned_data

class EngineerResponseForm(forms.ModelForm):
    class Meta:
        model = PSNEntry
        fields = '__all__'
