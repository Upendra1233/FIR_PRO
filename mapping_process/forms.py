from django import forms
from .models import MappingProcess

class MappingProcessForm(forms.ModelForm):
    class Meta:
        model = MappingProcess
        fields = '__all__'  # Include all fields from the model

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

        # Example: Ensure `req_raised_by` is not empty
        req_raised_by = cleaned_data.get('req_raised_by')
        if not req_raised_by:
            self.add_error('req_raised_by', 'This field is required.')

        return cleaned_data

MappingProcess.objects.all()