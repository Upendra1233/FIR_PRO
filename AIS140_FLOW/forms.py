from django import forms
from .models import AIS140Request

class ManagerForm(forms.ModelForm):
    class Meta:
        model = AIS140Request
        fields = [
            'request_id','reupdated_request_al',
            'date_of_request','Customer_assigned_date','AL_assigned_date', 'customer_name', 'customer_phone', 'dealer_name', 'assigned_to',
            'state',  'rto_code', 'rto_name', 'vehicle_available_in_workshop', 'assigned_engineer_email',
            'device_mode', 'request_type', 'vin_no', 'psn', 'aadhar_card', 'teleco_status', 'teleco_type',
            'validity_expiry_date', 'sos_fitment_date', 'pan_card', 'manufacturing_year', 'engine','requested_by',
            'requested_name',
            'requested_phone_number','dealer_code','Customer_Alternate_number','Cust_veh_Regn_Address','Customer_Email_ID','category','AIS140_Type','Dealer_mail',
            'vehicle_no', 'vehicle_model', 'owner_name', 'owner_phone', 'ao_name', 'ro', 'zone','remarks','AL_comments','AL_remarks',
            'completion_status', 'sim_activation_manual', 'sim_activation_service', 'request_sent_by_email'
        ]
        widgets = {
            'date_of_request': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'reupdated_request_al': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'Customer_assigned_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'AL_assigned_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'validity_expiry_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'sos_fitment_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'sw_flashed_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'remarks': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter remarks','rows': 1}),
            'requested_by': forms.Select(attrs={'class': 'form-control'}),
            'requested_name': forms.Select(attrs={'class': 'form-control','placeholder': 'Select Mail ID'}),
            'requested_phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Phone Number'}),
            'Cust_veh_Regn_Address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Customer Address',
                'rows': 1
            }),
            'dealer_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Dealer Code'}),
            'AL_remarks': forms.TextInput(attrs={'class': 'form-control', 'rows': 1, 'placeholder': 'Enter AL Remarks'}),
            'AL_comments': forms.TextInput(attrs={'class': 'form-control', 'rows': 1, 'placeholder': 'Enter AL Comments'}),

        }


class EngineerForm(forms.ModelForm):
    class Meta:
        model = AIS140Request
        fields = [
            'request_id',
            'd1', 'D1_engineer', 'd2', 'D2_engineer', 'd3', 'remarks', 'communication_status', 'vehicle_running_location',
            'contact_person', 'contact_person_phone', 'sw_flashed_version', 'sw_flashed_date', 'sos_verification'
        ]
        widgets = {
            'sw_flashed_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_vehicle_running_location(self):
        value = self.cleaned_data.get('vehicle_running_location')
        if value not in dict(AIS140Request.VEHICLE_RUNNING_LOCATION).keys():
            raise forms.ValidationError("Invalid value for vehicle running location.")
        return value

class PartBForm(forms.ModelForm):
    class Meta:
        model = AIS140Request
        fields = [
            'request_id',
            'device_mode', 'request_type', 'icicid_no', 'imei_no', 'subscription_raised_by',
            'current_sim_status', 'existing_plan_start_date', 'existing_plan_end_date',
            'reqd_plan_start_date', 'reqd_plan_end_date', 'plan_reqd', 'top_up_reqd_for',
            'sr_req_no', 'sr_req_date', 'sr_success_date', 'tat_sr_s_sr_r', 'existing_sw',
            'sch_sw', 'sw_sch_date', 'sw_success_date', 'tat_sws_swsch', 'veh_status','certification_start_date','certification_end_date',
            'bb_completed_date', 'sos_fitment', 'sos_fitment_date', 'sos_verification_reqd',
            'sos_verified_date', 'data_posting_verification', 'data_verified_date',
            'otp_generated_date', 'otp_updated_date', 'temp_cert_reqd', 'temp_cert_date','permanent_cert_date',
            'permanent_certificate', 'responsibility',  'completion_status', 'completion_date','remarks_02',
            'upload_certificate_in_ialert','upload_certificate_in_ialert_01','upload_certificate_in_ialert_02', 'mail_to_customer','Dealer_mail', 'TSM_mail','upload_certificate_in_danlaw_server',
            'total_tat','d1','d2','D1_engineer', 'D2_engineer','D1_comments','D2_comments','Update_to_AL_API','temp_raised_by','perm_raised_by','additional_email_id'
        ]

        widgets = {
            'device_mode':forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Device Model'}),
            'certification_start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'certification_end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'remarks_02' :forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter remarks','rows': 1}),
            'existing_plan_start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'existing_plan_end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'reqd_plan_start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'reqd_plan_end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'sr_req_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'sr_success_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'sw_sch_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'sw_success_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'sos_fitment_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'sos_verified_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'data_verified_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'otp_generated_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'otp_updated_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'temp_cert_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'completion_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'top_up_reqd_for': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter top-up required for','rows': 1}),
            'permanent_cert_date;': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'responsibility': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter responsibility'}),
            'upload_certificate_in_ialert': forms.ClearableFileInput(attrs={'class': 'form-control'}),  # Fixed widget
            'upload_certificate_in_ialert_01': forms.ClearableFileInput(attrs={'class': 'form-control'}),  # Fixed widget
            'upload_certificate_in_ialert_02': forms.ClearableFileInput(attrs={'class': 'form-control'}),  # Fixed widget
            'upload_certificate_in_danlaw_server': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Danlaw server certificate details'}),
            'icicid_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter ICICID No', 'maxlength': '20'}),
            'imei_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter IMEI No', 'maxlength': '17'}),
            'd1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter D1 Remarks', 'rows': 1}),
            'd2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter D2 Remarks', 'rows': 1}),
            'D1_engineer': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter D1 Engineer Email'}),
            'D2_engineer': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter D2 Engineer Email'}),
            'Dealer_mail': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Dealer Mail ID' , 'row': 1}),
            'TSM_mail': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter TSM Mail ID' , 'row': 1}),
            'D1_comments':forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter D1 Comments', 'rows': 1}),
            'D2_comments':forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter D2 Comments', 'rows': 1}),
            'Update_to_AL_API': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Update to AL API details', 'rows': 1}),

        }

    def clean_Update_to_AL_API(self):
        """Ensure Update_to_AL_API field is not empty."""
        value = self.cleaned_data.get('Update_to_AL_API')
        if not value or not str(value).strip():
            raise forms.ValidationError('Please update Update to A.L API field.')
        return str(value).strip()

    def clean(self):
        """Comprehensive validation for certificates and D1/D2 remarks based on Update_to_AL_API value."""
        cleaned = super().clean()
        api_value = cleaned.get('Update_to_AL_API')

        # Check certificate file uploads
        has_temp_cert = self.files.get('upload_certificate_in_ialert') or bool(getattr(self.instance, 'upload_certificate_in_ialert', None))
        has_perm_cert = self.files.get('upload_certificate_in_ialert_01') or bool(getattr(self.instance, 'upload_certificate_in_ialert_01', None))
        has_vahan_cert = self.files.get('upload_certificate_in_ialert_02') or bool(getattr(self.instance, 'upload_certificate_in_ialert_02', None))

        # RULE 1: If Permanent Certificate is uploaded → Update_to_AL_API MUST be "Permanent"
        if has_perm_cert and api_value != 'Permanent':
            self.add_error('Update_to_AL_API', 'When Permanent Certificate is uploaded, Update to A.L API must be set to "Permanent"')

        # RULE 2: If only Temporary Certificate is uploaded (no Permanent) → Update_to_AL_API MUST be "Temporary"
        if has_temp_cert and not has_perm_cert and api_value != 'Temporary':
            self.add_error('Update_to_AL_API', 'When only Temporary Certificate is uploaded, Update to A.L API must be set to "Temporary"')

        # RULE 3-6: Handle scenarios when both certificates are blank
        if not has_temp_cert and not has_perm_cert:
            d1_remarks = cleaned.get('d1')
            d1_comments = cleaned.get('D1_comments')
            d2_remarks = cleaned.get('d2')
            d2_comments = cleaned.get('D2_comments')

            d1_remarks_filled = d1_remarks and str(d1_remarks).strip()
            d1_comments_filled = d1_comments and str(d1_comments).strip()
            d2_remarks_filled = d2_remarks and str(d2_remarks).strip()
            d2_comments_filled = d2_comments and str(d2_comments).strip()

            d1_complete = d1_remarks_filled and d1_comments_filled
            d2_complete = d2_remarks_filled and d2_comments_filled

            # RULE 3: Check D2 - if either is filled but not both, show error "both should be mandatory"
            d2_partially_filled = (d2_remarks_filled or d2_comments_filled) and not d2_complete
            if d2_partially_filled:
                self.add_error('d2', '⚠️ Both D2 Remarks and D2 Comments are mandatory - either fill both or leave both empty')
                self.add_error('D2_comments', '⚠️ Both D2 Remarks and D2 Comments are mandatory - either fill both or leave both empty')

            # RULE 5: Check D1 - if either is filled but not both, show error "both should be mandatory"
            d1_partially_filled = (d1_remarks_filled or d1_comments_filled) and not d1_complete
            if d1_partially_filled:
                self.add_error('d1', '⚠️ Both D1 Remarks and D1 Comments are mandatory - either fill both or leave both empty')
                self.add_error('D1_comments', '⚠️ Both D1 Remarks and D1 Comments are mandatory - either fill both or leave both empty')

            # RULE 4 & 6: Validate Update_to_AL_API based on which D-level is complete
            # If both D1 and D2 are complete, Update_to_AL_API should be "D2" (the latest follow-up)
            if d1_complete and d2_complete:
                if api_value != 'D2':
                    self.add_error('Update_to_AL_API', 'When both D1 and D2 are complete, Update to A.L API must be set to "D2"')
            # If only D2 is complete, Update_to_AL_API should be "D2"
            elif d2_complete and not d1_complete:
                if api_value != 'D2':
                    self.add_error('Update_to_AL_API', 'When both D2 Remarks and D2 Comments are filled, Update to A.L API must be set to "D2"')
            # If only D1 is complete, Update_to_AL_API should be "D1"
            elif d1_complete and not d2_complete:
                if api_value != 'D1':
                    self.add_error('Update_to_AL_API', 'When both D1 Remarks and D1 Comments are filled, Update to A.L API must be set to "D1"')

        # New validations based on Update_to_AL_API value
        if api_value == 'D1':
            if not cleaned.get('d1') or not str(cleaned.get('d1')).strip():
                self.add_error('d1', 'D1 Remarks is required when Update to A.L API is set to "D1"')
            if not cleaned.get('D1_comments') or not str(cleaned.get('D1_comments')).strip():
                self.add_error('D1_comments', 'D1 Comments is required when Update to A.L API is set to "D1"')
        elif api_value == 'D2':
            if not cleaned.get('d2') or not str(cleaned.get('d2')).strip():
                self.add_error('d2', 'D2 Remarks is required when Update to A.L API is set to "D2"')
            if not cleaned.get('D2_comments') or not str(cleaned.get('D2_comments')).strip():
                self.add_error('D2_comments', 'D2 Comments is required when Update to A.L API is set to "D2"')
        elif api_value == 'Temporary':
            if not has_temp_cert:
                self.add_error('upload_certificate_in_ialert', 'Temporary Certificate is required when Update to A.L API is set to "Temporary"')
        elif api_value == 'Permanent':
            if not has_perm_cert:  # Assuming upload_certificate_in_ialert_01 for Permanent as per user
                self.add_error('upload_certificate_in_ialert_01', 'Permanent Certificate is required when Update to A.L API is set to "Permanent"')

        return cleaned


