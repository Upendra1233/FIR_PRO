from django import forms
from .models import MappingProcess

class MappingProcessForm(forms.ModelForm):
    class Meta:
        model = MappingProcess
        fields = '__all__'
        widgets = {
            'mapping_req_received_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'date_of_old_device_sales': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'first_s_activation_of_old_device': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'first_c_activation_of_old_device': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'old_device_validity': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'current_validity_status_of_new_device': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'mapping_completion_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'warranty_of_the_device': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'added_validity_for_new_device': forms.Textarea(attrs={'rows': 1, 'class': 'form-control'}),
            'hod_remarks': forms.Textarea(attrs={'rows': 1, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(MappingProcessForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False  # Make all fields optional

    def clean(self):
        cleaned_data = super().clean()

        # Handle "Others" logic for dropdowns
        if cleaned_data.get('current_card_status_of_new_device') == 'Others' and not cleaned_data.get('current_card_status_of_new_device_other'):
            self.add_error('current_card_status_of_new_device_other', 'This field is required when "Others" is selected.')

        if cleaned_data.get('activation_status_of_new_device') == 'Others' and not cleaned_data.get('activation_status_of_new_device_other'):
            self.add_error('activation_status_of_new_device_other', 'This field is required when "Others" is selected.')

        return cleaned_data