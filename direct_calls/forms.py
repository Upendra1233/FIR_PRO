from django import forms
from django.core.validators import RegexValidator, MaxLengthValidator
from django.core.exceptions import ValidationError
from .models import DirectCall
import re

# new: max char liit and mixin to enforce it server-side + addmaxlength attrs client-side
# Default maxlength and per-field overrides
DEFAULT_MAX = 200
FIELD_MAX = {
    # fields allowed up to 200 chars
    'issue_analysis_01': 200,
    'final_action_taken': 200,
    'remarks_in_ialert': 200,
    'D1':200,
    'D2':200,
    'D3':200,
}

MAX_FIELDS = (
    'D1', 'D2', 'D3', 'ialert_comments',
    'hod_comment', 'remarks', 'remarks_03', 'final_conclusion',
    'customer_feedback_eng_review', 'final_action_taken', 'issue_identified','issue_category','dealer_name',
    'issue_analysis', 'issue_analysis_01', 'remarks_in_ialert',
    'ialert_comments', 'Latency_7_days', 'V_packet_7_days',
    'Latency_3_months', 'V_packet_3_months', 'analysis', 'external_modification',
)
class MaxLengthFormMixin:
    """
    Adds client-side maxlength + stronger JS to prevent typing/pasting beyond MAX_CHARS
    and enforces server-side length with validators. Also ensures textarea rows=1.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fname in MAX_FIELDS:
            if fname in self.fields:
                field = self.fields[fname]
                widget = field.widget
                max_val = FIELD_MAX.get(fname, DEFAULT_MAX)
                max_s = str(max_val)

                # Ensure server-side MaxLengthValidator is present (guard against duplicate addition)
                has_max_validator = any(
                    getattr(v, 'limit_value', None) == max_val for v in field.validators
                )
                if not has_max_validator:
                    field.validators.append(MaxLengthValidator(max_val))

                # HTML maxlength (browser support) + data attr for extra JS checks
                widget.attrs['maxlength'] = max_s
                widget.attrs['data-maxlength'] = max_s

                # If widget is a textarea, force rows=1 for consistent display
                if isinstance(widget, forms.widgets.Textarea):
                    widget.attrs['rows'] = '1'

                # Defensive client-side handlers — truncate on input/paste and prevent extra key presses.
                widget.attrs['oninput'] = f"if(this.value.length > {max_val}) this.value = this.value.slice(0, {max_val});"
                widget.attrs['onpaste'] = (
                    "const el=this; setTimeout(()=>{ if(el.value.length > %d) el.value = el.value.slice(0, %d); }, 0);"
                ) % (max_val, max_val)

                # onkeydown / onkeypress: block character input when at limit and no selection
                widget.attrs['onkeydown'] = (
                    "const max={max};"
                    "const k = event.key || '';"
                    "const allowed = ['Backspace','Delete','ArrowLeft','ArrowRight','ArrowUp','ArrowDown','Tab','Enter'];"
                    "if(allowed.includes(k) || event.ctrlKey || event.metaKey) return;"
                    "const selStart = this.selectionStart || 0; const selEnd = this.selectionEnd || 0;"
                    "if(this.value.length >= max && selStart === selEnd) event.preventDefault();"
                ).format(max=max_val)

                widget.attrs['onkeypress'] = (
                    "const max={max}; const selStart=this.selectionStart||0; const selEnd=this.selectionEnd||0;"
                    "if(this.value.length >= max && selStart === selEnd) event.preventDefault();"
                ).format(max=max_val)

    def clean(self):
        cleaned = super().clean()
        for fname in MAX_FIELDS:
            if fname in self.fields:
                val = cleaned.get(fname)
                if not val:
                    continue
                sval = str(val)
                max_val = FIELD_MAX.get(fname, DEFAULT_MAX)
                if len(sval) > max_val:
                    cleaned[fname] = sval[:max_val]   # truncate silently
        return cleaned

class DirectCallForm(MaxLengthFormMixin, forms.ModelForm):
    class Meta:
        model = DirectCall
        fields = '__all__'
        widgets = {
            'date_of_complaint': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'date_of_sale_of_device': forms.DateInput(attrs={'type': 'date'}),
            'vehicle_sale_date': forms.DateInput(attrs={'type': 'date'}),
            'customer_raised_issue': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter customer voice'}),
            'first_communication_in_darby': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'last_communication_in_darby': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'final_action_taken': forms.Textarea(attrs={'rows': 1, 'class': 'form-control'}),
            'date_of_closure': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'vehicle_avl_in_workshop': forms.Select(attrs={'class': 'form-control'}),
            # ensure textareas that should be limited have maxlength attribute
            'D1': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter D1 Comments', 'rows': 1, 'maxlength': str(DEFAULT_MAX)}),
            'D2': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter D2 Comments', 'rows': 1, 'maxlength': str(DEFAULT_MAX)}),
            'D3': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter D3 Comments', 'rows': 1, 'maxlength': str(DEFAULT_MAX)}),
            'ialert_comments': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Comments in IAlert', 'rows': 1, 'maxlength': str(DEFAULT_MAX)}),
            'manager_comments': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Manager Comments', 'rows': 1, 'maxlength': str(DEFAULT_MAX)}),
            'hod_comment': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Manager Comments', 'rows': 1, 'maxlength': str(DEFAULT_MAX)}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Remarks', 'rows': 1, 'maxlength': str(DEFAULT_MAX)}),
            'remarks_03': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Remarks 03', 'rows': 1, 'maxlength': str(DEFAULT_MAX)}),
            'final_conclusion': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Final Conclusion', 'rows': 1, 'maxlength': str(DEFAULT_MAX)}),
            'customer_feedback_eng_review': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Customer Feedback for Engineer Review', 'rows': 1, 'maxlength': str(DEFAULT_MAX)}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date_of_complaint'].widget.attrs['readonly'] = True
        if not self.instance.call_status:  # Set default value if not already set
            self.fields['call_status'].initial = 'Pending'

class ManagerForm(MaxLengthFormMixin, forms.ModelForm):
    contact_number = forms.CharField(
        max_length=40,
        required=False,
        validators=[
            RegexValidator(
                regex=r'^[0-9;\-\s]*$',
                message="Contact number must be exactly digits and separator ; ."
            )
        ],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter 10-digit contact number'})
    )
    customer_mail_id = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Multiple emails separated by semicolon'})
    )

    class Meta:
        model = DirectCall
        fields = [
            'date_of_complaint', 'complaint_raised_from_location', 'customer_raised_issue', 'complaint_raised',
            'complaint_raised_by', 'contact_number', 'customer_mail_id', 'vehicle_avl_in_workshop', 'complaint_raised_through',
            'complaint_received_by', 'vin','psn', 'complaint_assigned_to', 'submitted_to_email','ialert_remarks',
            'engineer_contact_number', 'upload_file','call_type', 'ticket_no', 'updated_contact_no','ialert_tk_timestamp'
        ]
        widgets = {
            'date_of_complaint': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'},
                format='%Y-%m-%dT%H:%M'  # Match the browser's datetime-local format
            ),
            'customer_raised_issue': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter customer voice'}),  # Changed to TextInput
            'ialert_tk_timestamp': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'},
                format='%Y-%m-%dT%H:%M'
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date_of_complaint'].input_formats = ['%Y-%m-%dT%H:%M']
        # Ensure the IAlert timestamp sent by the browser (datetime-local) is parsed correctly
        if 'ialert_tk_timestamp' in self.fields:
            self.fields['ialert_tk_timestamp'].input_formats = ['%Y-%m-%dT%H:%M']

    def clean(self):
        cleaned_data = super().clean()
        customer_mail_id = cleaned_data.get('customer_mail_id', '').strip()
        
        # Validate multiple emails separated by semicolon
        if customer_mail_id:
            emails = [email.strip() for email in customer_mail_id.split(';')]
            email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
            for email in emails:
                if email and not re.match(email_regex, email):
                    raise ValidationError(
                        f'Invalid email format: "{email}". Please use semicolon-separated emails (e.g., email1@example.com;email2@example.com)'
                    )
        
        return cleaned_data

class EngineerForm(MaxLengthFormMixin, forms.ModelForm):
    class Meta:
        model = DirectCall
        fields = [
            'psn',
            'end_customer_mail_id',
            'veh_reg_no',

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
            'S_trigger_date',
            's_trigger_completion_date',
            'C_trigger_date',
            'vehicle_run',
            'kilometers_hours',
            'main_battery_voltage',
            'veh_model',
            'engine_type',
            'final_action_taken',
            'call_status',
            'date_of_closure',
            'contact_person_name',
            'contact_person_number',
            'contact_category',
            'owner_contact_no',
            'customer_contact_no',
            'exist_software',
            'updated_software',
            'issue_identified',
            'issue_analysis',
            'issue_analysis_01',
            'issue_category',
            'dealer_name',
            'al_mfg_plant',
            'call_closure_cat',
            'nrd_category',
            'card_status',
            'D1',
            'D1_engineer',
            'D1_remark',
            'D2_remark',
            'D3_remark',
            'D1_closure_date',
            'D2',
            'D2_engineer',
            'D2_exp_date',
            'D2_closure_date',
            'D3_Engineer',
            'D3_exp_date',
            'D3_closure_date',
            'D3',
            'Latest_update',
            'd1_d2_d3_ialert',
            'no_of_complaint_received',
            'remarks_in_ialert',
            'ialert_comments',
            'Latency_7_days',
            'V_packet_7_days',
            'Latency_3_months',
            'V_packet_3_months',
            'analysis',
            'final_action_taken',
            'finalised_issue_category',
            'upload_file_01',
            'call_status',
            'engineer_recommendation',
            'manager_comments',
            'hod_comment',
            'chargable_or_not',
            'payment_status',
            "remarks",
            'date_of_closure',
            'call_closed_by',
            'external_modification',
            'device_IMEI',
            'device_ICCID',
            'device_to_be_sent',
            'dealer_address',
            'D1_resp',
            'D2_resp',
            'D3_resp',
        ]
        widgets = {
            'payment_status': forms.Select(attrs={'class': 'form-control'}),
            'psn': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter PSN'}),
            'veh_reg_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Veh Reg No'}),
            'support_required': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Support Required'}),
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
            'S_trigger_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            's_trigger_completion_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'C_trigger_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'vehicle_sale_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'first_communication_in_darby': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'last_communication_in_darby': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'vehicle_run': forms.Select(attrs={'class': 'form-control'}),
            'kilometers_hours': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Kilometers/Hours'}),
            'main_battery_voltage': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Main Battery Voltage'}),
            'issue_analysis': forms.Select(attrs={'class': 'form-control'}),
            'issue_analysis_01':forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Issue analysis', 'rows': 1}),
            'final_action_taken': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Final Action Taken', 'rows': 1}),
            'issue_category':forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Issue Category', 'rows': 1}),
            'dealer_name': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Dealer name', 'rows': 1}),
            'call_status': forms.Select(attrs={'class': 'form-control'}),
            'payment_status': forms.Select(attrs={'class': 'form-control'}),
            'date_of_closure': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'contact_person_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Contact Person Name'}),
            'contact_person_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Contact Person Number'}),
            'contact_category': forms.Select(attrs={'class': 'form-control'}),
            'owner_contact_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Owner Contact Number'}),
            'customer_contact_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Owner Contact Number(Darby)'}),
            'call_closure_cat': forms.Select(attrs={'class': 'form-control'}),
            'exist_software': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Existing Software'}),
            'updated_software': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Updated Software'}),
            'finalised_issue_category': forms.Select(attrs={'class': 'form-control'}),
            'upload_file_01': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'D1': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter D1 Comments', 'rows': 1, 'maxlength': str(DEFAULT_MAX)}),
            'D1_Remark': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter D1 Remarks', 'rows': 1}),
            'D2_Remark': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter D2 Remarks', 'rows': 1}),
            'D3_Remark': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter D3 Remarks', 'rows': 1}),
            'D2_exp_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'D3_exp_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'd1_d2_d3_ialert': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Remarks in IAlert', 'rows': 1}),

            'D2': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter D2 Comments', 'rows': 1, 'maxlength': str(DEFAULT_MAX)}),
            'D1_closure_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'D2_closure_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'D3_closure_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'Latest_update': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Latest Update', 'rows': 1, 'maxlength': str(DEFAULT_MAX)}),

            'remarks_in_ialert': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Remarks in IAlert', 'rows': 1}),
            'ialert_comments': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Comments in IAlert', 'rows': 1, 'maxlength': str(DEFAULT_MAX)}),
            'manager_comments': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Manager Comments', 'rows': 1, 'maxlength': str(DEFAULT_MAX)}),
            'hod_comment': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Manager Comments', 'rows': 1, 'maxlength': str(DEFAULT_MAX)}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Remarks', 'rows': 1, 'maxlength': str(DEFAULT_MAX)}),
            'remarks_03': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Remarks 03', 'rows': 1, 'maxlength': str(DEFAULT_MAX)}),
            'final_conclusion': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Final Conclusion', 'rows': 1, 'maxlength': str(DEFAULT_MAX)}),
            'customer_feedback_eng_review': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Customer Feedback for Engineer Review', 'rows': 1, 'maxlength': str(DEFAULT_MAX)}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.payment_status:
            self.fields['payment_status'].initial = 'Not paid'

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = DirectCall
        fields = ['confirmation', 'feedback', 'rating', 'customer_feedback','feedback_submitted_datetime']
class EngineerReviewForm(MaxLengthFormMixin, forms.ModelForm):
    class Meta:
        model = DirectCall
        fields = [
            'engineer_name',
            'called_date',
            'latency_for_last_7_days_cc',
            'vpacket_for_last_7_days_cc',
            'remarks_03',
            'final_conclusion',
            'final_status',
            'call_closed_by',
            'exp_review_date',
            'customer_feedback_eng_review'
        ]
        widgets = {
            'engineer_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Engineer Name'}),
            'called_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'latency_for_last_7_days_cc': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Latency for Last 7 Days'}),
            'vpacket_for_last_7_days_cc': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter V Packet for Last 7 Days'}),
            'remarks_03': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Remarks 03', 'rows': 1, 'maxlength': str(DEFAULT_MAX)}),
            'final_conclusion': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Final Conclusion', 'rows': 1, 'maxlength': str(DEFAULT_MAX)}),
            'final_status': forms.Select(attrs={'class': 'form-control'}),
            'call_closed_by': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Call Closed By'}),
            'exp_review_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'customer_feedback_eng_review': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Customer Feedback for Engineer Review', 'rows': 1, 'maxlength': str(DEFAULT_MAX)}),
        }

class DeviceRepairForm(MaxLengthFormMixin, forms.ModelForm):
    class Meta:
        model = DirectCall
        fields = [
            'engineer_recommendation',
            'unique_id',
            'psn',
            'vin',
            'complaint_assigned_to',
            'device_IMEI', 'device_ICCID',
            'chargable_or_not',
            'payment_status',
            'issue_identified',
            "device_to_be_sent",
            'hod_comment',
            'dealer_address',
            'chargable_or_not',
            'payment_status',
            "faulty_device_reached_date",
            'engineer_responsible_fetch',
            'device_taken_for_repair',
            'device_repaired',
            'copq_labour',
            'copq_matl',
            'matls_used',
            'plant_analysis',
            'plant_conclusion',
            "device_shipped_to_location",
            "device_shipped_to_engineer",
            "sim_validity",
            'device_shipped_date',
            'device_shipped_through',
            'device_shipped_lr_no',
            'plant_analysis',
            'plant_conclusion',
            'device_delivered_to_customer',
            'device_fitted_by',
            'device_working_status',
            "device_delivered_to_engineer",
            'grn_no_for_faulty_device',
        ]
        widgets = {
            'chargable_or_not': forms.Select(attrs={'class': 'form-control'}),
            'payment_status': forms.Select(attrs={'class': 'form-control'}),
            'device_IMEI': forms.TextInput(attrs={'class': 'form-control'}),
            'unique_id': forms.TextInput(attrs={'class': 'form-control'}),
            'vin': forms.TextInput(attrs={'class': 'form-control'}),
            'psn': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter PSN'}),
            'device_ICCID': forms.TextInput(attrs={'class': 'form-control'}),
            'complaint_assigned_to': forms.TextInput(attrs={'class': 'form-control'}),
            'device_to_be_sent': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Device to be Sent'}),
            "device_shipped_to_location": forms.TextInput(attrs={'class': 'form-control'}),
            "device_shipped_to_engineer": forms.TextInput(attrs={'class': 'form-control'}),
            "sim_validity": forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            "device_delivered_to_engineer": forms.TextInput(attrs={'class': 'form-control'}),
            'engineer_recommendation': forms.Select(attrs={'class': 'form-control'}),
            'faulty_device_psn_number_fetch': forms.TextInput(attrs={'class': 'form-control'}),
            'engineer_responsible_fetch': forms.TextInput(attrs={'class': 'form-control'}),
            'device_taken_for_repair': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'device_repaired': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'copq_labour': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'copq_matl': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'matls_used': forms.Select(attrs={'class': 'form-control'}),
            'issue_identified': forms.TextInput(attrs={'class': 'form-control'}),
            'hod_comment': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter HOD Comment', 'rows': 1, 'maxlength': str(DEFAULT_MAX)}),
            'faulty_device_reached_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'chargable_or_not': forms.Select(attrs={'class': 'form-control'}),
            'device_shipped_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'device_shipped_through': forms.TextInput(attrs={'class': 'form-control'}),
            'device_shipped_lr_no': forms.TextInput(attrs={'class': 'form-control'}),
            'device_delivered_to_customer': forms.TextInput(attrs={'class': 'form-control'}),
            'dealer_address': forms.TextInput(attrs={'class': 'form-control'}),
            'device_fitted_by': forms.TextInput(attrs={'class': 'form-control'}),
            'device_working_status': forms.Select(attrs={'class': 'form-control'}),
            'grn_no_for_faulty_device': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter GRN Number'}),
            'plant_analysis': forms.Textarea(attrs={'class': 'form-control', 'rows': 1, 'placeholder': 'Enter plant analysis', 'maxlength': str(DEFAULT_MAX)}),
            'plant_conclusion': forms.Textarea(attrs={'class': 'form-control', 'rows': 1, 'placeholder': 'Enter plant conclusion', 'maxlength': str(DEFAULT_MAX)}),
        }
class AltDeviceForm(forms.ModelForm):
    class Meta:
        model = DirectCall
        fields = [
            'unique_id',
            'psn',
            'vin',
            'device_IMEI',
            'device_ICCID',
            'complaint_assigned_to',
            'issue_identified',
            "device_to_be_sent",
            'alt_device_sent_by',
            'alt_device_psn',
            'al_dev_sim_status',
            'alt_device_validity_status',
            'alt_device_shipped_date',
            'alt_device_shipped_through',
            'alt_device_shipped_lr_no',
            'date_of_alt_device_delivered_to_customer',
            'validity_of_old_device',
            'validity_of_alt_device',
            'validity_transfer_from_old_device',
            'validity_from_old_to_new_yes_done_by',
            'updated_validity_of_alt_device',
            'alt_device_fitted_by',
            'alt_device_fitted_date',
            'alt_device_mapping_completion_date',
            'device_working_status',
            'device_to_be_sent',
            'old_device_sent_to_location',
            'alt_device_working_status',
            'faulty_device_shipped_date',
            'faulty_device_shipped_thru',
            'faulty_device_shipped_lr_details',
            'faulty_device_reached_date',
            'faulty_device_confirmation_from_destination',
            'grn_no_for_faulty_device',
        ]
        widgets = {
            'unique_id': forms.TextInput(attrs={'class': 'form-control'}),
            'vin': forms.TextInput(attrs={'class': 'form-control'}),
            'device_IMEI': forms.TextInput(attrs={'class': 'form-control'}),
            'device_ICCID': forms.TextInput(attrs={'class': 'form-control'}),
            'complaint_assigned_to': forms.TextInput(attrs={'class': 'form-control'}),
            'issue_identified': forms.TextInput(attrs={'class': 'form-control'}),
            'al_dev_sim_status': forms.Select(attrs={'class': 'form-control'}),  # Updated to Select widget
            'device_to_be_sent': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Device to be Sent'}),
            'psn': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Device to be Sent'}),
            'alt_device_fitted_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'alt_device_psn': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter ALT Device PSN'}),
            'validity_of_old_device': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'alt_device_sent_to_customer_from_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Location'}),
            'alt_device_sent_by':forms.Select(attrs={'class': 'form-control'}),
            'date_of_alt_device_delivered_to_customer': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'alt_device_fitted_by': forms.TextInput(attrs={'class': 'for m-control', 'placeholder': 'Enter Fitter Name'}),
            'faulty_device_psn_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Faulty Device PSN'}),
            'validity_from_old_to_new_yes_done_by': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Validity Transfer Details'}),
            'alt_device_shipped_lr_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter LR Number'}),
            'alt_device_mapping_completion_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'alt_device_shipped_through': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Shipping Method'}),
            'device_working_status': forms.Select(attrs={'class': 'form-control'}),
            'alt_device_shipped_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'validity_of_alt_device': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'engineer_responsible': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Engineer Name'}),
            'validity_transfer_from_old_device': forms.Select(attrs={'class': 'form-control'}),
            'updated_validity_of_alt_device': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'alt_device_validity_status': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'old_device_sent_to_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Old Device Location'}),
            'faulty_device_shipped_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'faulty_device_shipped_thru': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Shipping Method'}),
            'faulty_device_shipped_lr_details': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter LR Details'}),
            'faulty_device_reached_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'faulty_device_confirmation_from_destination': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Confirmation Details'}),
            'grn_no_for_faulty_device': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter GRN Number'}),
        }
