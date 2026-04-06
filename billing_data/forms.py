from django import forms
from .models import BillingData, OrderDetail

class BillingDataForm(forms.ModelForm):
    class Meta:
        model = BillingData
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['invoice_value_without_gst'].widget.attrs['readonly'] = True

class OrderDetailForm(forms.ModelForm):
    class Meta:
        model = OrderDetail
        fields = '__all__'