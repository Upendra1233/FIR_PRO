from django import forms
from .models import BillingData

class BillingDataForm(forms.ModelForm):
    class Meta:
        model = BillingData
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.required = False  # Ensure the field is not required
            if hasattr(field.widget, 'attrs'):
                field.widget.attrs.pop('required', None)  # Remove 'required' attribute from HTML