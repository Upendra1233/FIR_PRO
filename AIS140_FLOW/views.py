from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.utils.timezone import now
from django.core.mail import EmailMessage
from django.urls import reverse
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
import os
from .models import AIS140Request
from .forms import ManagerForm, PartBForm
import logging
import csv
import requests
from django.utils import timezone
from django.utils import timezone
from datetime import datetime, date, time, timedelta
import pytz
from django.utils import timezone
from django.utils.timezone import localtime
import logging

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
import json
from psn_project.email_utils import send_email_with_config
from datetime import datetime
import pytz
logger = logging.getLogger(__name__)
IST = pytz.timezone("Asia/Kolkata")
UTC = pytz.UTC

# Engineer name to email mapping
ENGINEER_EMAIL_MAP = {
    "Arun": "arung@danlawtech.com",
    "Rishwanth": "rishwanthr@danlawtech.com",
    "Arun Maity": "eastdanlaw@danlawtech.com",
    "Paribesh": "paribeshb@danlawtech.com",
    "Narendra": "narendrareddyg@danlawtech.com",
    "Dilip": "dilipkumarn@danlawtech.com",
    "Dilip Kumar": "dilipkumarn@danlawtech.com",
    "Jitendra": "pantnagarplant@danlawtech.com",
    "Jitendra": "pantnagarplant@danlawtech.com",
    "Gayadhar": "gayadhar@danlawtech.com",
    "Eliyas": "eliyasp@danlawtech.com",
    "Siva": "sivanambirajant@danlawtech.com",
    "Rajesh": "Ennoreplant@danlawtech.com",
    "Gowtham": "gowthamv@danlawtech.com",
    "Yoga": "yoganandam@danlawtech.com",
    "SR": "rajendrans@danlawtech.com",
}

def resolve_engineer_email(identifier):
    """
    Resolve engineer name or email to actual email address.
    If already an email, return as-is.
    If a name, lookup in mapping.
    """
    if not identifier:
        return None

    identifier = str(identifier).strip()

    # If it's already an email address, return it
    if "@" in identifier:
        return identifier

    # Otherwise, try to find it in the mapping
    return ENGINEER_EMAIL_MAP.get(identifier, identifier)

def to_ist(dt):
    if not dt:
        return ""

    # If string → try parse safely
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt)
        except Exception:
            return ""

    # Year sanity guard (prevents overflow)
    if not (1900 <= dt.year <= 2100):
        return ""

    # Naive datetime → assume UTC
    if dt.tzinfo is None:
        try:
            dt = UTC.localize(dt)
        except Exception:
            return ""

    try:
        return dt.astimezone(IST).strftime("%d-%m-%Y %H:%M:%S")
    except Exception:
        return ""
from django.utils import timezone

def save(self, *args, **kwargs):
    now_dt = timezone.now()

    datetime_fields = [
        'date_of_request',

        'Customer_assigned_date',
        'AL_assigned_date',
        'existing_plan_start_date',
        'existing_plan_end_date',
        'reqd_plan_start_date',
        'reqd_plan_end_date',
        'sr_req_date',
        'sr_success_date',
        'sw_sch_date',
        'sw_success_date',
        'sos_fitment_date',
        'sos_verified_date',
        'data_verified_date',
        'otp_generated_date',
        'otp_updated_date',
        'temp_cert_date',
        'permanent_cert_date',
        'completion_date',
        'D1_closure',
        'D2_closure',
    ]

    for field in datetime_fields:
        if getattr(self, field, None) is None:
            setattr(self, field, None)  # allow NULL safely

    super().save(*args, **kwargs)

def part_a_form(request, id=None):
    entry = None
    if id:
        entry = get_object_or_404(AIS140Request, id=id)
    if request.method == 'POST':
        try:
            old_assigned_email = entry.assigned_engineer_email if entry else None

            if entry:
                form = ManagerForm(request.POST, request.FILES, instance=entry)
            else:
                form = ManagerForm(request.POST, request.FILES)
            if form.is_valid():
                entry = form.save(commit=False)
                if not id:  # only set date on creation
                    entry.date_of_request = now()
                entry.save()

                # Generate Part B URL
                part_b_url = request.build_absolute_uri(reverse('part_b_form', args=[entry.id]))
                # Prepare email details
                subject = f"AIS140 Certification Request : {entry.unique_id}"
                html_message = render_to_string('emails/part_a_email.html', {
                    'entry': entry,
                    'part_b_url': part_b_url,
                    'site_domain': request.build_absolute_uri('/')[:-1],
                })
                engineer_email = resolve_engineer_email(entry.assigned_engineer_email)
                recipient_list = [engineer_email] if engineer_email else []
                cc_list = ['sales@danlawtech.com', "dilipkumarn@danlawtech.com","narendrareddyg@danlawtech.com","rajendrans@danlawtech.com"]

                # Send email on NEW creation OR when assigned_engineer_email changes
                send_email = False
                if not id:
                    send_email = True  # New ticket
                elif entry.assigned_engineer_email and entry.assigned_engineer_email != old_assigned_email and entry.assigned_engineer_email != "--":
                    send_email = True  # Assignment changed

                if send_email and entry.assigned_engineer_email and entry.assigned_engineer_email != "--":
                    try:
                        send_email_with_config(
                            subject=subject,
                            html_message=html_message,
                            recipient_list=recipient_list,
                            cc_list=cc_list,
                            config_type='AIS140'
                        )
                        logger.info(f"Email sent for Part-A (Request ID: {entry.unique_id})")
                    except Exception as e:
                        logger.error(f"Failed to send email (Request ID: {entry.unique_id}): {e}")

                # Redirect to Part A form with success parameter
                success_url = reverse('part_a_form') + '?success=true'
                return redirect(success_url)
            else:
                logger.error(f"Form errors: {form.errors}")
        except Exception as e:
            logger.error(f"Unexpected error in part_a_form: {e}")
            return redirect('part_a_form')
    else:
        if entry:
            form = ManagerForm(instance=entry)
        else:
            form = ManagerForm(initial={'Customer_assigned_date': now()})
    success = request.GET.get('success', False)
    return render(request, 'AIS140_FLOW/part_a_form.html', {
        'form': form,
        'success': success
    })

def part_b_form(request, id):
    # Fetch the entry for Part-B
    entry = get_object_or_404(AIS140Request, id=id)

    # Fetch Part-A data
    part_a_data = {
        'date_of_request': entry.date_of_request,
        'Customer_assigned_date': entry.Customer_assigned_date,
        'AL_assigned_date': entry.AL_assigned_date,
        'reupdated_request_al':entry.reupdated_request_al,
        'requested_by': entry.requested_by,
        'requested_name': entry.requested_name,
        'requested_phone_number': entry.requested_phone_number,
        'device_mode': entry.device_mode,
        'request_type': entry.request_type,
        'category': entry.category,
        'assigned_to': entry.assigned_to,
        'user_id': entry.user_id,
        'state': entry.state,
        'vin_no': entry.vin_no,
        'engine': entry.engine,
        'psn': entry.psn,
        'vehicle_no': entry.vehicle_no,
        'vehicle_model': entry.vehicle_model,
        'customer_name': entry.customer_name,
        'customer_phone': entry.customer_phone,
        'pan_card': entry.pan_card,
        'aadhar_card': entry.aadhar_card,
        'manufacturing_year': entry.manufacturing_year,
        'rto_name': entry.rto_name,
        'rto_code': entry.rto_code,
        'dealer_name': entry.dealer_name,
        'dealer_code': entry.dealer_code,
        'Dealer_mail': entry.Dealer_mail,
        'ao_name': entry.ao_name,
        'ro': entry.ro,
        'zone': entry.zone,
        'remarks': entry.remarks,
        'AL_remarks':entry.AL_remarks,
        'AL_comments':entry.AL_comments,
        'ticket_through':entry.ticket_through,
        'Customer_Alternate_number':entry.Customer_Alternate_number,
        'Cust_veh_Regn_Address': entry.Cust_veh_Regn_Address,
        'Customer_Email_ID':entry.Customer_Email_ID,
        'AIS140_Type':entry.AIS140_Type,
        'Dealer_Contact':entry.Dealer_Contact
        }

    # Determine if the form should be read-only
    is_read_only = entry.completion_status  in ["Permanent", "Temp + Perm","Cancelled","Reject","Third Party Device-Rejected"]

    # Initialize modal context variables
    show_success_modal = False
    success_message = ""
    error_message = ""
    error_reasons = ""

    if request.method == 'POST' and not is_read_only:
        form = PartBForm(request.POST, request.FILES, instance=entry)  # Include request.FILES for file uploads
        if form.is_valid():
            cleaned = form.cleaned_data
            instance = form.save(commit=False)
            # For below completion status just give current timestamp for completion_status
            terminal_statuses = {
                "Permanent",
                "Temp + Perm",
                "Temporary",
                "Cancelled",
                "Reject",
                "Third Party Device-Rejected",
            }

            # Handle datetime-local fields from form submission
            current_time_ist = now().astimezone(IST)

            # Parse and set D1_closure if provided
            if request.POST.get('D1_closure'):
                try:
                    d1_closure_str = request.POST.get('D1_closure')
                    # Parse datetime-local format (YYYY-MM-DDTHH:mm)
                    d1_dt = datetime.strptime(d1_closure_str, '%Y-%m-%dT%H:%M')
                    # Localize as IST
                    d1_dt = IST.localize(d1_dt)
                    instance.D1_closure = d1_dt
                    logger.info(f"D1_closure set to: {d1_dt} (Request ID: {entry.unique_id})")
                except Exception as e:
                    logger.error(f"Error parsing D1_closure: {e}")

            # Parse and set D2_closure if provided
            if request.POST.get('D2_closure'):
                try:
                    d2_closure_str = request.POST.get('D2_closure')
                    # Parse datetime-local format (YYYY-MM-DDTHH:mm)
                    d2_dt = datetime.strptime(d2_closure_str, '%Y-%m-%dT%H:%M')
                    # Localize as IST
                    d2_dt = IST.localize(d2_dt)
                    instance.D2_closure = d2_dt
                    logger.info(f"D2_closure set to: {d2_dt} (Request ID: {entry.unique_id})")
                except Exception as e:
                    logger.error(f"Error parsing D2_closure: {e}")

            # Parse and set completion_date if provided
            if request.POST.get('completion_date'):
                try:
                    completion_date_str = request.POST.get('completion_date')
                    # Parse datetime-local format (YYYY-MM-DDTHH:mm)
                    completion_dt = datetime.strptime(completion_date_str, '%Y-%m-%dT%H:%M')
                    # Localize as IST
                    completion_dt = IST.localize(completion_dt)
                    instance.completion_date = completion_dt
                    logger.info(f"completion_date set to: {completion_dt} (Request ID: {entry.unique_id})")
                except Exception as e:
                    logger.error(f"Error parsing completion_date: {e}")

            # Auto-set completion_date when status is set to terminal status
            if instance.completion_status in terminal_statuses and not instance.completion_date:
                instance.completion_date = current_time_ist
                logger.info(f"Auto-set completion_date to current IST time (Request ID: {entry.unique_id})")

            instance.save()

            # Verify saved values
            logger.info(f"After save - D1_closure: {instance.D1_closure}, D2_closure: {instance.D2_closure}, completion_date: {instance.completion_date} (Request ID: {entry.unique_id})")

            entry = instance

            # Send to customer API
            try:
                result = _send_to_customer_api(request, entry)
                if result.get('success'):
                    logger.info("Successfully sent to customer: %s", result)
                else:
                    logger.warning("Customer API send failed: %s", result.get('error'))
            except Exception as e:
                logger.exception("Error sending to customer API: %s", e)

            if (getattr(entry, 'd1', None) is not None or getattr(entry, 'd2', None) is not None) and (entry.Update_to_AL_API == "D1" or entry.Update_to_AL_API == "D2") :

                try:
                    subject = f"AIS140 Certificate Generation -Show Stopper  {entry.unique_id} on {entry.vin_no}"
                    html_message = render_to_string('emails/customer_update.html', {
                        'entry': entry,
                        'site_domain': request.build_absolute_uri('/')[:-1],  # Get the site domain
                    })
                    if entry.state=="KARNATAKA":
                        add_email=["sales.hubli@amlmotors.com"]
                    elif entry.state=="MAHARASHTRA":
                        add_email=["ashish.rawat2@ashokleyland.com","suraj.khatri@ashokleyland.com","kapil.mohan@ashokleyland.com"]
                    elif entry.state=="GUJARAT":
                        add_email=["ashish.rawat2@ashokleyland.com","kapil.mohan@ashokleyland.com"]                        
                    else:
                        add_email=[]
                    # Resolve engineer emails
                    assigned_eng_email = resolve_engineer_email(entry.assigned_engineer_email)
                    recipient_list_1 = [assigned_eng_email, entry.Customer_Email_ID, entry.Dealer_mail, entry.additional_email_id, "Athulya.T@ashokleyland.com", "KRY_arunkumar@ashokleyland.com"] + add_email
                    recipient_list_1 = [email for email in recipient_list_1 if email]  # Remove empty/None values
                    cc_list_1 = ['sales@danlawtech.com', "dilipkumarn@danlawtech.com", "narendrareddyg@danlawtech.com", "rajendrans@danlawtech.com"]
                    send_email_with_config(
                        subject=subject,
                        html_message=html_message,
                        recipient_list=recipient_list_1,
                        cc_list=cc_list_1,
                        config_type='AIS140'
                    )
                    logger.info(f"Email sent to manager for Part-B form update (Request ID: {entry.unique_id})")
                except Exception as e:
                    logger.error(f"Failed to send email for Part-B form update (Request ID: {entry.unique_id}): {e}")
            # Check if the form is marked as closed
            if entry.completion_status in ["Permanent", "Temp + Perm","Temporary","Cancelled","Reject","Third Party Device-Rejected"]:
                try:
                    # Prepare email details
                    subject = f"AIS140 Request Completed :  {entry.unique_id}"
                    html_message = render_to_string('emails/part_b_closed_email.html', {
                        'entry': entry,
                        'site_domain': request.build_absolute_uri('/')[:-1],  # Get the site domain
                    })
                    if entry.state=="KARNATAKA":
                        add_email=["sales.hubli@amlmotors.com"]
                    elif entry.state=="MAHARASHTRA":
                        add_email=["ashish.rawat2@ashokleyland.com","suraj.khatri@ashokleyland.com","kapil.mohan@ashokleyland.com"]
                    else:
                        add_email=[]
                    # Resolve engineer emails
                    assigned_eng_email = resolve_engineer_email(entry.assigned_engineer_email)
                    recipient_list = [assigned_eng_email, entry.Customer_Email_ID, entry.Dealer_mail, entry.additional_email_id, "Athulya.T@ashokleyland.com", "KRY_arunkumar@ashokleyland.com"] + add_email
                    recipient_list = [email for email in recipient_list if email]  # Remove empty/None values
                    cc_list = ['sales@danlawtech.com',"narendrareddyg@danlawtech.com","rajendrans@danlawtech.com"]  # Replace with additional recipients if needed
                    # Collect attachments based on completion_status
                    attachments = []

                    if entry.Update_to_AL_API == "Temporary":
                        if entry.upload_certificate_in_ialert and entry.upload_certificate_in_ialert.name:
                            try:
                                file_content = entry.upload_certificate_in_ialert.read()
                                attachments.append((
                                    entry.upload_certificate_in_ialert.name.split('/')[-1],
                                    file_content,
                                    'application/octet-stream'
                                ))
                            except Exception as e:
                                logger.error(f"Error reading file: {e}")

                        if entry.upload_certificate_in_ialert_01 and entry.upload_certificate_in_ialert_01.name:
                            try:
                                file_content = entry.upload_certificate_in_ialert_01.read()
                                attachments.append((
                                    entry.upload_certificate_in_ialert_01.name.split('/')[-1],
                                    file_content,
                                    'application/octet-stream'
                                ))
                            except Exception as e:
                                logger.error(f"Error reading file: {e}")

                    elif entry.Update_to_AL_API == "Permanent":

                        if entry.upload_certificate_in_ialert_01 and entry.upload_certificate_in_ialert_01.name:
                            try:
                                file_content = entry.upload_certificate_in_ialert_01.read()
                                attachments.append((
                                    entry.upload_certificate_in_ialert_01.name.split('/')[-1],
                                    file_content,
                                    'application/octet-stream'
                                ))
                            except Exception as e:
                                logger.error(f"Error reading file: {e}")

                        if entry.upload_certificate_in_ialert_02 and entry.upload_certificate_in_ialert_02.name:
                            try:
                                file_content = entry.upload_certificate_in_ialert_02.read()
                                attachments.append((
                                    entry.upload_certificate_in_ialert_02.name.split('/')[-1],
                                    file_content,
                                    'application/octet-stream'
                                ))
                            except Exception as e:
                                logger.error(f"Error reading file: {e}")

                    elif entry.Update_to_AL_API == "Temp + Perm":
                        if entry.upload_certificate_in_ialert and entry.upload_certificate_in_ialert.name:
                            try:
                                file_content = entry.upload_certificate_in_ialert.read()
                                attachments.append((
                                    entry.upload_certificate_in_ialert.name.split('/')[-1],
                                    file_content,
                                    'application/octet-stream'
                                ))
                            except Exception as e:
                                logger.error(f"Error reading file: {e}")

                        if entry.upload_certificate_in_ialert_01 and entry.upload_certificate_in_ialert_01.name:
                            try:
                                file_content = entry.upload_certificate_in_ialert_01.read()
                                attachments.append((
                                    entry.upload_certificate_in_ialert_01.name.split('/')[-1],
                                    file_content,
                                    'application/octet-stream'
                                ))
                            except Exception as e:
                                logger.error(f"Error reading file: {e}")

                        if entry.upload_certificate_in_ialert_02 and entry.upload_certificate_in_ialert_02.name:
                            try:
                                file_content = entry.upload_certificate_in_ialert_02.read()
                                attachments.append((
                                    entry.upload_certificate_in_ialert_02.name.split('/')[-1],
                                    file_content,
                                    'application/octet-stream'
                                ))
                            except Exception as e:
                                logger.error(f"Error reading file: {e}")

                    # Create the email with attachments
                    send_email_with_config(
                        subject=subject,
                        html_message=html_message,
                        recipient_list=recipient_list,
                        cc_list=cc_list,
                        attachments=attachments if attachments else None,
                        config_type='AIS140'
                    )

                    logger.info(f"Completion email sent for closed Part-B form (Request ID: {entry.unique_id})")
                except Exception as e:
                    logger.error(f"Failed to send email for closed Part-B form (Request ID: {entry.unique_id}): {e}")

            return redirect(f"{reverse('part_b_form', args=[entry.id])}?submitted=1")
        else:
            # Capture form errors for display
            error_message = "Form validation failed. Please fix the errors below."
            error_reasons = "|".join(
                f"{field}: {', '.join(str(e) for e in errors)}"
                for field, errors in form.errors.items()
            )
            logger.error(f"Part B Form errors: {form.errors}")
    else:
        form = PartBForm(instance=entry)

    # Check for success redirect (after form submission and re-render)
    if request.GET.get('submitted') == '1':
        show_success_modal = True
        success_message = entry.unique_id or entry.id

    return render(request, 'AIS140_FLOW/part_b_form.html', {
        'form': form,
        'part_a_data': part_a_data,
        'is_read_only': is_read_only,
        'show_success_modal': show_success_modal,
        'success_message': success_message,
        'error_message': error_message,
        'error_reasons': error_reasons,
    })


def success_page(request):
    return render(request, 'AIS140_FLOW/success.html')



def download_part_b_csv(request):

    # File name
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    filename = f'AIS140_Data_{timestamp}.csv'

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # CSV Header -> Model Field mapping
    field_map = {
        'Unique ID': 'unique_id',
        'Date of Request': 'date_of_request',
#        'Assigned To Engineer Date': 'Customer_assigned_date',
#        'Resp Engineer': 'assigned_engineer_email',
        'State': 'state',
#        'Request Type': 'request_type',
        'Chassis No': 'vin_no',
#        'PSN No': 'psn',
        'Completion Status': 'completion_status',
        'Update to A.L': 'Update_to_AL_API',
        'Completion Date': 'completion_date',
        'D2 Remarks': 'd2',
        'D2 Closure': 'D2_closure',

        'D1 Remarks': 'd1',
        'D1 Closure': 'D1_closure',
        'Reassigned to DTIL':'reupdated_request_al',
        'Dealer Name': 'dealer_name',
        'RTO Code': 'rto_code',
        'Customer Name': 'customer_name',

#        'D1 Comments': 'D1_comments',
#        'D1 Engineer': 'D1_engineer',
#        'D2 Comments': 'D2_comments',
#        'D2 Engineer': 'D2_engineer',


#        'AL Remarks':'AL_remarks',
#        'AL Comments':'AL_comments',
#        'Engine No': 'engine',
#        'Device Model': 'device_mode',
#        'IMEI No': 'imei_no',
#        'Vehicle Regn No': 'vehicle_no',
#        'Vehicle Model': 'vehicle_model',
        'Customer Phone No': 'customer_phone',
        'Customer Alternate Phone No': 'Customer_Alternate_number',
        'Customer Address': 'Cust_veh_Regn_Address',
#        'Manufacturing Year':'manufacturing_year',
#        'Vehicle Reg No':'vehicle_no',
#        'RTO Name': 'rto_name',
        'Dealer Contact NO':'Dealer_Contact',
#        'Category': 'category',
#        'Remarks': 'remarks',
#        'Ticket Through':'ticket_through',
#        'Temporary Certificate Required': 'temp_cert_reqd',
#        'Temporary Certficate Raised By':'temp_raised_by',
#        'Temporary Certificate Date': 'temp_cert_date',
#        'Temporary certificate': 'upload_certificate_in_ialert',
#        'Permanent Certficate Raised By':'perm_raised_by',
#        'Permanent Certificate Date': 'permanent_cert_date',
#        'Permanent certificate': 'upload_certificate_in_ialert_01',
#        'Vahan Certificate': 'upload_certificate_in_ialert_02',

#        'Total TAT': 'total_tat',
#        'Completion Start Date': 'certification_start_date',
    }
    datetime_fields_ist = {
        'date_of_request',
        'Customer_assigned_date',
        'D1_closure',
        'D2_closure',
        'completion_date',
        'reupdated_request_al',
        'temp_cert_date',
        'permanent_cert_date',
        'certification_start_date',
        'certification_end_date',
    }


    # Selected columns
    columns = request.GET.get('columns', '').split(',')
    if columns == [''] or not columns:
        fieldnames = list(field_map.keys())
    else:
        fieldnames = [col for col in columns if col in field_map]

    # Base queryset (IMPORTANT FIX: use values directly)
    queryset = AIS140Request.objects.all()

    # Log initial count
    logger.info(f"Download CSV - Initial total records: {queryset.count()}")

    # Filters - with logging
    state = request.GET.get('state')
    if state and state.strip():
        logger.info(f"Download CSV - Filtering by state: '{state}'")
        queryset = queryset.filter(state=state)
        logger.info(f"Download CSV - After state filter: {queryset.count()} records")

    if request.GET.get('chassis_no'):
        queryset = queryset.filter(vin_no__icontains=request.GET['chassis_no'])
        logger.info(f"Download CSV - After chassis_no filter: {queryset.count()} records")

    if request.GET.get('psn_no'):
        queryset = queryset.filter(psn__icontains=request.GET['psn_no'])
        logger.info(f"Download CSV - After psn_no filter: {queryset.count()} records")

    if request.GET.get('customer_name'):
        queryset = queryset.filter(customer_name__icontains=request.GET['customer_name'])

    if request.GET.get('assigned_engineer_email'):
        queryset = queryset.filter(assigned_engineer_email=request.GET['assigned_engineer_email'])
        logger.info(f"Download CSV - After assigned_engineer filter: {queryset.count()} records")

    if request.GET.get('completion_date_from'):
        queryset = queryset.filter(completion_date__gte=request.GET['completion_date_from'])

    if request.GET.get('completion_date_to'):
        queryset = queryset.filter(completion_date__lte=request.GET['completion_date_to'])

    if request.GET.get('category'):
        queryset = queryset.filter(category=request.GET['category'])

    if request.GET.get('date_of_request_from'):
        queryset = queryset.filter(date_of_request__gte=request.GET['date_of_request_from'])

    if request.GET.get('date_of_request_to'):
        queryset = queryset.filter(date_of_request__lte=request.GET['date_of_request_to'])

    if request.GET.get('unique_id'):
        queryset = queryset.filter(unique_id__icontains=request.GET['unique_id'])

    # Handle completion_status filter - the critical one
    completion_status = request.GET.getlist('completion_status')
    # Filter out empty strings to handle "nothing selected" case
    completion_status = [s for s in completion_status if s.strip()]

    logger.info(f"==================== CSV DOWNLOAD DEBUG ====================")
    logger.info(f"All GET parameters: {dict(request.GET)}")
    logger.info(f"Received completion_status values: {completion_status}")
    logger.info(f"Total selected statuses: {len(completion_status)}")
    logger.info(f"Queryset count BEFORE completion_status filter: {queryset.count()}")

    if completion_status:
        queryset = queryset.filter(completion_status__in=completion_status)
        logger.info(f"Queryset count AFTER completion_status filter: {queryset.count()}")
    else:
        logger.info(f"No completion_status filter applied (empty list)")

    logger.info(f"FINAL CSV export record count: {queryset.count()}")
    logger.info(f"===========================================================")


    #  fetch only required fields & avoid model conversion
    queryset = queryset.values(*field_map.values())

    writer = csv.DictWriter(response, fieldnames=fieldnames)
    writer.writeheader()

    # Use iterator() for large data safety
    for entry in queryset.iterator():

        row = {}

        for col in fieldnames:
            db_field = field_map[col]
            value = entry.get(db_field)

            if value is None:
                row[col] = ''
            else:
                # Check if field needs IST conversion
                if db_field in datetime_fields_ist and isinstance(value, (datetime, date)):
                    # Convert UTC to IST
                    if isinstance(value, datetime):
                        # Ensure timezone aware
                        if timezone.is_naive(value):
                            value = timezone.make_aware(value)
                        # Convert to IST
                        ist_value = value.astimezone(IST)
                        row[col] = ist_value.strftime("%d-%m-%Y %H:%M:%S")
                    else:
                        row[col] = value.strftime("%d-%m-%Y")
                elif isinstance(value, (datetime, date, time)):
                    row[col] = value.strftime("%d-%m-%Y %H:%M:%S")
                else:
                    row[col] = str(value)

        writer.writerow(row)

    return response


def download_full_csv(request):

    # File name
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    filename = f'AIS140_Full_Data_{timestamp}.csv'

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # CSV Header -> Model Field mapping (Full fields)
    field_map = {
        'Unique ID': 'unique_id',
        'Date of Request': 'date_of_request',
        'Assigned To Engineer Date': 'Customer_assigned_date',
        'Resp Engineer': 'assigned_engineer_email',
        'State': 'state',
        'Request Type': 'request_type',
        'Chassis No': 'vin_no',
        'PSN No': 'psn',
        'D1 Remarks': 'd1',
        'D1 Comments': 'D1_comments',
        'D1 Engineer': 'D1_engineer',
        'D1 Closure Timestamp': 'D1_closure',
        'D2 Remarks': 'd2',
        'D2 Comments': 'D2_comments',
        'D2 Engineer': 'D2_engineer',
        'D2 Closure Timestamp': 'D2_closure',
        'Completion Status': 'completion_status',
        'Update to A.L': 'Update_to_AL_API',
        'Completion Date': 'completion_date',
        'Reassigned to DTIL':'reupdated_request_al',
        'AL Remarks':'AL_remarks',
        'AL Comments':'AL_comments',
        'Engine No': 'engine',
        'Device Model': 'device_mode',
        'IMEI No': 'imei_no',
        'Vehicle Regn No': 'vehicle_no',
        'Vehicle Model': 'vehicle_model',
        'Customer Name': 'customer_name',
        'Customer Phone No': 'customer_phone',
        'Customer Alternate Phone No': 'Customer_Alternate_number',
        'Customer Address': 'Cust_veh_Regn_Address',
        'Manufacturing Year':'manufacturing_year',
        'Vehicle Reg No':'vehicle_no',
        'RTO Name': 'rto_name',
        'RTO Code': 'rto_code',
        'Dealer Name': 'dealer_name',
        'Dealer Contact NO':'Dealer_Contact',
        'Category': 'category',
        'Remarks': 'remarks',
        'Ticket Through':'ticket_through',
        'Temporary Certificate Required': 'temp_cert_reqd',
        'Temporary Certficate Raised By':'temp_raised_by',
        'Temporary Certificate Date': 'temp_cert_date',
        'Temporary certificate': 'upload_certificate_in_ialert',
        'Permanent Certficate Raised By':'perm_raised_by',
        'Permanent Certificate Date': 'permanent_cert_date',
        'Permanent certificate': 'upload_certificate_in_ialert_01',
        'Vahan Certificate': 'upload_certificate_in_ialert_02',
        'Total TAT': 'total_tat',
        'Completion Start Date': 'certification_start_date',
        'Completion End Date': 'certification_end_date',
    }
    datetime_fields_ist = {
        'date_of_request',
        'Customer_assigned_date',
        'D1_closure',
        'D2_closure',
        'completion_date',
        'reupdated_request_al',
        'temp_cert_date',
        'permanent_cert_date',
        'certification_start_date',
        'certification_end_date',
    }

    # Selected columns
    columns = request.GET.get('columns', '').split(',')
    if columns == [''] or not columns:
        fieldnames = list(field_map.keys())
    else:
        fieldnames = [col for col in columns if col in field_map]

    # Base queryset (IMPORTANT FIX: use values directly)
    queryset = AIS140Request.objects.all()

    # Log initial count
    logger.info(f"Download Full CSV - Initial total records: {queryset.count()}")

    # Filters - with logging
    state = request.GET.get('state')
    if state and state.strip():
        logger.info(f"Download Full CSV - Filtering by state: '{state}'")
        queryset = queryset.filter(state=state)
        logger.info(f"Download Full CSV - After state filter: {queryset.count()} records")

    if request.GET.get('chassis_no'):
        queryset = queryset.filter(vin_no__icontains=request.GET['chassis_no'])
        logger.info(f"Download Full CSV - After chassis_no filter: {queryset.count()} records")

    if request.GET.get('psn_no'):
        queryset = queryset.filter(psn__icontains=request.GET['psn_no'])
        logger.info(f"Download Full CSV - After psn_no filter: {queryset.count()} records")

    if request.GET.get('customer_name'):
        queryset = queryset.filter(customer_name__icontains=request.GET['customer_name'])

    if request.GET.get('assigned_engineer_email'):
        queryset = queryset.filter(assigned_engineer_email=request.GET['assigned_engineer_email'])
        logger.info(f"Download Full CSV - After assigned_engineer filter: {queryset.count()} records")

    if request.GET.get('completion_date_from'):
        queryset = queryset.filter(completion_date__gte=request.GET['completion_date_from'])

    if request.GET.get('completion_date_to'):
        queryset = queryset.filter(completion_date__lte=request.GET['completion_date_to'])

    if request.GET.get('category'):
        queryset = queryset.filter(category=request.GET['category'])

    if request.GET.get('date_of_request_from'):
        queryset = queryset.filter(date_of_request__gte=request.GET['date_of_request_from'])

    if request.GET.get('date_of_request_to'):
        queryset = queryset.filter(date_of_request__lte=request.GET['date_of_request_to'])

    if request.GET.get('unique_id'):
        queryset = queryset.filter(unique_id__icontains=request.GET['unique_id'])

    # Handle completion_status filter - the critical one
    completion_status = request.GET.getlist('completion_status')
    # Filter out empty strings to handle "nothing selected" case
    completion_status = [s for s in completion_status if s.strip()]

    logger.info(f"==================== FULL CSV DOWNLOAD DEBUG ====================")
    logger.info(f"All GET parameters: {dict(request.GET)}")
    logger.info(f"Received completion_status values: {completion_status}")
    logger.info(f"Total selected statuses: {len(completion_status)}")
    logger.info(f"Queryset count BEFORE completion_status filter: {queryset.count()}")

    if completion_status:
        queryset = queryset.filter(completion_status__in=completion_status)
        logger.info(f"Queryset count AFTER completion_status filter: {queryset.count()}")
    else:
        logger.info(f"No completion_status filter applied (empty list)")

    logger.info(f"FINAL FULL CSV export record count: {queryset.count()}")
    logger.info(f"===========================================================")


    #  fetch only required fields & avoid model conversion
    queryset = queryset.values(*field_map.values())

    writer = csv.DictWriter(response, fieldnames=fieldnames)
    writer.writeheader()

    # Use iterator() for large data safety
    for entry in queryset.iterator():

        row = {}

        for col in fieldnames:
            db_field = field_map[col]
            value = entry.get(db_field)

            if value is None:
                row[col] = ''
            else:
                # Check if field needs IST conversion
                if db_field in datetime_fields_ist and isinstance(value, (datetime, date)):
                    # Convert UTC to IST
                    if isinstance(value, datetime):
                        # Ensure timezone aware
                        if timezone.is_naive(value):
                            value = timezone.make_aware(value)
                        # Convert to IST
                        ist_value = value.astimezone(IST)
                        row[col] = ist_value.strftime("%d-%m-%Y %H:%M:%S")
                    else:
                        row[col] = value.strftime("%d-%m-%Y")
                elif isinstance(value, (datetime, date, time)):
                    row[col] = value.strftime("%d-%m-%Y %H:%M:%S")
                else:
                    row[col] = str(value)

        writer.writerow(row)

    return response


def real_time_page(request):
    completion_status = request.GET.getlist('completion_status')
    assigned_engineer_email = request.GET.get('assigned_engineer_email', '')
    state = request.GET.get('state', '')
    chassis_no = request.GET.get('chassis_no', '')
    psn_no = request.GET.get('psn_no', '')
    customer_name = request.GET.get('customer_name', '')
    completion_date_from = request.GET.get('completion_date_from', '')
    completion_date_to = request.GET.get('completion_date_to', '')
    category = request.GET.get('category', '')
    date_of_request_from = request.GET.get('date_of_request_from', '')
    date_of_request_to = request.GET.get('date_of_request_to', '')
    unique_id = request.GET.get('unique_id', '')
    page = int(request.GET.get('page', 1))

    entries = AIS140Request.objects.all()
    if completion_status:
        entries = entries.filter(completion_status__in=completion_status)
    if assigned_engineer_email:
        entries = entries.filter(assigned_engineer_email=assigned_engineer_email)
    if state:
        entries = entries.filter(state__icontains=state)
    if chassis_no:
        entries = entries.filter(vin_no__icontains=chassis_no)
    if psn_no:
        entries = entries.filter(psn__icontains=psn_no)
    if customer_name:
        entries = entries.filter(customer_name__icontains=customer_name)
    if completion_date_from:
        entries = entries.filter(completion_date__gte=completion_date_from)
    if completion_date_to:
        entries = entries.filter(completion_date__lte=completion_date_to)
    if category:
        entries = entries.filter(category__icontains=category)
    if date_of_request_from:
        entries = entries.filter(date_of_request__gte=date_of_request_from)
    if date_of_request_to:
        entries = entries.filter(date_of_request__lte=date_of_request_to)
    if unique_id:
        entries = entries.filter(unique_id__icontains=unique_id)

    entries = entries.order_by('-date_of_request')

    # Pagination
    paginator = Paginator(entries, 25)
    try:
        paged_entries = paginator.page(page)
    except PageNotAnInteger:
        paged_entries = paginator.page(1)
    except EmptyPage:
        paged_entries = paginator.page(paginator.num_pages)


    entry_list = []

    for entry in paged_entries:
        sw_sch_date = entry.sw_sch_date
        completion_date = entry.completion_date
        total_tat = ''

        if sw_sch_date and completion_date:
            try:
                if timezone.is_naive(sw_sch_date):
                    sw_sch_date = timezone.make_aware(sw_sch_date)

                if timezone.is_naive(completion_date):
                    completion_date = timezone.make_aware(completion_date)

                diff = completion_date - sw_sch_date
                total_seconds = int(diff.total_seconds())

                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                seconds = total_seconds % 60

                total_tat = f"{hours:02}:{minutes:02}:{seconds:02}"

            except Exception:
                total_tat = ''

        if entry.reupdated_request_al:
            updated_dt = entry.reupdated_request_al
            if timezone.is_naive(updated_dt):
                updated_dt = timezone.make_aware(updated_dt)
            entry.is_new = (timezone.now() - updated_dt).days < 3
        else:
            entry.is_new = False

        entry.entry_total_tat = total_tat

        entry.is_new = False
        if entry.reupdated_request_al:
            updated_dt = entry.reupdated_request_al
            if timezone.is_naive(updated_dt):
                updated_dt = timezone.make_aware(updated_dt)
            entry.is_new = (timezone.now() - updated_dt).days < 3

        entry_list.append(entry)

    unique_states = AIS140Request.objects.values_list('state', flat=True).distinct()
    unique_assigned_engineer_email = AIS140Request.objects.values_list('assigned_engineer_email', flat=True).distinct()
    unique_categories = AIS140Request.objects.values_list('category', flat=True).distinct()
    unique_completion_statuses = AIS140Request.objects.values_list('completion_status', flat=True).distinct()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        table_data = render_to_string(
            'AIS140_FLOW/partials/real_time_table_rows.html',
            {'entries': entry_list}
        )
        return JsonResponse({
            'table_data': table_data,
            'page': paged_entries.number,
            'num_pages': paginator.num_pages,
            'has_next': paged_entries.has_next(),
            'has_previous': paged_entries.has_previous(),
        })
    return render(request, 'AIS140_FLOW/real_time_page.html', {
        'entries': entry_list,
        'unique_states': unique_states,
        'unique_assigned_to': unique_assigned_engineer_email,
        'unique_categories': unique_categories,
        'unique_completion_statuses': unique_completion_statuses,
        'page': paged_entries.number,
        'num_pages': paginator.num_pages,
        'has_next': paged_entries.has_next(),
        'has_previous': paged_entries.has_previous(),
    })
import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
import pytz

logger = logging.getLogger(__name__)

@csrf_exempt
def api_create_ais140_ticket(request):
    if request.method == 'POST':
        try:
            # Decode raw body
            raw_body = request.body.decode('utf-8')
            logger.info(f"AIS140 Ticket API - Raw Payload: {raw_body}")

            data = json.loads(raw_body)

            # Required fields from customer payload
            required_fields = [
                'request_id',
                'request_date', 'state', 'chassis_number', 'engine_no', 'obu_id',
                'vehicle_reg_no', 'vehicle_model','customer_name',
                'customer_mobile_number','pan_no', 'aadhar_no', 'mfg_year',
                'rto_name', 'rto_code', 'dealer_name', 'dealer_code'
            ]

            for field in required_fields:
                if field not in data:
                    logger.error(f"Missing field in payload: {field}")
                    return JsonResponse(
                        {'success': False, 'error': f'Missing field: {field}'},
                        status=400
                    )

            # Create entry
            entry = AIS140Request.objects.create(
                request_id=data.get('request_id'),
                date_of_request=now().astimezone(pytz.timezone('Asia/Kolkata')),
                state=data.get('state'),
                vin_no=data.get('chassis_number'),
                engine=data.get('engine_no'),
                psn=data.get('obu_id'),
                vehicle_no=data.get('vehicle_reg_no'),
                vehicle_model=data.get('vehicle_model'),
                customer_name=data.get('customer_name'),
                customer_phone=data.get('customer_mobile_number'),
                Customer_Alternate_number=data.get('customer_alternate_number'),
                Customer_Email_ID=data.get('customer_email_id'),
                Cust_veh_Regn_Address=data.get('cust_veh_regn_address'),
                Cust_veh_Regn_Pincode=data.get('cust_veh_regn_pincode'),
                pan_card=data.get('pan_no'),
                aadhar_card=data.get('aadhar_no'),
                manufacturing_year=data.get('mfg_year'),
                request_type=data.get('ais140_type'),       #
                AIS140_Type=data.get('ais140_type').strip().title(), #
                rto_name=data.get('rto_name'),
                rto_code=data.get('rto_code'),
                dealer_name=data.get('dealer_name'),
                Dealer_Contact=data.get('dealer_contact'),
                Dealer_Location=data.get('dealer_location'),
                Dealer_mail=data.get('dealer_email_id'),
                TSM_mail=data.get('tsm_email_id'),
                Ialert_Email_ID=data.get('ialert_email_id'),
                dealer_code=data.get('dealer_code'),
                sos_fitment_date=data.get('sos_confirmed_on'),
                zone=data.get('zoneName'),

                category=data.get('category'),
                ticket_through="A.L API",
                assigned_engineer_email="--"


            )

            logger.info(f"AIS140 Ticket Created Successfully. Unique ID: {entry.unique_id}")

            return JsonResponse({'success': True, 'unique_id': entry.unique_id})

        except Exception as e:
            logger.exception("Error while creating AIS140 ticket")
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Only POST allowed'}, status=405)
@csrf_exempt
def api_update_ais140_remarks(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST only'}, status=405)
    try:
        data = json.loads(request.body.decode('utf-8'))
        logger.info(f"AIS140 Ticket API Data Upated - Raw Payload: {data}")

        request_id = data.get('request_id')
        vin_no = (data.get('vin_no') or '').strip()
        AL_remarks = (data.get('remarks') or '').strip()
        AL_comments = (data.get('comments') or '').strip()
        if not request_id:
            return JsonResponse({'success': False, 'error': 'request_id is mandatory'}, status=400)
        if not vin_no:
            return JsonResponse({'success': False, 'error': 'vin_no is mandatory'}, status=400)
        if not AL_remarks:
            return JsonResponse({'success': False, 'error': 'remarks is mandatory'}, status=400)

        entry = AIS140Request.objects.get(request_id=request_id)

        if entry.vin_no != vin_no:
            logger.warning("VIN mismatch: request_id=%s expected=%s got=%s",
                          request_id, entry.vin_no, vin_no)
            return JsonResponse({'success': False, 'error': 'VIN mismatch'}, status=400)

        entry.AL_remarks = AL_remarks
        entry.AL_comments = AL_comments
        entry.reupdated_request_al=now().astimezone(pytz.timezone('Asia/Kolkata'))
        entry.completion_status="Pending"
        entry.save()

        # Send email notification to assigned engineer
        try:
            if entry.assigned_engineer_email and entry.assigned_engineer_email != "--":
                engineer_email = resolve_engineer_email(entry.assigned_engineer_email)
                subject = f"AIS140 AL Remarks Updated - {entry.unique_id} ({entry.vin_no})"
                html_message = render_to_string('emails/remarks_updated_email.html', {
                    'entry': entry,
                    'AL_remarks': AL_remarks,
                    'AL_comments': AL_comments,
                    'site_domain': request.build_absolute_uri('/')[:-1],
                })
                recipient_list = [engineer_email, "narendrareddyg@danlawtech.com", "rajendrans@danlawtech.com"]
                recipient_list = [email for email in recipient_list if email]  # Remove empty/None values
                cc_list = ['sales@danlawtech.com', "dilipkumarn@danlawtech.com"]

                send_email_with_config(
                    subject=subject,
                    html_message=html_message,
                    recipient_list=recipient_list,
                    cc_list=cc_list,
                    config_type='AIS140'
                )
                logger.info(f"Remarks update email sent to engineer for request_id={request_id}, unique_id={entry.unique_id}")
            else:
                logger.warning(f"No engineer assigned for request_id={request_id}, skipping email")
        except Exception as e:
            logger.error(f"Failed to send remarks update email for request_id={request_id}: {e}")

        logger.info("Updated remarks for request_id=%s vin=%s", request_id, entry.vin_no)

        return JsonResponse({
            'success': True,
            'message': 'Remarks succesfully updated!',
            'request_id': entry.request_id
        }, status=200)

    except AIS140Request.DoesNotExist:
        logger.error("Ticket not found: request_id=%s", data.get('request_id'))
        return JsonResponse({'success': False, 'error': 'Ticket not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.exception("api_update_ais140_remarks failed")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@require_GET
def fetch_darby_communication_ais140(request, id):
    from django.shortcuts import get_object_or_404
    import requests

    try:
        entry = get_object_or_404(AIS140Request, id=id)
        vin = (getattr(entry, 'vin_no', '') or getattr(entry, 'vin', '')).strip().upper()
        logger.debug("fetch_darby_communication_ais140 - VIN: %s (entry.unique_id=%s)", entry.vin_no, entry.unique_id)
        if not vin:
            return JsonResponse({'success': False, 'error': 'VIN not available for this entry'}, status=400)

        api_url = "https://api.al.drivewithdarby.com/v1/assets/dynamic/search"
        headers = {
            "Authorization": "Bearer eyJhbGciOiJIUzM4NCJ9.eyJpc3MiOiJkYXJieSIsImp0aSI6ImJkNzVmYWIzLWNhNDktNDBiMi1iZGJjLThiYzJiMDllOTFlNyIsImlhdCI6MTc1MDg0NDc2OSwiZXhwIjoxNzgyMzgwNzY5LCJDSSI6NDIsIlVJIjoiMzFhZmUzMjgtZTIzYS00MDI2LWJkMGEtYmJkMzViMGRkODg0IiwiRU0iOiJWaXNod2FuYXRoLkdAYXNob2tsZXlsYW5kLmNvbSIsIlJJIjoiMWQ5MDllZTUtOWQ1ZS00Y2E3LWJjZmEtMzQ5YWUzM2YzMjIzIiwiVFkiOiJBRE1JTl9VU0VSIiwiRk4iOiJWaXNod2FuYXRoIiwiTE4iOiJHOiBEYW5sYXcgQXNzZXQgRHluYW1pYyBTZWFyY2giLCJQSSI6IjMxYWZlMzI4LWUyM2EtNDAyNi1iZDBhLWJiZDM1YjBkZDg4NCIsIlBOIjoiRGFubGF3IEFzc2V0IER5bmFtaWMgU2VhcmNoIiwiQUkiOiJjOWQ1YjViOS1lNjE4LTQ5OTktYmY1Mi1hNjQ4NTgwYjU0N2EiLCJBVCI6WyJBU1NFVDpSRUFEIiwiUkVQT1JUOlJFQUQiLCJMSVZFOlJFQUQiLCJDQU1QQUlHTjpSRUFEIiwiREFTSEJPQVJEOlJFQUQiXX0.LPPA6mVuKOH1L_KOvoe0r1anfuSMSjbuWyYdK7LVH82UGLKpQpsASMoSEHz81p0L",  # keep token secure
            "Content-Type": "application/json"
        }
        payload = {"assetType": "DEVICE", "filters": {"vin": [vin]}}

        resp = requests.post(api_url, headers=headers, json=payload, timeout=10)
        logger.info("Darby search – status=%s", resp.status_code)
        logger.debug("Darby request payload: %r", payload)
        resp.raise_for_status()
        data = resp.json()

        # parsing logic (existing)
        candidates = []
        if isinstance(data, dict):
            for key in ('data', 'assets', 'result', 'items'):
                if key in data and isinstance(data[key], list):
                    candidates.extend(data[key])
            if not candidates:
                for v in data.values():
                    if isinstance(v, list):
                        candidates.extend(v)
        elif isinstance(data, list):
            candidates = data

        iccid = ''
        imei = ''
        asset = None
        for item in candidates:
            if isinstance(item, dict) and ('iccid' in item or 'imei' in item):
                asset = item
                break

        if not asset:
            def find_in(obj):
                if isinstance(obj, dict):
                    if 'iccid' in obj or 'imei' in obj:
                        return obj
                    for v in obj.values():
                        res = find_in(v)
                        if res:
                            return res
                if isinstance(obj, list):
                    for el in obj:
                        res = find_in(el)
                        if res:
                            return res
                return None
            asset = find_in(data)

        if asset and isinstance(asset, dict):
            iccid = asset.get('iccid') or asset.get('iccid_no') or asset.get('iccidNumber') or ''
            imei  = asset.get('imei')  or asset.get('imei_no')   or asset.get('imeiNumber')   or ''
            productCode=asset.get('productCode') or asset.get('productCode') or asset.get('productCode') or ''

        # Always return raw payload for frontend inspection; keep success True so frontend can act
        return JsonResponse({
            'success': True,
            'iccid': iccid or '',
            'imei': imei or '',
            'productCode':productCode or '',
            'raw': data
        })
    except requests.RequestException as e:
        logger.error("Darby API request error: %s", e)
        return JsonResponse({'success': False, 'error': f'API request failed: {str(e)}'}, status=502)
    except Exception as e:
        logger.exception("Unexpected error in fetch_darby_communication_ais140")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

import requests
import logging
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)


# --------------------------------------------------
# 0️⃣ Send to Customer API
# --------------------------------------------------

def _send_to_customer_api(request, entry):
    """
    Send entry data to customer API.
    Returns dict with 'success' key.
    """
    logger.debug("sending to iAlert: request_id=%s vin_no=%s d1=%r comments=%r",
                 entry.request_id, entry.vin_no, entry.d1,
                 getattr(entry, "D1_comments", ""))
    logger.info("Sending to customer API from path: %s", request.path)
    try:
        result = upload_to_ialert(request, {
            "request_id": entry.request_id,
            "vin_no": entry.vin_no,
            "d1": entry.d1,
            "D1_comments": getattr(entry, 'D1_comments', ''),
        }, entry)
        return result
    except Exception as e:
        logger.exception("Error in _send_to_customer_api: %s", e)
        return {"success": False, "error": str(e)}


# --------------------------------------------------
# 1️⃣ Get iAlert Token
# --------------------------------------------------
def _get_ialert_token():
    token_url = "https://ialert2.ashokleyland.com/operation/ialertelite/api/login/generate-token"
    #            https://ialertuat.ashokleyland.com/operationuat/admin/api/login/generate-token
    token_header = {"token": "ZWJhMjljODM4Y2M3ZDgxMDk3MjA3ODdkMDFhNWIyMWE="}
#    token_header = {"token": "YjhhNjBlYmU4NDA3M2RhM2I0YzRhNDMxMzc1NjQxYTM="}
    try:
        resp = requests.get(token_url, headers=token_header, timeout=15)
        logger.debug("IAlert token endpoint status=%s body=%s", resp.status_code, resp.text)
        resp.raise_for_status()

        # Try JSON extraction first, then fallback to plain text
        token = None
        try:
            j = resp.json()
        except ValueError:
            j = None

        if j:
            if isinstance(j, dict):
                for key in ("token", "accessToken", "access_token", "data"):
                    if j.get(key) and isinstance(j.get(key), (str, int)):
                        token = j.get(key)
                        break
                if not token:
                    for container in ("data", "result", "response"):
                        c = j.get(container)
                        if isinstance(c, dict):
                            for key in ("token", "accessToken", "access_token"):
                                if c.get(key):
                                    token = c.get(key)
                                    break
                        if token:
                            break
            elif isinstance(j, str):
                token = j

        if not token:
            # fallback to plain text body (some APIs return raw token)
            text = (resp.text or "").strip()
            if text:
                logger.debug("IAlert token endpoint returned non-JSON text; using resp.text")
                token = text

        if token:
            token = str(token).strip()
            logger.debug("IAlert token extracted (len=%d)", len(token))
            return token

        logger.error("IAlert token not found in response; body=%s", resp.text[:1000])
        return None
    except requests.exceptions.RequestException as e:
        logger.exception("IAlert token request failed: %s", e)
        return None
import os
import requests
import logging
import base64
import json

logger = logging.getLogger(__name__)

def upload_to_ialert(request, data, entry=None):

    token = _get_ialert_token()
    if not token:
        return {"success": False, "error": "Token generation failed"}

    url = "https://ialert2.ashokleyland.com/operation/ialertelite/api/ais140/certificate-upload"
#"https://ialertuat.ashokleyland.com/operationuat/admin/api/ais140/certificate-upload"
    headers = {"Authorization": token}

    payload = {
        "request_id": data.get("request_id"),
        "vin_no": str(data.get("vin_no", "")).strip(),
        "remarks": (entry.d1 if entry.Update_to_AL_API == "D1" else entry.d2) if entry else "",
        "comments":(entry.D1_comments if entry.Update_to_AL_API == "D1" else entry.D2_comments) if entry else "",
    }

    if entry and entry.Update_to_AL_API in ["Temporary", "Permanent", "Temp + Perm"]:
        payload["remarks"] = ""
        payload["comments"] = ""

    logger.info("Payload sending to iAlert: %s", payload)

    # File mapping
    if entry and entry.Update_to_AL_API == "Temporary":
        mapping = (
            ("upload_certificate_in_ialert", "temp_certificate"),
            ("upload_certificate_in_ialert_01", "vltd_certificate_1"),
        )

    elif entry and entry.Update_to_AL_API == "Permanent":
        mapping = (
            ("upload_certificate_in_ialert_01", "vltd_certificate_1"),
            ("upload_certificate_in_ialert_02", "vltd_certificate_2"),
        )

    elif entry and entry.Update_to_AL_API == "Temp + Perm":
        mapping = (
            ("upload_certificate_in_ialert", "temp_certificate"),
            ("upload_certificate_in_ialert_01", "vltd_certificate_1"),
            ("upload_certificate_in_ialert_02", "vltd_certificate_2"),
        )

    else:
        mapping = ()

    files = {}
    debug_json = {"payload": payload, "files": {}}

    for fieldname, postname in mapping:

        f = None

        # Case 1: File from request
        if request is not None:
            f = request.FILES.get(fieldname)

        if f:
            f.seek(0)

            file_bytes = f.read()
            size = len(file_bytes)

            logger.info("Sending uploaded file: %s size=%s", f.name, size)

            # Store debug JSON
            debug_json["files"][postname] = {
                "filename": f.name,
                "size_bytes": size,
                "blob_base64_preview": base64.b64encode(file_bytes[:200]).decode()
            }

            f.seek(0)

            files[postname] = (f.name, f, f.content_type or "application/pdf")
            continue

        # Case 2: File from DB
        if entry is not None:

            f_field = getattr(entry, fieldname, None)

            if f_field and f_field.name:

                try:

                    file_path = f_field.path

                    if os.path.exists(file_path):

                        size = os.path.getsize(file_path)

                        logger.info("Reading file from disk: %s size=%s", file_path, size)

                        fp = open(file_path, "rb")

                        file_bytes = fp.read()

                        debug_json["files"][postname] = {
                            "filename": os.path.basename(file_path),
                            "size_bytes": size,
                            "blob_base64_preview": base64.b64encode(file_bytes[:200]).decode()
                        }

                        fp.seek(0)

                        files[postname] = (
                            os.path.basename(file_path),
                            fp,
                            "application/pdf"
                        )

                    else:
                        logger.error("File does not exist: %s", file_path)

                except Exception as e:
                    logger.error("Error opening file %s: %s", file_path, e)

    logger.info("Files prepared for upload: %s", list(files.keys()))

    # Save full debug JSON
    try:
        logger.info(
            "Full Payload + File Debug JSON: %s",
            json.dumps(debug_json)[:5000]  # limit size
        )
    except Exception as e:
        logger.error("Failed to log debug JSON: %s", e)

    try:

        resp = requests.post(
            url,
            data=payload,
            files=files if files else None,
            headers=headers,
            timeout=30
        )

        logger.info("iAlert response status: %s", resp.status_code)
        logger.info("iAlert response body: %s", resp.text)

        resp.raise_for_status()

        return {
            "success": True,
            "status_code": resp.status_code,
            "response": resp.text
        }

    except requests.RequestException as e:

        logger.exception("Upload failed: %s", e)

        return {
            "success": False,
            "error": str(e),
            "response": getattr(e.response, "text", None)
        }

    finally:

        for v in files.values():

            file_obj = v[1]

            if hasattr(file_obj, "close"):
                try:
                    file_obj.close()
                except:
                    pass