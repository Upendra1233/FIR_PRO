from django.shortcuts import render, get_object_or_404, redirect
from django.core.mail import EmailMessage, send_mail
from django.conf import settings
from django.http import JsonResponse
from .forms import DirectCallForm, ManagerForm, EngineerForm, FeedbackForm,  DeviceRepairForm, AltDeviceForm, EngineerReviewForm
from .models import DirectCall
import logging
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import csv
from django.http import HttpResponse
from datetime import datetime, timedelta, date, time
from django.utils.timezone import localtime, now, make_aware
import traceback
from django.utils import timezone
import pytz
import requests
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.db.models import Count
from django.templatetags.static import static
import base64
import os
from django.core.paginator import Paginator
from django.db.models import Q
import json
from django.utils.dateparse import parse_datetime
from .generate_device_repair_request_pdf import generate_device_repair_request_pdf
from django import forms
from django.core.files.storage import default_storage
from django.contrib.staticfiles import finders
import mimetypes

logger = logging.getLogger(__name__)

TRIGGER_REMARKS = {
    "D1 Followup - Waiting For Vehicle Support",
    "D2 Followup - Waiting For Vehicle Support",
    "D3 Followup - Waiting For Vehicle Support",
}


def manager_form(request, id=None):
    entry = None
    if id:
        entry = get_object_or_404(DirectCall, id=id)

    if request.method == 'POST':
        try:
            post_data = request.POST.copy()

            # Handle "Others" logic for dropdowns
            dropdown_fields = ['complaint_raised', 'complaint_raised_through', 'complaint_assigned_to', 'call_type']
            for field in dropdown_fields:
                if post_data.get(field) == 'others':
                    post_data[field] = post_data.get(f"{field}_other", 'others')

            form = ManagerForm(post_data, request.FILES, instance=entry)
            if form.is_valid():

                # copy instance (attach uploaded file if provided)
                entry = form.save(commit=False)
                uploaded_file = request.FILES.get('upload_file')
                if uploaded_file:
                    entry.upload_file = uploaded_file
                try:
                    previous_date = entry.date_of_complaint
                    entry.date_of_complaint = now()
                    logger.info("Overriding date_of_complaint from %s to %s for %s", previous_date, entry.date_of_complaint, getattr(entry, 'unique_id', 'N/A'))
                except Exception as e:
                    logger.exception("Failed to override date_of_complaint: %s", e)
                    entry.date_of_complaint = now()
                entry.save()
                start_time = entry.date_of_complaint + timedelta(hours=6, minutes=30)
                end_time   = entry.date_of_complaint + timedelta(hours=6, minutes=45)

                tech_support_needed = f"{start_time.strftime('%d-%m-%Y %I:%M %p')} TO {end_time.strftime('%I:%M %p')}"
                context = {
                    'entry': entry,
                    'site_domain': request.build_absolute_uri('/').rstrip('/'),
                    'tech_support_needed': tech_support_needed,
                }

                subject = f"{entry.unique_id} CRSC Assigned to {entry.complaint_assigned_to} ON {entry.vin}"
                email_body = render_to_string('direct_calls/manager_email.html', context)

                engineer_email = entry.submitted_to_email
                sales_emails = [
                    'rajendrans@danlawtech.com',
                    'yoganandam@danlawtech.com',
                    'sales@danlawtech.com',
                    'sivanambirajant@danlawtech.com'
                ]

                email = EmailMessage(subject, email_body, settings.DEFAULT_FROM_EMAIL, [engineer_email], cc=sales_emails)
                email.content_subtype = 'html'

                if uploaded_file:
                    try:
                        email.attach(uploaded_file.name, uploaded_file.read(), uploaded_file.content_type)
                        logger.info(f"File {uploaded_file.name} attached successfully.")
                    except Exception as e:
                        logger.error(f"Failed to attach file: {e}\n{traceback.format_exc()}")
                else:
                    logger.warning("No file uploaded to attach.")

                logger.info("Attempting to send manager assignment email to %s (cc: %s)", engineer_email, sales_emails)
                try:
                    email.send()
                    logger.info("Manager assignment email sent.")
                except Exception as e:
                    logger.error("Error sending manager assignment email: %s\n%s", e, traceback.format_exc())

                # Send customer email if available
                customer_subject = f"Ticket Created: {entry.unique_id} ON Your Request"
                customer_email_body = render_to_string('direct_calls/customer_email.html', context)
                sales_cc = ["sales@danlawtech.com", "yoganandam@danlawtech.com", "eliyasp@danlawtech.com",
                            "narendrareddyg@danlawtech.com", "rajendrans@danlawtech.com"]
                cust_emails =  [e for e in [email.strip() for email in (entry.customer_mail_id or '').split(';') if email.strip()] + [entry.submitted_to_email] if e]

                if cust_emails:
                    try:
                        customer_email_message = EmailMessage(customer_subject, customer_email_body, settings.DEFAULT_FROM_EMAIL, cust_emails, cc=sales_cc)
                        customer_email_message.content_subtype = 'html'
                        customer_email_message.send()
                        logger.info("Customer email sent to %s", cust_emails)
                    except Exception as e:
                        logger.error("Error sending customer email: %s\n%s", e, traceback.format_exc())
                else:
                    logger.warning("No customer email available to send notification.")

                # Respond according to request type
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': True})
                messages.success(request, 'Saved successfully.')
                return redirect(request.path)
            else:
                logger.error("Form errors: %s", form.errors)
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'errors': form.errors})
        except Exception as e:
            logger.exception("Unexpected error in manager_form: %s", traceback.format_exc())
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'An unexpected error occurred. Please try again.'})
            messages.error(request, 'An unexpected error occurred. Please try again.')

    else:
        form = ManagerForm(instance=entry)

    return render(request, 'direct_calls/manager_form.html', {'form': form, 'instance': entry})
def calculate_tat(start, end):
    if not start or not end:
        return '--'
    diff = end - start
    if diff.total_seconds() < 0:
        return '--'
    hours, remainder = divmod(diff.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

# helper to set Latest_update to max of D1/D2/D3 closure datetimes (does not save)
def set_latest_update_from_closures(instance):
    try:
        candidates = [d for d in (
            getattr(instance, 'D1_closure_date', None),
            getattr(instance, 'D2_closure_date', None),
            getattr(instance, 'D3_closure_date', None)
        ) if d]
        instance.Latest_update = max(candidates) if candidates else None
    except Exception as e:
        logger.exception("Failed to compute Latest_update: %s", e)
    return instance

def engineer_form(request, id):
    entry = get_object_or_404(DirectCall, id=id)
    is_closed = entry.call_status in [
            "Resolved", "Closed", "Closed-CI", "Cancelled", "FIR-Resolved","Resale",
            "FIR-Repair", "FIR-Replace", "FIR-Replace_Repair", "Reject","D1-D2-D3 Completed","Auto Resolved"
    ]

    form_readonly = is_closed
    if request.method == 'POST':
        post_data = request.POST.copy()
        form = EngineerForm(post_data, request.FILES, instance=entry)

        if form.is_valid():
            entry = form.save(commit=False)
            if 'upload_file_01' in request.FILES:
                entry.upload_file_01 = request.FILES['upload_file_01']

            call_status = post_data.get('call_status')
            entry.call_status = call_status

            CLOSED_STATUSES = {
                "Resolved", "Closed", "Closed-CI", "Cancelled", "Resale",
                "FIR-Repair", "FIR-Replace", "FIR-Replace_Repair", "Reject",
                "D1-D2-D3 Completed", "Auto Resolved"
            }

            ALLOWED_CLOSURE_REMARKS = {
                # D3 specific
                "D3 - CONTACT DETAILS WRONG",
                "D3 - CUSTOMER ISSUE - DASHBOARD MODIFICATION",
                "D3 - CUSTOMER ISSUE - FUSE",
                "D3 - CUSTOMER ISSUE - PHYSICAL DAMAGE",
                "D3 - CUSTOMER ISSUE - THIRDPARTY DEVICE",
                "D3 - CUSTOMER ISSUE - VEHICLE WIRING",
                "D3 - CUSTOMER ISSUE - WATER INGRESS",
                "D3 - OUT OF WARRANTY",
                "D3 - NO ISSUE - CUSTOMER COMPLAINT",

                # ISSUE RESOLVED
                "D1 - ISSUE RESOLVED",
                "D2 - ISSUE RESOLVED",
                "D3 - ISSUE RESOLVED",

                "D1 - CUSTOMER ISSUE - VEHICLE WIRING",
                "D2 - CUSTOMER ISSUE - VEHICLE WIRING",

                "D1 - CUSTOMER ISSUE - DASHBOARD MODIFICATION",
                "D2 - CUSTOMER ISSUE - DASHBOARD MODIFICATION",
                # CUSTOMER ISSUE - FUSE
                "D1 - CUSTOMER ISSUE - FUSE",
                "D2 - CUSTOMER ISSUE - FUSE",

                # PHYSICAL DAMAGE
                "D1 - CUSTOMER ISSUE - PHYSICAL DAMAGE",
                "D2 - CUSTOMER ISSUE - PHYSICAL DAMAGE",

                # THIRDPARTY DEVICE
                "D1 - CUSTOMER ISSUE - THIRDPARTY DEVICE",
                "D2 - CUSTOMER ISSUE - THIRDPARTY DEVICE",

                # WATER INGRESS
                "D1 - CUSTOMER ISSUE - WATER INGRESS",
                "D2 - CUSTOMER ISSUE - WATER INGRESS",

                # IALERT ISSUE
                "D1 - iALERT ISSUE",
                "D2 - iALERT ISSUE",

                # NO ISSUE - CUSTOMER COMPLAINT
                "D1 - NO ISSUE - CUSTOMER COMPLAINT",
                "D2 - NO ISSUE - CUSTOMER COMPLAINT",

                # OUT OF WARRANTY
                "D1 - OUT OF WARRANTY",
                "D2 - OUT OF WARRANTY",

                "D1 - CUSTOMER RESCHEDULING - VEHICLE SUPPORT DATE",
                "D2 - CUSTOMER RESCHEDULING - VEHICLE SUPPORT DATE",

                # DEALER SENT DEVICE FOR SERVICE
                "D1 - DEALER SENT DEVICE FOR SERVICE",
                "D2 - DEALER SENT DEVICE FOR SERVICE",
                "D3 - DEALER SENT DEVICE FOR SERVICE",

                # DEVICE DISPATCHED TO WORKSHOP
                "D1 - DEVICE DISPATCHED TO WORKSHOP",
                "D2 - DEVICE DISPATCHED TO WORKSHOP",
                "D3 - DEVICE DISPATCHED TO WORKSHOP",

                # Other D3 states
                "D3 - CUSTOMER NOT ANSWERING",
                "D3 - CUSTOMER RESCHEDULING - VEHICLE SUPPORT DATE",
                "D3 - MONITORING",
                "D3 - VEHICLE PHYSICAL SUPPORT - WAITING",
                "D3 - VIDEO CALL SUPPORT - WAITING",
                "D3 - iALERT ISSUE",

                "SIM EXPIRED",
                "DEVICE TO BE SENT FOR REPAIR",
                "DEVICE TO BE SENT FOR REPLACE"
            }

            selected_remark = (post_data.get('d1_d2_d3_ialert') or entry.d1_d2_d3_ialert or '').strip()
            if call_status in CLOSED_STATUSES and entry.call_type == "I Alert Call" and selected_remark not in ALLOWED_CLOSURE_REMARKS:
                msg = 'Remarks are not acceptable for call closure. Please pick an appropriate D1/D2/D3 remark.'
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'message': msg}, status=400)
                else:
                    return JsonResponse({'success': False, 'message': msg})

            # --- D1 Closure Date Logic ---
            if entry.D1 and not entry.D1_closure_date:
                entry.D1_closure_date = now()


            if entry.D2 and not entry.D2_closure_date:
                entry.D2_closure_date = now()

            # ensure D3 closure logic included
            if entry.D3 and not entry.D3_closure_date:
                entry.D3_closure_date = now()

            entry.d1_tat = calculate_tat(entry.date_of_complaint, entry.D1_closure_date)
            entry.d2_tat = calculate_tat(entry.D1_closure_date, entry.D2_closure_date)

            # update Latest_update from D1/D2/D3 before saving
            set_latest_update_from_closures(entry)

            # Handle closure date and TAT calculations
            if call_status in [
                "Resolved", "Closed", "Closed-CI","D1-D2-D3 Completed","Auto Resolved", "Cancelled", "FIR-Resolved","Resale",
                "FIR-Repair", "FIR-Replace", "FIR-Replace_Repair", "Reject","Resale", "FIR-For Approval"
            ] and not (entry.manager_comments and str(entry.manager_comments).strip()):
                entry.date_of_closure = now()
                entry.d1_tat = calculate_tat(entry.date_of_complaint, entry.D1_closure_date)
                entry.d2_tat = calculate_tat(entry.D1_closure_date, entry.D2_closure_date)
                entry.tat = calculate_tat(entry.date_of_complaint, entry.date_of_closure)
                entry.final_status = date.today()
                set_latest_update_from_closures(entry)

            # === SAVE ENTRY ONLY ONCE, BEFORE EMAIL SENDING ===
            entry.save()

            if call_status == "FIR-For Approval":
                context = {
                    'direct_call': entry,
                    'site_domain': request.build_absolute_uri('/').rstrip('/'),
                    'engineer_form_url': request.build_absolute_uri(reverse('engineer_form', args=[entry.id])),
                }
                try:
                    logger.info(f"Preparing to send FIR-For Approval email for {entry.unique_id}")
                    engineer_email = [entry.submitted_to_email,'rajendrans@danlawtech.com']
                    cc_emails =["yoganandam@danlawtech.com", 'sales@danlawtech.com',"sivanambirajant@danlawtech.com"]
                    subject_for_approval = f"Wating for FIR-Approval - {entry.unique_id} ON {entry.vin}"
                    email_body_for_approval = render_to_string('direct_calls/fir_approval_request_mail.html', context)
                    email = EmailMessage(
                        subject=subject_for_approval,
                        body=email_body_for_approval,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=engineer_email,
                        cc=cc_emails
                    )
                    email.content_subtype = 'html'
                    email.send()
                    logger.info(f"FIR-For Approval email sent successfully for {entry.unique_id}")
                except Exception as e:
                    logger.error(f"Failed to send FIR email for {entry.unique_id}: {e}")
                finally:
                    pass
            elif call_status == "Pending" and (entry.D1_remark and entry.D1_remark.strip()) or (entry.D2_remark and entry.D2_remark.strip()):
                # Build ticket_update_url but fall back if URL name not found
                try:
                    ticket_update_url = request.build_absolute_uri(reverse('ticket_update', args=[entry.id]))
                except Exception:
                    ticket_update_url = request.build_absolute_uri(f"/direct_calls/ticket_update/{entry.id}/")
                context = {
                    'direct_call': entry,
                    'site_domain': request.build_absolute_uri('/').rstrip('/'),
                    'ticket_update_url': ticket_update_url,
                }
                subject_pending = f"Ticket Status  Update: {entry.unique_id} - {entry.vin}"
                email_body_pending = render_to_string('direct_calls/ticket_update.html', context)
                customer_emails =  [e for e in [email.strip() for email in (entry.customer_mail_id or '').split(';') if email.strip()] + [entry.submitted_to_email] if e]

                try:
                    engineer_email = entry.customer_mail_id
                    cc_emails = [entry.submitted_to_email,"yoganandam@danlawtech.com",'rajendrans@danlawtech.com', 'sales@danlawtech.com']
                    email = EmailMessage(
                        subject=subject_pending,
                        body=email_body_pending,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=customer_emails,
                        cc=cc_emails
                    )
                    email.content_subtype = 'html'
                    email.send()
                    logger.info(f"Pending email sent successfully for {entry.unique_id}")
                except Exception as e:
                    logger.error(f"Failed to send Ticket Update email for {entry.unique_id}: {e}")

            elif call_status in ["Resolved", "Closed","Closed-CI","Resale", "FIR-Repair", "FIR-Replace", "FIR-Replace_Repair", "Reject", "Cancelled"]:
                context = {
                    'direct_call': entry,
                    'site_domain': request.build_absolute_uri('/').rstrip('/'),
                    'feedback_form_url': request.build_absolute_uri(reverse('submit_feedback', args=[entry.id]))
                }
                if call_status in ["Cancelled", "Resolved", "Closed","Closed-CI"]:
                    subject_confirm = f"CRSC {call_status}: {entry.unique_id} - {entry.vin}"
                else:
                    subject_confirm = f"CRSC {call_status}: {entry.unique_id} - {entry.vin}"
                subject_customer = f"Customer Feedback Request - CRSC Ticket {entry.unique_id} Status {call_status} ON {entry.vin}"
                email_body_confirm = render_to_string('direct_calls/manager_call_closed_email.html', context)
                email_body_customer = render_to_string('direct_calls/feedback_email.html', context)
                customer_emails = [e for e in [email.strip() for email in (entry.customer_mail_id or '').split(';') if email.strip()] + [entry.submitted_to_email] if e]

                # wrap send logic in try/except (fix: ensure try has except)
                try:
                    engineer_email = entry.submitted_to_email
                    cc_emails = [entry.submitted_to_email, 'narendrareddyg@danlawtech.com', 'rajendrans@danlawtech.com', 'sales@danlawtech.com', "sivanambirajant@danlawtech.com"]
                    email = EmailMessage(
                        subject=subject_confirm,
                        body=email_body_confirm,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=customer_emails,
                        cc=cc_emails
                    )
                    email.content_subtype = 'html'
                    file_path = os.path.join(settings.MEDIA_ROOT, 'StaticFile', 'Warranty Form.docx')
                    if os.path.exists(file_path):
                        try:
                            email.attach_file(file_path)
                            logger.info("Attached Warranty Form %s for FIR-For Approval ticket %s", file_path, entry.unique_id)
                        except Exception as e:
                            logger.error("Error attaching warranty form %s for %s: %s", file_path, entry.unique_id, e)
                    else:
                        logger.warning("Warranty Form not found at %s for ticket %s", file_path, entry.unique_id)

                    email.send()
                    logger.info(f"{call_status} email sent to engineer ({engineer_email}) and CC ({cc_emails}) for: {entry.unique_id}")

                    # Only send customer feedback request for the specified statuses (NOT for Cancelled/Reject)
                    if call_status in ["Resolved", "Auto Resolved", "D1-D2-D3 Completed", "Closed", "Closed-CI", "FIR-For Approval", "FIR-Repair", "FIR-Replace", "FIR-Replace_Repair"]:
                        customer_email = [e.strip() for e in [entry.customer_mail_id, entry.end_customer_mail_id] if e and e.strip()]
                        cc_email_customer = ['rajendrans@danlawtech.com', 'sales@danlawtech.com']

                        if customer_email:
                            email = EmailMessage(
                                subject=subject_customer,
                                body=email_body_customer,
                                from_email=settings.DEFAULT_FROM_EMAIL,
                                to=customer_email,
                                cc=cc_email_customer
                            )
                            email.content_subtype = 'html'

                            try:
                                email.send(fail_silently=False)
                                logger.info("%s email sent to customer %s for: %s", call_status, customer_email, entry.unique_id)
                            except Exception:
                                logger.exception("Failed to send customer email for %s", entry.unique_id)
                        else:
                            logger.warning(f"Customer email not available for call ID {entry.unique_id}.")
                except Exception:
                    logger.exception("Failed to send engineer/customer emails for %s", getattr(entry, 'unique_id', 'N/A'))

            if call_status in ["FIR-Repair","FIR-Replace","FIR-Replace_Repair","FIR-Resolved"]:
                ist = pytz.timezone('Asia/Kolkata')
                data = {
                    'centralised_id': entry.centralised_id,
                    'device_model': entry.device_model,
                    'unique_id': entry.unique_id,
                    'engineer_requested_date': entry.date_of_complaint.astimezone(ist).strftime('%Y-%m-%d %H:%M:%S') if entry.date_of_complaint else 'N/A',
                    'details': {
                        'Service Request Number': entry.unique_id,
                        'Date of Complaint': entry.date_of_complaint.astimezone(ist).strftime('%Y-%m-%d %H:%M:%S') if entry.date_of_complaint else 'N/A',
                        'Complaint Raised By': entry.complaint_raised_by,
                        'Contact Number': entry.contact_number,
                        'Service Engineer Name': entry.complaint_assigned_to,
                        'Device Model': entry.device_model,
                        'PSN': entry.psn,
                        'VIN Number': entry.vin,
                        'Firmware Version': entry.exist_software,
                        'Device ICCID': entry.device_ICCID,
                        'Commercial Expiry Date': entry.activation_end_date.astimezone(ist).strftime('%Y-%m-%d %H:%M:%S') if entry.activation_end_date else 'N/A',
                        'Last communication in Darby': entry.last_communication_in_darby.astimezone(ist).strftime('%Y-%m-%d %H:%M:%S') if entry.last_communication_in_darby else 'N/A',
                        'Vehicle Running Location': entry.vehicle_running_location,
                        'Vehicle Run': entry.vehicle_run,
                        'Issue Identified': entry.issue_identified,
                        'Issue_analysis': entry.analysis,
                        'External Modification': entry.external_modification,
                        'Issue Description': entry.issue_analysis,
                        'Engineer Recommendation': entry.engineer_recommendation,
                        'Device Sent To': entry.device_to_be_sent,
                        'Dealer Address' : entry.dealer_address,
                        'Final Issue': entry.analysis,
                        'Manager Comments': entry.manager_comments,
                        'HOD Comments': entry.hod_comment,
                    },
                    'service_engineer_name': entry.complaint_assigned_to,
                    'manager_email': entry.submitted_to_email,
                    'call_type': entry.call_type,
                    'date_of_closure': entry.date_of_closure.astimezone(ist).strftime('%Y-%m-%d %H:%M:%S') if entry.date_of_closure else 'N/A',
                }

                # Generate the FIR PDF Document in the format FIR_{Recommendation}_{Unique}
                pdf_file_name = f"FIR_{entry.engineer_recommendation}_{entry.unique_id}.pdf"
                pdf_file_path = os.path.join(settings.MEDIA_ROOT, pdf_file_name)
                generate_device_repair_request_pdf(data, pdf_file_path)

                # Send FIR email with the PDF attachment
                try:
                    # Determine mail receipants based on device_to_be_sent
                    extra_recipients = []
                    if entry.device_to_be_sent == "Goa":
                        extra_recipients.append("deepa@danlawems.com")
                    elif entry.device_to_be_sent == "Hyderabad":
                        extra_recipients.append("lavanyav@danlawtech.com")

                    email = EmailMessage(
                        subject=f"FIR Generated - {entry.unique_id} ON {entry.vin}",
                        body=f"Please find the attached FIR document for the Request ID: {entry.unique_id}.",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[entry.submitted_to_email] + extra_recipients,
                        cc=["sales@danlawtech.com","yoganandam@danlawtech.com","rajendrans@danlawtech.com", "sivanambirajant@danlawtech.com","dilipkumarn@danlawtech.com"]
                    )
                    email.attach_file(pdf_file_path)
                    if hasattr(entry, 'upload_file_01') and entry.upload_file_01:
                        upload_file_path = entry.upload_file_01.path
                        email.attach_file(upload_file_path)
                    email.send()
                    logger.info(f"FIR PDF generated and additional file and emailed for call ID: {entry.unique_id}")
                except Exception as e:
                    logger.error(f"Failed to send FIR email: {e}")

                #sending link based on Engineer recommendation
                if entry.engineer_recommendation in ["Repair", "Replace", "Replace_Repair"]:
                    try:
                        alt_device_form_url = request.build_absolute_uri(
                            reverse('alt_device_form_with_id', args=[entry.id])
                        )
                        # Set subject based on recommendation
                        if entry.engineer_recommendation == "Repair":
                            alt_device_email_subject = f"Device Shipment Details - For Repair to Update"
                        else:
                            alt_device_email_subject = f"Alternate Device Details Required for {entry.unique_id} ON {entry.vin}"
                        context = {
                            'entry': entry,
                            'alt_device_form_url': alt_device_form_url,
                        }
                        alt_device_email_body = render_to_string('direct_calls/alternate_device_email.html', context)
                        alt_device_email = EmailMessage(
                            subject=alt_device_email_subject,
                            body=alt_device_email_body,
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            to=[entry.submitted_to_email],
                            cc=["sales@danlawtech.com", "sivanambirajant@danlawtech.com", "yoganandam@danlawtech.com", "eliyasp@danlawtech.com"]
                        )
                        alt_device_email.content_subtype = 'html'
                        alt_device_email.send()
                        logger.info(f"Alternate device form link email sent for call ID: {entry.unique_id}")
                    except Exception as e:
                        logger.error(f"Failed to send alternate device form link email: {e}")

            # Note: entry is already saved above before email sending to prevent duplicate emails

            portal_error = None
            portal_blocked = False
            try:
                if post_data.get('submit_to_customer_portal') in ('1', 'true', 'True'):
                    portal_url = getattr(settings, 'CUSTOMER_PORTAL_URL', None)
                    if portal_url:
                        payload = {
                            "ticket_id": str(entry.ticket_no or entry.unique_id),
                            "status": str(call_status or ''),
                            "remarks": str(entry.d1_d2_d3_ialert or ""),
                            "comments": str(entry.ialert_comments or ""),
                            "engineer": str(entry.complaint_assigned_to or "")
                        }
                        headers = {}
                        token = getattr(settings, 'CUSTOMER_PORTAL_TOKEN', None)
                        if token:
                            headers['Authorization'] = f"Bearer {token}"
                        logger.info("Attempting customer portal submit for %s -> %s", entry.unique_id, portal_url)
                        resp = requests.post(portal_url, json=payload, headers=headers, timeout=15)
                        if resp.status_code == 400:
                            portal_blocked = True
                            try:
                                portal_error = resp.json()
                            except Exception:
                                portal_error = resp.text or "Validation error (400) from customer portal"
                        elif not resp.ok:
                            portal_blocked = True
                            try:
                                portal_error = resp.json()
                            except Exception:
                                portal_error = f"Customer portal error {resp.status_code}: {resp.text[:1000]}"
                        else:
                            logger.info("Customer portal accepted submission for %s", entry.unique_id)
                    else:
                        logger.debug("Customer portal submission requested but CUSTOMER_PORTAL_URL not configured.")
            except requests.exceptions.RequestException as e:
                portal_blocked = True
                portal_error = f"Customer portal request failed: {str(e)}"
                logger.exception("Customer portal request exception for %s", entry.unique_id)

            # If portal blocked (400 or other failure), return JSON describing the error
            if portal_blocked:
                # Ensure the entry is saved locally (already saved above).
                response = {
                    'success': True,
                    'message': 'Saved locally but customer portal returned errors.',
                    'customer_portal_error': portal_error
                }
                return JsonResponse(response)

            response = {'success': True, 'message': 'Form submitted successfully!'}
            return JsonResponse(response)
        else:
            logger.error(f"Form errors: {form.errors}")
            return JsonResponse({'success': False, 'errors': form.errors})

    else:
        form = EngineerForm(instance=entry)

        if is_closed:
            for field in form.fields:
                form.fields[field].widget.attrs['readonly'] = True
            # guard against forms that don't include call_status
            if 'call_status' in form.fields:
                form.fields['call_status'].widget.attrs['disabled'] = True

    return render(request, 'direct_calls/engineer_form.html', {
        'form': form,
        'entry': entry,
        'is_closed': is_closed,
        'form_readonly': form_readonly,
    })


def format_dt(dt, tz):
    try:
        if not dt:
            return ''
        # If dt is a proper datetime but is naive, make it aware.
        if hasattr(dt, 'utcoffset'):
            # If its utcoffset is None, make it aware.
            if dt.utcoffset() is None:
                dt = make_aware(dt, tz)
        else:
            # dt is not a datetime at all.
            return ''
        return dt.astimezone(tz).strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        # Log error if needed
        return ''


def download_csv(request):
    response = HttpResponse(content_type='text/csv')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'Direct_calls_Data_{timestamp}.csv'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    fieldnames = [
        'Ticket Number',
        'Engineer Recommandation',
        'Manager Comments',
        'HOD Comments',
        'External Modification',
        'Device IMEI',
        'Device ICCID',
        'Device sent to',
        'Dealer Address',
        'Confirmation',
        'Feedback',
        'Rating',
        'Customer Feedback'
    ]

    writer = csv.DictWriter(response, fieldnames=fieldnames)
    writer.writeheader()

    for call in DirectCall.objects.all():
        try:
            row = {
                'Ticket Number': call.unique_id or '',
                'Engineer Recommandation': call.engineer_recommendation or '',
                'Manager Comments': call.manager_comments or '',
                'HOD Comments': call.hod_comment or '',
                'External Modification': call.external_modification or '',
                'Device IMEI': call.device_IMEI or '',
                'Device ICCID': call.device_ICCID or '',
                'Device sent to': call.device_to_be_sent or '',
                'Dealer Address': call.dealer_address or '',
                'Confirmation': call.confirmation or '',
                'Feedback': call.feedback or '',
                'Rating': str(call.rating) if call.rating is not None else '',
                'Customer Feedback': call.customer_feedback or '',
            }
            writer.writerow(row)
        except Exception as e:
            # Log the issue or skip the row
            print(f"Error processing record ID {call.id if call.id else 'Unknown'}: {e}")
            continue

    return response
def part_b_a_realtime(request):
    return render(request, 'direct_calls/part_b_a_realtime.html', )

def real_time_data(request):
    return render(request, 'direct_calls/real_time_data.html')

def fetch_records_with_fields(request):
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    part_b_status = request.GET.get('part_b_status', 'All')
    call_statuses = request.GET.getlist('call_status')
    assigned_to = request.GET.get('assigned_to')
    product_code = request.GET.get('product_code')
    call_type = request.GET.get('call_type')
    vin = request.GET.get('vin')
    unique_id = request.GET.get('unique_id')
    d2_exp_start = request.GET.get('d2_exp_start')
    d2_exp_end = request.GET.get('d2_exp_end')
    d2_closure_start = request.GET.get('d2_closure_start')
    d2_closure_end = request.GET.get('d2_closure_end')
    d3_exp_start = request.GET.get('d3_exp_start')
    d3_exp_end = request.GET.get('d3_exp_end')
    d3_closure_start = request.GET.get('d3_closure_start')
    d3_closure_end = request.GET.get('d3_closure_end')
    ticket_no = request.GET.get('ticket_no')
    date_of_closure_from = request.GET.get('date_of_closure_from')
    date_of_closure_to = request.GET.get('date_of_closure_to')
    tz = timezone.get_current_timezone()
    today = timezone.now().date()
    upper_complaint_date = today - timedelta(days=7)  # before (today - 7)
    upper_complaint_dt = timezone.make_aware(datetime.combine(upper_complaint_date, time.min), tz)
    complaint_cutoff_dt = timezone.make_aware(datetime.combine(date(2025, 10, 25), time.min), tz)

    def parse_date_or_none(s):
        if not s:
            return None
        dt = parse_date(s)
        if dt:
            return timezone.make_aware(datetime.combine(dt, time.min), tz)
        try:
            return timezone.make_aware(datetime.strptime(s, '%d-%m-%Y'), tz)
        except Exception:
            return None
    queryset = DirectCall.objects.all()
    if from_date:
        queryset = queryset.filter(date_of_complaint__gte=from_date)
    if to_date:
        queryset = queryset.filter(date_of_complaint__lte=to_date)
    if date_of_closure_from:
        queryset = queryset.filter(date_of_closure__gte=date_of_closure_from)
    if date_of_closure_to:
        queryset = queryset.filter(date_of_closure__lte=date_of_closure_to)
    ALLOWED_PB_STATUSES = ['Closed', 'Closed-CI', 'Resolved']
    cutoff_date = timezone.now().date() - timedelta(days=7)
    complaint_cutoff = date(2025, 10, 25)
    if part_b_status == 'Pending':
        # Only include records with allowed call_status values.
        # Pending = final_status is NULL OR (allowed statuses with date_of_closure older than 7 days)
        queryset = queryset.filter(
            Q(final_status__isnull=True, call_status__in=ALLOWED_PB_STATUSES) |
            (Q(call_status__in=ALLOWED_PB_STATUSES) & Q(date_of_closure__date__lt=cutoff_date) & Q(date_of_complaint__date__gt=complaint_cutoff))
        )
    elif part_b_status == 'Completed':
        # Completed = final_status is NOT NULL OR (allowed statuses with date_of_closure older than 7 days)
        queryset = queryset.filter(
            Q(final_status__isnull=False, call_status__in=ALLOWED_PB_STATUSES) |
            (Q(call_status__in=ALLOWED_PB_STATUSES) & Q(date_of_closure__date__lt=cutoff_date) & Q(date_of_complaint__date__gt=complaint_cutoff))
        )
    if call_statuses and 'All' not in call_statuses:
        queryset = queryset.filter(call_status__in=call_statuses)
    if assigned_to and assigned_to != "All":
        queryset = queryset.filter(complaint_assigned_to=assigned_to)
    if product_code and product_code != "All":
        queryset = queryset.filter(device_model=product_code)
    if call_type and call_type != "All":
        queryset = queryset.filter(call_type=call_type)
    if vin:
        queryset = queryset.filter(vin__icontains=vin)
    if unique_id:
        queryset = queryset.filter(unique_id__icontains=unique_id)
    if d2_exp_start:
        queryset = queryset.filter(D2_exp_date__gte=d2_exp_start,D2_closure_date__isnull=True)
    if d2_exp_end:
        queryset = queryset.filter(D2_exp_date__lte=d2_exp_end,D2_closure_date__isnull=True)
    if d2_closure_start or d2_closure_end:
        parsed_start = parse_date_or_none(d2_closure_start)
        parsed_end = parse_date_or_none(d2_closure_end)
        if parsed_start:
            queryset = queryset.filter(D2_closure_date__date__gte=parsed_start.date())
        if parsed_end:
            queryset = queryset.filter(D2_closure_date__date__lte=parsed_end.date())
    if d3_exp_start:
        queryset = queryset.filter(D3_exp_date__gte=d3_exp_start,D3_closure_date__isnull=True)
    if d3_exp_end:
        queryset = queryset.filter(D3_exp_date__lte=d3_exp_end,D3_closure_date__isnull=True)
    if d3_closure_start or d3_closure_end:
        parsed_start = parse_date_or_none(d3_closure_start)
        parsed_end = parse_date_or_none(d3_closure_end)
        if parsed_start:
            queryset = queryset.filter(D3_closure_date__date__gte=parsed_start.date())
        if parsed_end:
            queryset = queryset.filter(D3_closure_date__date__lte=parsed_end.date())
    if ticket_no:
        queryset = queryset.filter(ticket_no__icontains=ticket_no)
    ALLOWED_PB_STATUSES = ['Resolved', 'Closed', 'Closed-CI']
    if part_b_status == 'Pending':
        # call_status in allowed, complaint date between (25-10-2025, today-7), and final_status != "Closed"
        queryset = queryset.filter(
            call_status__in=ALLOWED_PB_STATUSES,
            date_of_complaint__gt=complaint_cutoff_dt,
            date_of_complaint__lt=upper_complaint_dt
        ).exclude(final_status="Closed")
    elif part_b_status == 'Completed':
        # call_status in allowed, complaint date between (25-10-2025, today-7), and final_status == "Closed"
        queryset = queryset.filter(
            call_status__in=ALLOWED_PB_STATUSES,
            date_of_complaint__gt=complaint_cutoff_dt,
            date_of_complaint__lt=upper_complaint_dt,
            final_status="Closed"
        )

    # from_date/to_date using full-datetime parsing (avoid SQLite date() UDF)
    if from_date:
        parsed_from = parse_date_or_none(from_date)
        if parsed_from:
            queryset = queryset.filter(date_of_complaint__gte=parsed_from)
    if to_date:
        parsed_to = parse_date_or_none(to_date)
        if parsed_to:
            queryset = queryset.filter(date_of_complaint__lt=parsed_to + timedelta(days=1))

    if date_of_closure_from:
        parsed = parse_date_or_none(date_of_closure_from)
        if parsed:
            queryset = queryset.filter(date_of_closure__gte=parsed)
    if date_of_closure_to:
        parsed = parse_date_or_none(date_of_closure_to)
        if parsed:
            queryset = queryset.filter(date_of_closure__lt=parsed + timedelta(days=1))
    call_status_data_direct_call = queryset.filter(call_type="Direct Call").values('call_status').annotate(count=Count('id'))
    call_status_data = queryset.values('call_status').annotate(count=Count('id'))  # Aggregate call statuses
    assigned_to_data_i_alert = queryset.filter(call_type="I Alert Call").values('call_status').annotate(count=Count('id'))

    queryset = queryset.order_by('-date_of_complaint')

    page_param = request.GET.get('page', '1')
    if page_param == 'all':
        data = list(queryset.values(
    'id', 'unique_id', 'call_type', 'date_of_complaint',
    'complaint_raised_by', 'complaint_assigned_to', 'vin', 'psn', 'call_status',
    'date_of_closure', 'final_action_taken', 'hod_comment', 'rating',
    'feedback_submitted_datetime', 'customer_feedback', 'contact_number',
    'D1_closure_date', 'D2_closure_date','D3_closure_date','Latest_update', 'engineer_recommendation','D1_remark','D2_remark','D3_remark',
    'vehicle_avl_in_workshop', 'complaint_raised_from_location',
    'customer_raised_issue', 'complaint_raised', 'customer_mail_id',
    'complaint_raised_through', 'complaint_received_by', 'ticket_no',
    'device_model', 'telco_status', 'active_profile', 'activation_start_date',
    'activation_end_date', 'vehicle_sale_date', 'first_communication_in_darby',
    'last_communication_in_darby', 'vehicle_type', 'vehicle_run',
    'kilometers_hours', 'main_battery_voltage', 'issue_identified',
    'issue_analysis','analysis', 'dealer_name','external_modification', 'manager_comments','issue_category',
    'd1_tat', 'd2_tat', 'tat', 'upload_file_01', 'device_to_be_sent',
    'engineer_name', 'called_date', 'latency_for_last_7_days_cc',
    'vpacket_for_last_7_days_cc', 'remarks_03', 'final_conclusion',
    'final_status', 'call_closed_by', 'exp_review_date',
    'customer_feedback_eng_review', 'alt_device_sent_by', 'alt_device_psn',
    'al_dev_sim_status', 'alt_device_shipped_through',
    'alt_device_shipped_lr_no', 'date_of_alt_device_delivered_to_customer',
    'validity_from_old_to_new_yes_done_by', 'updated_validity_of_alt_device',
    'alt_device_fitted_by', 'alt_device_working_status',
    'faulty_device_confirmation_from_destination', 'device_repaired',
    'device_shipped_to_location', 'faulty_device_shipped_date',
    'faulty_device_shipped_thru', 'faulty_device_shipped_lr_details',
    'device_taken_for_repair', 'device_delivered_to_customer',
    'device_shipped_date', 'device_fitted_by', 'device_working_status',
    'analysis', 'remarks', 'remarks_in_ialert', 'submitted_to_email',
    'engineer_contact_number', 'end_customer_mail_id',
    'vehicle_running_location', 'state', 'region', 'contact_person_name',
    'contact_person_number', 'contact_category', 'exist_software',
    'updated_software', 'issue_analysis_01','issue_category', 'D1', 'D1_engineer', 'D2',
    'D2_engineer', 'D2_exp_date', 'D3', 'D3_Engineer', 'D3_exp_date',
    'finalised_issue_category', 'device_IMEI', 'device_ICCID',
    'dealer_address', 'confirmation', 'feedback'
        ))
        # Format datetime fields for each record
        for record in data:
            format_datetime_fields(record)
        response = {
            "data": data,
            "current_page": 1,
            "total_pages": 1,
            "has_previous": False,
            "has_next": False,
            "call_counts": {
                "total": queryset.count(),
                "direct": queryset.filter(call_type="Direct Call").count(),
                "i_alert": queryset.filter(call_type="I Alert Call").count(),
            },
            "charts": {
                "assigned_to": list(assigned_to_data_i_alert),  # Filtered data for "I Alert Call"
                "call_status": list(call_status_data_direct_call),
                "call_status_pie": list(call_status_data),  # Data for the Call Status Distribution chart
            },
        }
        return JsonResponse(response)

    # Paginate the results
    paginator = Paginator(queryset, 25)
    try:
        page_number = int(page_param)
    except ValueError:
        page_number = 1  # Default to the first page if the page parameter is invalid
    page_obj = paginator.get_page(page_number)

    # Serialize only the current page's data
    data = list(page_obj.object_list.values(
       'id', 'unique_id', 'call_type', 'date_of_complaint',
    'complaint_raised_by', 'complaint_assigned_to', 'vin', 'psn', 'call_status',
    'date_of_closure', 'final_action_taken', 'hod_comment', 'rating','ialert_tk_timestamp',
    'feedback_submitted_datetime', 'customer_feedback', 'contact_number',
    'D1_closure_date', 'D2_closure_date', 'D3_closure_date','D1_remark','D2_remark','D3_remark',
    'Latest_update','engineer_recommendation',
    'vehicle_avl_in_workshop', 'complaint_raised_from_location',
    'customer_raised_issue', 'complaint_raised', 'customer_mail_id',
    'complaint_raised_through', 'complaint_received_by', 'ticket_no',
    'device_model', 'telco_status', 'active_profile', 'activation_start_date',
    'activation_end_date', 'vehicle_sale_date', 'first_communication_in_darby',
    'last_communication_in_darby', 'vehicle_type', 'vehicle_run',
    'kilometers_hours', 'main_battery_voltage', 'issue_identified',
    'issue_analysis','analysis','dealer_name', 'issue_category','external_modification', 'manager_comments',
    'd1_tat', 'd2_tat', 'tat', 'upload_file_01', 'device_to_be_sent',
    'engineer_name', 'called_date', 'latency_for_last_7_days_cc',
    'vpacket_for_last_7_days_cc', 'remarks_03', 'final_conclusion',
    'final_status', 'call_closed_by', 'exp_review_date',
    'customer_feedback_eng_review', 'alt_device_sent_by', 'alt_device_psn',
    'al_dev_sim_status', 'alt_device_shipped_through',
    'alt_device_shipped_lr_no', 'date_of_alt_device_delivered_to_customer',
    'validity_from_old_to_new_yes_done_by', 'updated_validity_of_alt_device',
    'alt_device_fitted_by', 'alt_device_working_status',
    'faulty_device_confirmation_from_destination', 'device_repaired',
    'device_shipped_to_location', 'faulty_device_shipped_date',
    'faulty_device_shipped_thru', 'faulty_device_shipped_lr_details',
    'device_taken_for_repair', 'device_delivered_to_customer',
    'device_shipped_date', 'device_fitted_by', 'device_working_status',
    'analysis', 'remarks', 'remarks_in_ialert', 'submitted_to_email',
    'engineer_contact_number', 'end_customer_mail_id',
    'vehicle_running_location', 'state', 'region', 'contact_person_name',
    'contact_person_number', 'contact_category', 'exist_software',
    'updated_software', 'issue_analysis_01','issue_category', 'D1', 'D1_engineer', 'D2','dealer_name',
    'D2_engineer', 'D2_exp_date', 'D3', 'D3_Engineer', 'D3_exp_date',
    'finalised_issue_category', 'device_IMEI', 'device_ICCID',
    'dealer_address', 'confirmation', 'feedback'
))
    # Format datetime fields for each record
    for record in data:
        format_datetime_fields(record)
    # Count FIR-Resolved records in the current queryset
    fir_resolved_count = queryset.filter(call_status="FIR-Resolved").count()
    fir_resolved_blank_rating = queryset.filter(
        call_status="FIR-Resolved"
    ).filter(rating__isnull=True).count()  # Only check for NULL, not empty string

    response = {
        "data": data,
        "current_page": page_obj.number,
        "total_pages": paginator.num_pages,
        "has_previous": page_obj.has_previous(),
        "has_next": page_obj.has_next(),
        "call_counts": {
            "total": page_obj.paginator.count,
            "direct": queryset.filter(call_type="Direct Call").count(),
            "i_alert": queryset.filter(call_type="I Alert Call").count(),
            "fir_resolved": fir_resolved_count,
            "fir_resolved_blank_rating": fir_resolved_blank_rating,
        },
        "charts": {
            "assigned_to": list(assigned_to_data_i_alert),
            "call_status": list(call_status_data_direct_call),
            "call_status_pie": list(call_status_data),
        },
    }
    return JsonResponse(response)
from django.utils.dateparse import parse_date

def check_for_updates(request):
    last_checked = request.GET.get('last_checked')
    if last_checked:
        updated_records = DirectCall.objects.filter(last_updated__gt=parse_datetime(last_checked))
        has_updates = updated_records.exists()
    else:
        has_updates = DirectCall.objects.exists()
    return JsonResponse({'has_updates': has_updates})
def get_unique_field_values(request):
    call_statuses = DirectCall.objects.values_list('call_status', flat=True).distinct()
    assigned_to = DirectCall.objects.values_list('complaint_assigned_to', flat=True).distinct()
    product_code = DirectCall.objects.values_list('device_model', flat=True).distinct()

    call_types = DirectCall.objects.values_list('call_type', flat=True).distinct()  # Get unique Call Types
    d2_exp_dates = DirectCall.objects.values_list('D2_exp_date', flat=True).distinct()
    d3_exp_dates = DirectCall.objects.values_list('D3_exp_date', flat=True).distinct()
    return JsonResponse({
        'call_statuses': list(call_statuses),
        'assigned_to': list(assigned_to),
        'product_code': list(product_code),

        'call_types': list(call_types),  # Include Call Types
        'D2_exp_dates': list(d2_exp_dates),
        'D3_exp_dates': list(d3_exp_dates),
    })
def send_feedback_form(request, call_id):
    """
    Sends the feedback form to the customer when the call status is 'Closed'.
    """
    try:
        # Fetch the DirectCall object
        direct_call = get_object_or_404(DirectCall, id=call_id)

        # Ensure the call status is 'Closed'
        if (direct_call.call_status != 'Closed'):
            return JsonResponse({'success': False, 'message': 'Feedback form can only be sent for closed calls.'})

        context = {
            'direct_call': direct_call,
            'feedback_form_url': request.build_absolute_uri(reverse('feedback_form', args=[call_id])),
            'logo_base64': logo_base64
        }

        # Render the email body
        email_body = render_to_string('direct_calls/feedback_email.html', context)

        # Send the email
        customer_email = direct_call.customer_mail_id
        if customer_email:
            subject = f"Feedback Request for Ticket: {direct_call.unique_id}"
            email = EmailMessage(
                subject=subject,
                body=email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[customer_email]
            )
            email.content_subtype = 'html'
            email.send()

            return JsonResponse({'success': True, 'message': 'Feedback form sent to the customer.'})
        else:
            return JsonResponse({'success': False, 'message': 'Customer email is not available.'})

    except Exception as e:
        logger.error(f"Error sending feedback form: {e}")
        return JsonResponse({'success': False, 'message': 'An unexpected error occurred. Please try again.'})

def submit_feedback(request, call_id):
    """
    Handles the feedback form rendering and submission.
    """
    # Fetch the DirectCall object
    direct_call = get_object_or_404(DirectCall, id=call_id)

    if request.method == 'POST':
        # Bind the form with POST data
        form = FeedbackForm(request.POST, instance=direct_call)

        if form.is_valid():
            instance = form.save(commit=False)
            instance.feedback_submitted_datetime = datetime.now()  # Save current datetime
            instance.save()
            return render(request, 'direct_calls/feedback_form.html', {
                'direct_call': direct_call,
                'submitted': True  # Indicate that the form has been submitted
            })
        else:
            return render(request, 'direct_calls/feedback_form.html', {
                'form': form,
                'direct_call': direct_call,
                'submitted': False,
                'errors': form.errors
            })

    # For GET requests, check if feedback has already been submitted
    else:
        if direct_call.customer_feedback:  # Assuming `customer_feedback` is a field in the model
            return render(request, 'direct_calls/feedback_form.html', {
                'direct_call': direct_call,
                'submitted': True  # Indicate that feedback has already been submitted
            })
        else:
            form = FeedbackForm(instance=direct_call)
            return render(request, 'direct_calls/feedback_form.html', {
                'form': form,
                'direct_call': direct_call,
                'submitted': False
            })
def device_repair_form(request, call_id):
    instance = get_object_or_404(DirectCall, id=call_id)
    if request.method == 'POST':
        post_data = request.POST.copy()
        if not post_data.get('engineer_recommendation'):
            post_data['engineer_recommendation'] = 'Repair'  # Set default value
        form = DeviceRepairForm(post_data, instance=instance)
        if form.is_valid():
            form.save()
            # Check if device_shipped_lr_no field holds a nonempty value
            plant_conclusion = form.cleaned_data.get('plant_conclusion')
            if plant_conclusion and str(plant_conclusion).strip():
                # Build URLs for the Part E and Part F forms (if needed in the template)
                part_e_form_url = request.build_absolute_uri(reverse('part_e_form', args=[instance.id]))
                part_f_url = request.build_absolute_uri(reverse('part_f_form', args=[instance.id]))
                # Prepare email context with additional details, including both URLs
                email_context = {
                    'entry': instance,
                    'part_e_form_url': part_e_form_url,
                    'part_f_url': part_f_url,
                }
                # Send first email (Part E)
                try:
                    email_body_e = render_to_string('direct_calls/email_device_repair_draft.html', email_context)
                    email_subject_e = f"{instance.engineer_recommendation} Device Installation status for Ticket: {instance.unique_id}"
                    email_e = EmailMessage(
                        subject=email_subject_e,
                        body=email_body_e,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[instance.submitted_to_email,"sales@danlawtech.com"],
                        cc=["sales@danlawtech.com","sivanambirajant@danlawtech.com","eliyasp@danlawtech.com","yoganandam@danlawtech.com",'rajendran@danlawtech.com']
                    )
                    email_e.content_subtype = 'html'
                    email_e.send()
                    logger.info(f"PART E email sent for Ticket: {instance.unique_id}")
                except Exception as e:
                    logger.error(f"Failed to send PART E email for Ticket: {instance.unique_id}: {e}")
                # Send second email (Part F)
                try:
                    email_body_f = render_to_string('direct_calls/email_part_f_submission.html', email_context)
                    email_subject_f = f"{instance.engineer_recommendation} Device Dispatch status for Ticket: {instance.unique_id}"
                    email_f = EmailMessage(
                        subject=email_subject_f,
                        body=email_body_f,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[instance.submitted_to_email, "yogesh@danlawtech.com"],
                        cc=["sales@danlawtech.com","sivanambirajant@danlawtech.com","eliyasp@danlawtech.com","yoganandam@danlawtech.com",'rajendrans@danlawtech.com']
                    )
                    email_f.content_subtype = 'html'
                    email_f.send()
                    logger.info(f"PART F email sent for Ticket: {instance.unique_id}")
                except Exception as e:
                    logger.error(f"Failed to send PART F email for Ticket: {instance.unique_id}: {e}")
            return JsonResponse({'success': True, 'message': 'Form submitted successfully!'})
        else:
            logger.error(f"Form errors: {form.errors}")
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = DeviceRepairForm(instance=instance)
    return render(request, 'direct_calls/device_repair_form.html', {'form': form})

def alt_device_form(request, id):
    direct_call = get_object_or_404(DirectCall, id=id)
    if request.method == 'POST':
        form = AltDeviceForm(request.POST, instance=direct_call)
        if form.is_valid():
            # Save the form data
            form.save()

            if form.cleaned_data.get('faulty_device_shipped_lr_details'):
                try:
                    # Generate the URL for the device repair form
                    device_repair_form_url = request.build_absolute_uri(
                        reverse('device_repair_form', args=[direct_call.id])
                    )
                    # Prepare email context for the faulty device confirmation email
                    context = {
                        'direct_call': direct_call,
                        'device_repair_form_url': device_repair_form_url,
                    }

                    # Determine recipients based on device_to_be_sent
                    extra_recipients = []
                    if direct_call.device_to_be_sent == "Goa":
                        extra_recipients.append("deepa@danlawems.com")
                    elif direct_call.device_to_be_sent == "Hyderabad":
                        extra_recipients.append("lavanyav@danlawtech.com")

                    # Render and send the existing faulty device confirmation email
                    email_body = render_to_string('direct_calls/faulty_device_confirmation_email.html', context)
                    email_subject = f"Faulty Device for further analysis - Report for FIR {direct_call.unique_id}"
                    email = EmailMessage(
                        subject=email_subject,
                        body=email_body,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[direct_call.submitted_to_email] + extra_recipients,
                        cc=["sales@danlawtech.com", "sivanambirajant@danlawtech.com","rajendrans@danlawtech.com","yoganandam@danlawtech.com"]
                    )
                    email.content_subtype = 'html'
                    email.send()
                    logger.info(f"Faulty device confirmation email sent for Ticket: {direct_call.unique_id}")
                except Exception as e:
                    logger.error(f"Failed to send faulty device confirmation email for Ticket: {direct_call.unique_id}: {e}")
            return JsonResponse({'success': True, 'message': 'Form submitted successfully!'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = AltDeviceForm(instance=direct_call)

    return render(request, 'direct_calls/alt_device_form.html', {'form': form, 'id': id})

def device_tracking(request):
    return render(request, 'direct_calls/device_tracking.html')
def device_tracking_plant(request):
    """
    Render the plant-specific device tracking page.
    Template: direct_calls/device_tracking_plant.html
    """
    return render(request, 'direct_calls/device_tracking_plant.html')
def device_tracking_plant_shippment(request):
    """
    Render the plant-specific device tracking page.
    Template: direct_calls/device_tracking_plant.html
    """
    return render(request, 'direct_calls/device_tracking_plant_shippment.html')
def fetch_filter_field_values(request):
    # Fetch unique values for call_status, call_type, complaint_assigned_to, and hod_comment
    call_statuses = DirectCall.objects.values_list('call_status', flat=True).distinct().order_by('call_status')
    call_types = DirectCall.objects.values_list('call_type', flat=True).distinct().order_by('call_type')
    assigned_to = DirectCall.objects.values_list('complaint_assigned_to', flat=True).distinct().order_by('complaint_assigned_to')
    product_code = DirectCall.objects.values_list('device_model', flat=True).distinct().order_by('device_model')

    hod_comments = DirectCall.objects.values_list('hod_comment', flat=True).distinct().order_by('hod_comment')
    engineer_recommendations = DirectCall.objects.values_list('engineer_recommendation', flat=True).distinct().order_by('engineer_recommendation')
    return JsonResponse({
        'call_statuses': list(call_statuses),
        'assigned_to': list(assigned_to),
        'product_code': list(product_code),
        'call_types': list(call_types),
        'hod_comments': list(hod_comments),
        'engineer_recommendations': list(engineer_recommendations),
    })
def fetch_device_tracking_records(request):
    call_status = request.GET.get('call_status', 'All')
    psn = request.GET.get('psn', '')
    vin = request.GET.get('vin', '')
    unique_id = request.GET.get('unique_id', '')
    assigned_to = request.GET.get('complaint_assigned_to', '')
    product_code = request.GET.get('device_model', '')

    call_type = request.GET.get('call_type', 'All')
    hod_comment = request.GET.get('hod_comment', 'All')
    engineer_recommendation = request.GET.get('engineer_recommendation', 'All')
    part_b_status = request.GET.get('part_b_status', 'All')  # new filter for Part-B(A) status
    from_date = request.GET.get('from_date', '')
    to_date = request.GET.get('to_date', '')
    activity_status = request.GET.get('activity_status', 'All')

    # Filter the queryset
    queryset = DirectCall.objects.all()
    tz = timezone.get_current_timezone()
    today = timezone.now().date()
    upper_complaint_date = today - timedelta(days=7)
    upper_complaint_dt = timezone.make_aware(datetime.combine(upper_complaint_date, time.min), tz)
    complaint_cutoff_dt = timezone.make_aware(datetime.combine(date(2025, 10, 25), time.min), tz)

    def parse_date_or_none(s):
        if not s:
            return None
        dt = parse_date(s)
        if dt:
            return timezone.make_aware(datetime.combine(dt, time.min), tz)
        try:
            return timezone.make_aware(datetime.strptime(s, '%d-%m-%Y'), tz)
        except Exception:
            return None
    if call_status != "All":
        queryset = queryset.filter(call_status=call_status)
    if call_type != "All":
        queryset = queryset.filter(call_type=call_type)
    if psn:
        queryset = queryset.filter(psn__icontains=psn)
    if vin:
        queryset = queryset.filter(vin__icontains=vin)
    if unique_id:
        queryset = queryset.filter(unique_id__icontains=unique_id)
    if assigned_to != "All":
        queryset = queryset.filter(complaint_assigned_to__icontains=assigned_to)
    if product_code != "All":
        queryset = queryset.filter(device_model__icontains=product_code)
    if hod_comment != "All":
        queryset = queryset.filter(hod_comment__icontains=hod_comment)
    if engineer_recommendation != "All":
        queryset = queryset.filter(engineer_recommendation=engineer_recommendation)
    ALLOWED_PB_STATUSES = ['Resolved', 'Closed', 'Closed-CI']
    if part_b_status == 'Pending':
        queryset = queryset.filter(
            call_status__in=ALLOWED_PB_STATUSES,
            date_of_complaint__gt=complaint_cutoff_dt,
            date_of_complaint__lt=upper_complaint_dt
        ).exclude(final_status="Closed")
    elif part_b_status == 'Completed':
        queryset = queryset.filter(
            call_status__in=ALLOWED_PB_STATUSES,
            date_of_complaint__gt=complaint_cutoff_dt,
            date_of_complaint__lt=upper_complaint_dt,
            final_status="Closed"
        )
    if activity_status == "Pending":
        queryset = queryset.filter(Q(faulty_device_shipped_lr_details__isnull=True) | Q(faulty_device_shipped_lr_details__exact=''))
    elif activity_status == "Completed":
        queryset = queryset.exclude(Q(faulty_device_shipped_lr_details__isnull=True) | Q(faulty_device_shipped_lr_details__exact=''))

    # from_date/to_date using datetime parsing
    if from_date:
        parsed_from = parse_date_or_none(from_date)
        if parsed_from:
            queryset = queryset.filter(date_of_complaint__gte=parsed_from)
    if to_date:
        parsed_to = parse_date_or_none(to_date)
        if parsed_to:
            queryset = queryset.filter(date_of_complaint__lt=parsed_to + timedelta(days=1))

    if from_date:
        queryset = queryset.filter(date_of_complaint__date__gte=from_date)
    if to_date:
        queryset = queryset.filter(date_of_complaint__date__lte=to_date)
    print(f"Filters: call_status={call_status}, psn={psn}, vin={vin}, unique_id={unique_id}, assigned_to={assigned_to}, part_b_status={part_b_status}, activity_status={activity_status}")
    print(f"Queryset exists: {queryset.exists()}")
    queryset = queryset.order_by('-unique_id')

    data = list(queryset.values(
        'id',
        'unique_id', 'vin', 'psn', 'device_model', 'complaint_raised_by',
        'complaint_assigned_to', 'date_of_complaint', 'call_status','call_type', 'hod_comment', 'engineer_recommendation','device_to_be_sent',                     # Final Action Taken (already present)
        'vehicle_avl_in_workshop',
        'complaint_raised_from_location',
        'customer_raised_issue',
        'complaint_raised',
        'complaint_raised_by',
        'contact_number',
        'customer_mail_id',
        'complaint_raised_through',
        'complaint_received_by', 'ticket_no',
        'ialert_tk_timestamp',
        'device_model',
        'telco_status',
        'active_profile',
        'activation_start_date',
        'activation_end_date',
        'vehicle_sale_date',
        'first_communication_in_darby',
        'last_communication_in_darby', 'vehicle_type', 'vehicle_run',
        'kilometers_hours', 'main_battery_voltage', 'issue_identified',
        'issue_analysis','analysis',
        'dealer_name',
        'issue_category',
        'external_modification', 'manager_comments',
        'd1_tat', 'd2_tat', 'tat', 'upload_file_01', 'device_to_be_sent',
        'engineer_name', 'called_date', 'latency_for_last_7_days_cc',
        'vpacket_for_last_7_days_cc', 'remarks_03', 'final_conclusion',
        'final_status', 'call_closed_by', 'exp_review_date',
        'customer_feedback_eng_review', 'alt_device_sent_by', 'alt_device_psn',
        'al_dev_sim_status', 'alt_device_shipped_through',
        'alt_device_shipped_lr_no', 'date_of_alt_device_delivered_to_customer',
        'validity_from_old_to_new_yes_done_by', 'updated_validity_of_alt_device',
        'alt_device_fitted_by', 'alt_device_working_status',
        'faulty_device_confirmation_from_destination', 'device_repaired',
        'device_shipped_to_location', 'faulty_device_shipped_date',
        'faulty_device_shipped_thru', 'faulty_device_shipped_lr_details',
        'device_taken_for_repair', 'device_delivered_to_customer',
        'device_shipped_date', 'device_fitted_by', 'device_working_status',
        'analysis', 'remarks', 'remarks_in_ialert', 'submitted_to_email',
        'engineer_contact_number', 'end_customer_mail_id',
        'vehicle_running_location', 'state', 'region', 'contact_person_name',
        'contact_person_number', 'contact_category', 'exist_software',
        'updated_software', 'issue_analysis_01','issue_category', 'D1', 'D1_engineer', 'D2','dealer_name',
        'D2_engineer', 'D2_exp_date', 'D3', 'D3_Engineer', 'D3_exp_date',
        'finalised_issue_category', 'device_IMEI', 'device_ICCID',
        'dealer_address', 'confirmation', 'feedback'
    ))

    return JsonResponse({'data': data})


def part_e_form(request, id):
    instance = get_object_or_404(DirectCall, id=id)

    if request.method == 'POST':
        form = DeviceRepairForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            # Save the form data
            form.save()

            # Check if "Device Shipped LR No" holds a non- empty value
            plant_conclusion = form.cleaned_data.get('plant_conclusion')
            if plant_conclusion and str(plant_conclusion).strip():
                # Prepare common email context with details
                email_context = {
                    'entry': instance,
                    'logo_base64': '',  # Attach  Logo of danlaw
                }

                # Send Part E email
                try:
                    email_body_e = render_to_string('direct_calls/email_part_e_submission.html', email_context)
                    email_subject_e = f"Part E Form Submission for Ticket: {instance.unique_id}"
                    email_e = EmailMessage(
                        subject=email_subject_e,
                        body=email_body_e,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=["sales@danlawtech.com", instance.submitted_to_email],
                        cc=["sivanambirajant@danlawtech.com", "rajendrans@danlawtech.com",
                            "yoganandam@danlawtech.com", "eliyasp@danlawtech.com"]
                    )
                    email_e.content_subtype = 'html'
                    email_e.send()
                    logger.info(f"Part E email sent successfully for Ticket: {instance.unique_id}")
                except Exception as e:
                    logger.error(f"Failed to send Part E email for Ticket: {instance.unique_id}: {e}")

                # Send Part F email
                try:
                    email_body_f = render_to_string('direct_calls/email_part_f_submission.html', email_context)
                    email_subject_f = f"Part F - Device Shipped LR No provided for Ticket: {instance.unique_id}"
                    email_f = EmailMessage(
                        subject=email_subject_f,
                        body=email_body_f,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=["sales@danlawtech.com", "upendram@danlawtech.com"],
                    )
                    email_f.content_subtype = 'html'
                    email_f.send()
                    logger.info(f"Part F email sent successfully for Ticket: {instance.unique_id}")
                except Exception as e:
                    logger.error(f"Failed to send Part F email for Ticket: {instance.unique_id}: {e}")

            return JsonResponse({'success': True, 'message': 'Form submitted successfully!'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = DeviceRepairForm(instance=instance)

    return render(request, 'direct_calls/part_e_form.html', {'form': form})


def part_f_form(request, id):
    instance = get_object_or_404(DirectCall, id=id)
    if request.method == 'POST':
        form = DeviceRepairForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            # Check if "Device Shipped LR No" is provided
            device_lr_no = form.cleaned_data.get('device_shipped_lr_no')
            if device_lr_no and str(device_lr_no).strip():
                try:
                    email_context = {
                        'entry': instance,
                        # Optionally add the logo as a base64 string if available
                        'logo_base64': '',
                    }
                    # Render the email body using the HTML template
                    email_body = render_to_string('direct_calls/email_part_f_submission.html', email_context)
                    email_subject = f"Part D_1 - Device Shipped LR No provided for Ticket: {instance.unique_id}"
                    email = EmailMessage(
                        subject=email_subject,
                        body=email_body,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=["sales@danlawtech.com","upendram@danlawtech.com"],
                        cc=["sales@danlawtech.com","sivanambirajant@danlawtech.com","eliyasp@danlawtech.com","yoganandam@danlawtech.com","rajendrans@danlawtech.com"]
                    )
                    email.content_subtype = 'html'
                    email.send()
                    logger.info(f"Email sent successfully to sales@danlawtech.com for Ticket: {instance.unique_id}")
                except Exception as e:
                    logger.error(f"Failed to send Part F email for Ticket: {instance.unique_id}: {e}")
            return JsonResponse({'success': True, 'message': 'Form submitted successfully!'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = DeviceRepairForm(instance=instance)
    return render(request, 'direct_calls/part_f.html', {'form': form})



def to_ist(dt):
    """Convert a datetime to Asia/Kolkata timezone and format as string, or return empty string if None."""
    if not dt:
        return ''
    try:
        return dt.astimezone(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        return ''

@require_GET
def fetch_darby_communication(request, id):
    from django.shortcuts import get_object_or_404
    from datetime import datetime, timedelta
    import requests

    try:
        entry = get_object_or_404(DirectCall, id=id)
        vin = entry.vin.strip().upper()
        logger.info(f"VIN: {vin}")

        if entry.call_status in [
            "Pending","Resolved", "Closed","Closed-CI","Cancelled", "FIR-Resolved","FIR-For Approval", "FIR-Repair", "FIR-Replace", "FIR-Replace_Repair","D1-D2-D3 Completed","Auto Resolved","Closed-CI","Hold"
        ]:
            return JsonResponse({
                "device_model": entry.device_model,
                "telco_status": entry.telco_status,
                "exist_software": entry.exist_software,
                "active_profile": entry.active_profile,
                "al_mfg_plant": entry.al_mfg_plant,
                "card_status": entry.card_status,
                "psn": entry.psn,
                "customer_contact_no": entry.customer_contact_no,
                "last_communication_in_darby": entry.last_communication_in_darby.astimezone(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S') if entry.last_communication_in_darby else '',
                "first_communication_in_darby": entry.first_communication_in_darby.astimezone(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S') if entry.first_communication_in_darby else '',
                "s_trigger_completion_date": to_ist(entry.s_trigger_completion_date),
                "first_communication_in_darby": entry.first_communication_in_darby.astimezone(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S') if entry.first_communication_in_darby else '',
                "main_battery_voltage": entry.main_battery_voltage,
                "state": entry.state,
                "activation_start_date": to_ist(entry.activation_start_date),
                "activation_end_date": to_ist(entry.activation_end_date),
                "kilometers_hours": entry.kilometers_hours,
                "summary_table": [],
                "raw_data": {},
            })

        # 1. Fetch asset info (first API)
        api_url_1 = "https://api.al.drivewithdarby.com/v1/assets/dynamic/search"
        headers_1 = {
            "Authorization": f"Bearer eyJhbGciOiJIUzM4NCJ9.eyJpc3MiOiJkYXJieSIsImp0aSI6ImJkNzVmYWIzLWNhNDktNDBiMi1iZGJjLThiYzJiMDllOTFlNyIsImlhdCI6MTc1MDg0NDc2OSwiZXhwIjoxNzgyMzgwNzY5LCJDSSI6NDIsIlVJIjoiMzFhZmUzMjgtZTIzYS00MDI2LWJkMGEtYmJkMzViMGRkODg0IiwiRU0iOiJWaXNod2FuYXRoLkdAYXNob2tsZXlsYW5kLmNvbSIsIlJJIjoiMWQ5MDllZTUtOWQ1ZS00Y2E3LWJjZmEtMzQ5YWUzM2YzMjIzIiwiVFkiOiJBRE1JTl9VU0VSIiwiRk4iOiJWaXNod2FuYXRoIiwiTE4iOiJHOiBEYW5sYXcgQXNzZXQgRHluYW1pYyBTZWFyY2giLCJQSSI6IjMxYWZlMzI4LWUyM2EtNDAyNi1iZDBhLWJiZDM1YjBkZDg4NCIsIlBOIjoiRGFubGF3IEFzc2V0IER5bmFtaWMgU2VhcmNoIiwiQUkiOiJjOWQ1YjViOS1lNjE4LTQ5OTktYmY1Mi1hNjQ4NTgwYjU0N2EiLCJBVCI6WyJBU1NFVDpSRUFEIiwiUkVQT1JUOlJFQUQiLCJMSVZFOlJFQUQiLCJDQU1QQUlHTjpSRUFEIiwiREFTSEJPQVJEOlJFQUQiXX0.LPPA6mVuKOH1L_KOvoe0r1anfuSMSjbuWyYdK7LVH82UGLKpQpsASMoSEHz81p0L",
            "Content-Type": "application/json"
        }
        payload_1 = {
            "assetType": "DEVICE",
            "filters": {"vin": [vin]}
        }
        resp1 = requests.post(api_url_1, headers=headers_1, json=payload_1, timeout=10)
        resp1.raise_for_status()
        assets = resp1.json().get("results", [])
        asset = next((a for a in assets if a.get("vin", "").strip().upper() == vin), None)
        if not asset:
            logger.error(f"No asset found for VIN: {vin}")
            return JsonResponse({"error": f"No asset found with VIN: {vin}"}, status=404)

        # Device info fields
        device_model = asset.get("productCode", "")
        telco_status = asset.get("cardState", "")
        exist_software = asset.get("fwCategory", "")
        active_profile = asset.get("profileStatus", "")
        nrd_category = asset.get("nrdCategory", "")
        device_ICCID= asset.get("iccid", "")
        customer_contact_no=asset.get("consumerMobileNumber","")
        created_at = asset.get("createdAt", None)
        created_at_formatted = ""
        if created_at:
            try:
                dt = datetime.fromtimestamp(int(created_at) / 1000)
                created_at_formatted = dt.strftime("%d-%m-%Y")
            except Exception:
                created_at_formatted = ""
        # Get both Kafka published times (they may be None)
        vpacket_time_ms = asset.get("vpacketKafkaPublishedTime")
        apacket_time_ms = asset.get("apacketKafkaPublishedTime")

        # Convert to datetime if present
        vpacket_dt = datetime.fromtimestamp(int(vpacket_time_ms) / 1000) if vpacket_time_ms else None
        apacket_dt = datetime.fromtimestamp(int(apacket_time_ms) / 1000) if apacket_time_ms else None

        # Find the latest datetime
        last_communication_dt = None
        if vpacket_dt and apacket_dt:
            last_communication_dt = max(vpacket_dt, apacket_dt)
        elif vpacket_dt:
            last_communication_dt = vpacket_dt
        elif apacket_dt:
            last_communication_dt = apacket_dt
        else:
            # Fallback to lastCommunication if both are missing
            last_communication_ms = asset.get("lastCommunication", None)
            if last_communication_ms:
                try:
                    last_communication_dt = datetime.fromtimestamp(int(last_communication_ms) / 1000)
                except Exception:
                    last_communication_dt = None

        # Format as string for output
        last_communication_str = ""
        if last_communication_dt:
            last_communication_str = last_communication_dt.strftime("%Y-%m-%dT%H:%M")
        first_communication_ms = asset.get("firstCommunication", None)
        first_communication_str = ""
        if first_communication_ms:
            try:
                first_communication_dt = datetime.fromtimestamp(int(first_communication_ms) / 1000)
                first_communication_str = first_communication_dt.strftime("%Y-%m-%dT%H:%M")
            except Exception:
                first_communication_str = ""
        S_trigger_date_ms = asset.get("S_activationRequestDate", None)
        S_trigger_date_str = ""
        if S_trigger_date_ms:
            try:
                S_trigger_date_dt = datetime.fromtimestamp(int(S_trigger_date_ms) / 1000)
                S_trigger_date_str = S_trigger_date_dt.strftime("%Y-%m-%dT%H:%M")
            except Exception:
                S_trigger_date_str = ""
        C_trigger_date_ms = asset.get("C_activationRequestDate", None)
        C_trigger_date_str = ""
        if C_trigger_date_ms:
            try:
                C_trigger_date_dt = datetime.fromtimestamp(int(C_trigger_date_ms) / 1000)
                C_trigger_date_str = C_trigger_date_dt.strftime("%Y-%m-%dT%H:%M")
            except Exception:
                C_trigger_date_str = ""
        al_mfg_plant = asset.get("alMfgPlant", "")
        card_status = asset.get("cardStatus", "")
        psn = asset.get("assetName", "")
        main_battery_voltage = asset.get("vehicleBatteryPotential", "")
        kilometers_hours = asset.get("odometer", "")
        state = asset.get("state", "")
        activation_start_date_str = ""
        activation_end_date_str = ""

        if telco_status == "Bootstrap":
            activation_start_ms = asset.get("bootstrapActivationDate")
            activation_end_ms = asset.get("bootstrapExpiryDate")
        elif telco_status == "Commercial":
            activation_start_ms = asset.get("commercialActivationDate")
            activation_end_ms = asset.get("commercialExpiryDate")
        else:
            activation_start_ms = None
            activation_end_ms = None
        if activation_start_ms:
            try:
                activation_start_date = datetime.fromtimestamp(int(activation_start_ms) / 1000)
                activation_start_date_str = activation_start_date.strftime("%Y-%m-%dT%H:%M")
            except Exception:
                activation_start_date_str = ""
        if activation_end_ms:
            try:
                activation_end_date = datetime.fromtimestamp(int(activation_end_ms) / 1000)
                activation_end_date_str = activation_end_date.strftime("%Y-%m-%dT%H:%M")
            except Exception:
                activation_end_date_str = ""

        asset_id = asset.get("assetId", "")
        logger.info(f"Asset ID: {asset_id}")

        # Set your desired date range (last 7 days)
        end_dt = datetime.now()
        start_dt = end_dt - timedelta(days=6)
        startTime = start_dt.strftime('%Y-%m-%dT00:00:00Z')
        endTime = end_dt.strftime('%Y-%m-%dT23:59:59Z')

        api_url_2 = (
            f"https://web.al.drivewithdarby.com/v1/messages/asset/{asset_id}/analytics-daily-summary"
            f"?startTime={startTime}&endTime={endTime}"
        )
        resp2 = requests.get(api_url_2, headers=headers_1, timeout=10)
        resp2.raise_for_status()
        analytics_data = resp2.json()
        logger.info(json.dumps(analytics_data, indent=2))

        # Build summary_table from new API structure
        summary_table = []
        for row in analytics_data.get("results", []):
            min_odo = row.get("min_odo", 0) or 0
            max_odo = row.get("max_odo", 0) or 0
            kms = max_odo - min_odo if max_odo and min_odo else 0
            summary_table.append({
                "date": datetime.strptime(row.get("date", ""), "%Y-%m-%d").strftime("%d-%m-%Y") if row.get("date") else "",
                "v_packets": row.get("v_count", 0) or 0,
                "a_packets": row.get("a_count", 0) or 0,
                "total_packets": (row.get("v_count", 0) or 0) + (row.get("a_count", 0) or 0),
                "start_odo": min_odo,
                "end_odo": max_odo,
                "kms": kms,
                "lat_0_5": row.get("cnt_0_5m", 0) or 0,
                "lat_5_15": row.get("cnt_5_15m", 0) or 0,
                "lat_15_30": row.get("cnt_15_30m", 0) or 0,
                "lat_30_1h": row.get("cnt_30_60m", 0) or 0,
                "lat_1h_3h": row.get("cnt_1_3h", 0) or 0,
                "lat_3h_6h": row.get("cnt_3_6h", 0) or 0,
                "lat_6h_12h": row.get("cnt_6_12h", 0) or 0,
                "lat_12h_24h": row.get("cnt_12_24h", 0) or 0,
                "lat_gt_24h": row.get("cnt_gt_24h", 0) or 0,
            })

        # Attempt to detect S-trigger completion timestamp in asset keys (various possible names)
        s_trigger_completion_date_str = ""
        for k, v in asset.items():
            key_lower = k.lower()
            # prefer keys that indicate 's' trigger and 'completion' words
            if ('complete' in key_lower or 'completed' in key_lower or 'completion' in key_lower) and ('s_' in key_lower or key_lower.startswith('s') or 'sactivation' in key_lower or 's_activation' in key_lower):
                try:
                    ms = int(v)
                    s_trigger_completion_date_str = datetime.fromtimestamp(ms / 1000).strftime("%Y-%m-%dT%H:%M")
                    break
                except Exception:
                    continue
        # Fallback: try any completion-like key
        if not s_trigger_completion_date_str:
            for k, v in asset.items():
                if 'complete' in k.lower() or 'completion' in k.lower() or 'completed' in k.lower():
                    try:
                        ms = int(v)
                        s_trigger_completion_date_str = datetime.fromtimestamp(ms / 1000).strftime("%Y-%m-%dT%H:%M")
                        break
                    except Exception:
                        continue

        return JsonResponse({
            "device_model": device_model,
            "telco_status": telco_status,
            "exist_software": exist_software,
            "active_profile": active_profile,
            "al_mfg_plant": al_mfg_plant,
            "card_status": card_status,
            "psn": psn,
            "nrd_category": nrd_category,
            "device_ICCID":device_ICCID,
            "customer_contact_no":customer_contact_no,
            "last_communication_in_darby": last_communication_str,
            "first_communication_in_darby": first_communication_str,
            "main_battery_voltage": main_battery_voltage,
            "state": state,
            "activation_start_date": activation_start_date_str,
            "activation_end_date": activation_end_date_str,
            "S_trigger_date": S_trigger_date_str,
            "C_trigger_date": C_trigger_date_str,
            "s_trigger_completion_date": s_trigger_completion_date_str,
            "kilometers_hours": kilometers_hours,
            "summary_table": summary_table,
            "raw_data": analytics_data
        })

    except Exception as e:
        logger.exception("Error in fetch_darby_communication")
        return JsonResponse({"error": str(e)}, status=500)


DATETIME_FIELDS = [
    'date_of_complaint',
    'date_of_closure',
    'D1_closure_date',
    'D2_closure_date',
    'D3_closure_date',
    'Latest_update',
    'activation_start_date',
    'activation_end_date',
    'vehicle_sale_date',
    'first_communication_in_darby',
    'last_communication_in_darby',
    'S_trigger_date',
    'C_trigger_date',
    'called_date',
]

def format_datetime_fields(record):
    for field in DATETIME_FIELDS:
        value = record.get(field)
        if value:
            try:
                # If value is already a string in ISO format, parse it
                if isinstance(value, str) and 'T' in value:
                    value = datetime.fromisoformat(value.replace('Z', '+00:00'))
                # Format as 'YYYY-MM-DD HH:MM:SS'
                record[field] = value.strftime('%Y-%m-%d %H:%M:%S')
            except Exception:
                # If parsing fails, leave as it is, else pass
                pass
    return record


def part_b_a(request, id):
    entry = get_object_or_404(DirectCall, id=id)
    # Consider Part-B closed only when final_status indicates closed.

    fs = entry.final_status
    is_closed = False
    try:
        if fs is None:
            is_closed = False
        elif isinstance(fs, str):
            is_closed = fs.strip().lower() == 'closed'
        elif isinstance(fs, (date, datetime)):
            # final_status stored as a date means the record was closed
            is_closed = True
        else:
            is_closed = False
    except Exception:
        is_closed = False

    if request.method == 'POST':
        form = EngineerReviewForm(request.POST, request.FILES, instance=entry)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.called_date = timezone.now()  # This now works!
            instance.save()
            return JsonResponse({'success': True, 'message': 'Form submitted successfully!'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = EngineerReviewForm(instance=entry)
        if is_closed:
            for field in form.fields:
                form.fields[field].widget.attrs['readonly'] = True
            # guard against forms that don't include call_status
            if 'call_status' in form.fields:
                form.fields['call_status'].widget.attrs['disabled'] = True

    context = {
        'form': form,
        'entry': entry,
        'is_closed': is_closed,
        'call_type': entry.call_type,
    }
    return render(request, 'direct_calls/engineer_form_b_a.html', context)


@csrf_exempt
def api_create_ticket(request):
    """
    API endpoint to create/update direct call ticket
    Sends manager email if remarks contain trigger keywords
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Only POST allowed'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
        logger.info("IAlert Incoming Payload: %s", data)
    except Exception:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

    def _str(v):
        return str(v).strip() if v is not None else ""

    danlaw_unique_id = _str(data.get("danlaw_unique_id"))
    remarks = _str(data.get("remarks"))
    raw_ticket = None
    if "ticket_id" in data:
        raw_ticket = data.get("ticket_id")
    elif "ticketId" in data:
        raw_ticket = data.get("ticketId")
    raw_callback = data.get("callbackNo") if "callbackNo" in data else None

    # If either ticket id or callbackNo is present but blank, refuse to create/update
    if (("ticket_id" in data or "ticketId" in data) and (raw_ticket is None or str(raw_ticket).strip() == "")) or \
       ("callbackNo" in data and (raw_callback is None or str(raw_callback).strip() == "")):
        logger.warning("api_create_ticket refused: blank ticket_id and callbackNo in payload")
        return JsonResponse({
            'success': False,
            'action': 'Not-Updated : ticket_id and callbackNo should not be blank',
            'ticket_id': 'None',
            'unique_id': 'None'
        }, status=400)

    try:
        if not danlaw_unique_id:
            # Create new entry
            entry = DirectCall.objects.create(
                date_of_complaint=now().astimezone(pytz.timezone('Asia/Kolkata')),
                complaint_raised_from_location=_str(data.get('areaName')),
                customer_raised_issue=_str(data.get('issueDescription')),
                complaint_raised=_str(data.get('designation')),
                complaint_raised_by=_str(data.get('customerName')),
                contact_number=";".join([
                    _str(data.get('callbackNo')),
                    _str(data.get('driverContact')),
                    _str(data.get('serviceContact')),
                ]),
                customer_mail_id=_str(data.get('customerMailId')) or "sales@danlawtech.com",
                complaint_raised_through="I-Alert PD API",
                call_type="I Alert Call",
                vin=_str(data.get('vinNumber')),
                psn=_str(data.get('deviceId')),
                ticket_no=_str(data.get('ticketId')),
                vehicle_avl_in_workshop="No",
                complaint_received_by="A.L API",
                complaint_assigned_to="--",
                updated_contact_no=_str(data.get("comments")),
                ialert_remarks=remarks,
            )

            response = {
                'success': True,
                'action': 'created',
                'ticket_id': entry.id,
                'unique_id': entry.unique_id
            }
            logger.info("api_create_ticket created entry -> %s", response)
            return JsonResponse(response)

        # Update existing entry
        try:
            ticket = DirectCall.objects.get(unique_id=danlaw_unique_id)
        except DirectCall.DoesNotExist:
            logger.warning(f"No ticket found for danlaw_unique_id: {danlaw_unique_id}")
            return JsonResponse(
                {
                    'success': False,
                    'action': 'No ticket found for given danlaw_unique_id',
                    'ticket_id': 'None',
                    'unique_id': danlaw_unique_id
                },
                status=404
            )

        update_fields = []
        email_triggered = False

        # Contact update case
        if remarks == "Assigned to Danlaw – Contact Update":
            ticket.updated_contact_no = _str(data.get("comments"))
            ticket.ialert_remarks = remarks
            update_fields.append("updated_contact_no")
            update_fields.append("ialert_remarks")
            email_triggered = True

        # Re-assigned case → Pending
        elif remarks == "Assigned to Danlaw - new":
            ticket.call_status = "Pending"
            ticket.ialert_remarks = remarks
            update_fields.append("call_status")
            update_fields.append("ialert_remarks")
            email_triggered = True

        # Update remarks in any case
        if remarks and "ialert_remarks" not in update_fields:
            ticket.ialert_remarks = remarks
            update_fields.append("ialert_remarks")

        # SAVE TO DATABASE FIRST
        if update_fields:
            ticket.save(update_fields=update_fields)
            logger.info(f"Updated ticket {danlaw_unique_id} with fields: {update_fields}")

        # RETURN SUCCESS RESPONSE IMMEDIATELY
        response = {
            'success': True,
            'action': 'updated',
            'ticket_id': ticket.id,
            'unique_id': ticket.unique_id,
        }

        # SEND EMAIL IN BACKGROUND (non-blocking)
        if email_triggered:
            try:
                # Optional: Send email asynchronously using threading
                import threading
                email_thread = threading.Thread(
                    target=send_manager_email,
                    args=(ticket,),
                    daemon=True
                )
                email_thread.start()
                logger.info(f"Manager email triggered in background for ticket {danlaw_unique_id}")
            except Exception as e:
                logger.error(f"Failed to trigger background email for {danlaw_unique_id}: {e}")
                # Don't fail the API response if email fails

        return JsonResponse(response)

    except DirectCall.DoesNotExist:
        logger.warning(f"DirectCall not found for unique_id: {danlaw_unique_id}")
        return JsonResponse(
            {
                'success': False,
                'action': 'No ticket found for given danlaw_unique_id',
                'ticket_id': 'None',
                'unique_id': danlaw_unique_id
            },
            status=404
        )
    except Exception as e:
        logger.exception("api_create_ticket failed")
        return JsonResponse(
            {
                'success': False,
                'action': str(e),
                'ticket_id': 'None',
                'unique_id': danlaw_unique_id or 'None'
            },
            status=500
        )


def send_manager_email(entry):
    """
    Send manager email using manager_email.html template
    Triggers when remarks = "Assigned to Danlaw – Contact Update" or "Assigned to Danlaw - new"
    """
    def _str(v):
        return str(v).strip() if v is not None else ""

    try:
        # Validate remarks
        remarks = _str(getattr(entry, 'ialert_remarks', ''))
        trigger_remarks = [
            "Assigned to Danlaw – Contact Update",
            "Assigned to Danlaw - new"
        ]

        if remarks not in trigger_remarks:
            logger.warning(f"send_manager_email: remarks '{remarks}' not in trigger list")
            return False

        # Get recipient - filter out empty values and validate
        recipient_list = [entry.complaint_assigned_to,"yoganandam@danlawtech.com"]

        # Add submitted_to_email if available
        submitted_email = _str(getattr(entry, 'submitted_to_email', ''))
        if submitted_email and '@' in submitted_email:
            recipient_list.append(submitted_email)

        # Always add sales email
        sales_email = "sales@danlawtech.com"
        if sales_email not in recipient_list:
            recipient_list.append(sales_email)

        # Validate we have at least one recipient
        if not recipient_list:
            logger.warning(f"send_manager_email: No valid recipient email for ticket {entry.unique_id}")
            return False

        logger.info(f"send_manager_email: Sending to recipients: {recipient_list}")

        # Prepare context for email template
        context = {
            'entry': entry,
            'site_domain': settings.SITE_DOMAIN,
        }

        # Render HTML email
        html_message = render_to_string(
            'direct_calls/contact_update.html',
            context
        )
        plain_message = strip_tags(html_message)

        # Set subject based on remarks
        if remarks == "Assigned to Danlaw – Contact Update":
            subject = f"Customer Updated - Contact Update | Request ID: {entry.unique_id} ON {entry.ticket_no} For VIN :{entry.vin}"
        elif remarks == "Assigned to Danlaw - new":
            subject = f"Re- Opened Request ID: {entry.unique_id} ON {entry.ticket_no} For VIN :{entry.vin}"
        else:
            subject = f"Update | Request ID: {entry.unique_id}"

        cc_emails = ['yoganandam@danlawtech.com', 'rajendrans@danlawtech.com', 'sales@danlawtech.com']

        # Use EmailMessage instead of send_mail to support CC
        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipient_list,
            cc=cc_emails
        )
        email.content_subtype = 'html'
        email.send()

        logger.info(f"Manager email sent successfully for ticket {entry.unique_id} to {recipient_list}")
        return True

    except Exception as e:
        logger.exception(f"Error sending manager email for ticket {entry.unique_id}: {str(e)}")
        return False


import logging

logger = logging.getLogger(__name__)


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
def push_entry_to_ialert(entry):

    if str(entry.complaint_received_by).strip() != "A.L API":
        logger.warning(
            "NOT API TICKET → Skipping IAlert push for ticket %s (complaint_received_by=%s)",
            entry.ticket_no,
            entry.complaint_received_by
        )
        return False, None, "NOT API TICKET"

    payload = {
        "ticket_id": str(entry.ticket_no),
        "remarks": str(entry.d1_d2_d3_ialert or ""),
        "comments": str(entry.ialert_comments or ""),
        "engineer_name": str(entry.complaint_assigned_to or "")
    }

    # Log the exact fields we're about to send so we can debug missing comments
    try:
        logger.debug(
            "IAlert payload fields -> ticket=%s complaint_received_by=%s remarks_in_ialert=%r d1_d2_d3_ialert=%r engineer=%r",
            entry.ticket_no,
            entry.complaint_received_by,
            entry.d1_d2_d3_ialert,
            entry.ialert_comments,
            entry.complaint_assigned_to,
        )
    except Exception:
        logger.exception("Failed to log IAlert payload debug info")

    try:
        logger.info(
            "IAlert push summary -> ticket=%s remarks_present=%s comments_present=%s comments_len=%d",
            entry.ticket_no,
            bool(entry.d1_d2_d3_ialert and str(entry.d1_d2_d3_ialert).strip()),
            bool(entry.ialert_comments and str(entry.ialert_comments).strip()),
            len(str(entry.ialert_comments or ""))
        )
    except Exception:
        logger.exception("Failed to log IAlert payload summary")

    token = _get_ialert_token()
    if not token:
        logger.error("IAlert Push Failed – No Valid Token")
        return False, None, "no-token"

    logger.info("Sending Payload to IAlert: %s", payload)

    update_url = "https://ialert2.ashokleyland.com/operation/ialertelite/api/supportticket/support-ticket-status"
                 #https://ialertuat.ashokleyland.com/operationuat/admin/api/supportticket/support-ticket-status
    try:
        resp = requests.post(
            update_url,
            json=payload,
            headers={
                "Authorization": token,
                "Content-Type": "application/json"
            },
            timeout=20
        )
        # Log full response for troubleshooting (trim body to reasonable size)
        body_snippet = (resp.text or '')[:2000]
        logger.info("IAlert Update Response -> status=%s body_snippet=%s", resp.status_code, body_snippet)

        # If response contains JSON, log parsed JSON at debug level
        try:
            j = resp.json()
            logger.debug("IAlert response JSON: %s", j)
        except ValueError:
            # non-JSON response is fine — we've already logged a snippet
            pass

        return resp.ok, resp.status_code, resp.text

    except Exception as e:
        logger.exception("IAlert Push Exception: %s", e)
        return False, None, str(e)

@require_http_methods(["GET", "POST"])
def push_entry_to_ialert_view(request, id):
    entry = get_object_or_404(DirectCall, id=id)

    ok, status, resp = push_entry_to_ialert(entry)

    return JsonResponse(
        {
            'success': ok,
            'status_code': status,
            'response': resp
        },
        status=200 if ok else 502
    )
@csrf_exempt
def ialert_callback_and_forward(request):
    return JsonResponse({"message": "IAlert callback working"}, status=200)


from django.views.decorators.http import require_GET
@require_GET
def get_call_remarks(request, id):
    """
    Returns concatenated messages (I-Alert remarks+comments, manager, D1/D2/D3, customer, remarks)
    Each message: { author, text, timestamp (ISO or '') }
    Errors are returned as JSON with 500 status.
    """
    try:
        entry = get_object_or_404(DirectCall, id=id)
        msgs = []

        def _iso_ts(ts):
            if not ts:
                return ''
            try:
                if hasattr(ts, 'isoformat'):
                    return ts.isoformat()
                # if it's a string try to return as-is
                return str(ts)
            except Exception:
                return ''

        def push(text, author, ts=None):
            if not text:
                return
            txt = str(text).strip()
            if not txt:
                return
            msgs.append({
                'author': author,
                'text': txt,
                'timestamp': _iso_ts(ts)
            })

        # I-Alert remarks + comments concatenation when both present
        r = (getattr(entry, 'remarks_in_ialert', '') or '').strip()
        c = (getattr(entry, 'ialert_comments', '') or '').strip()
        ts_ialert = getattr(entry, 'ialert_tk_timestamp', None) or getattr(entry, 'last_updated', None) or getattr(entry, 'submitted_at', None)

        if r and c:
            push(f"{r} -- {c}", 'Mgr → A.L', ts_ialert)

            # push combined D1/D2/D3 as requested (remark -- D value)
            d1_comb = ' -- '.join([str(getattr(entry, 'D1_remark', '') or '').strip(), str(getattr(entry, 'D1', '') or '').strip()]).strip()
            d2_comb = ' -- '.join([str(getattr(entry, 'D2_remark', '') or '').strip(), str(getattr(entry, 'D2', '') or '').strip()]).strip()
            d3_comb = ' -- '.join([str(getattr(entry, 'D3_remark', '') or '').strip(), str(getattr(entry, 'D3', '') or '').strip()]).strip()
            if d1_comb:
                push(d1_comb, 'D1 Remark', getattr(entry, 'D1_closure_date', None))
            if d2_comb:
                push(d2_comb, 'D2 Remark', getattr(entry, 'D2_closure_date', None))
            if d3_comb:
                push(d3_comb, 'D3 Remark', getattr(entry, 'D3_closure_date', None))
        else:
            push(r, 'Mgr → A.L', ts_ialert)
            push(c, 'I-Alert Comments', ts_ialert)

        # Manager / HOD
        push(getattr(entry, 'manager_comments', None), 'Manager', getattr(entry, 'date_of_closure', None) or getattr(entry, 'last_updated', None) or getattr(entry, 'submitted_at', None))
        push(getattr(entry, 'hod_comment', None), 'HOD', getattr(entry, 'last_updated', None))

        # If r and c were not both present, add individual D1/D2/D3 remarks
        if not (r and c):
            push(getattr(entry, 'D1_remark', None), 'D1 Remark', getattr(entry, 'D1_closure_date', None))
            push(getattr(entry, 'D2_remark', None), 'D2 Remark', getattr(entry, 'D2_closure_date', None))
            push(getattr(entry, 'D3_remark', None), 'D3 Remark', getattr(entry, 'D3_closure_date', None))

        # Customer feedback and generic remarks
        push(getattr(entry, 'customer_feedback', None), 'Customer Feedback', getattr(entry, 'feedback_submitted_datetime', None))
        push(getattr(entry, 'remarks', None), 'Remarks', getattr(entry, 'last_updated', None))

        # Sort chronologically (oldest first). Messages without parsable timestamps go to the end.
        def _parse_ts(m):
            ts = m.get('timestamp')
            # Use an aware sentinel far in the future so missing/invalid timestamps sort to the end
            sentinel = datetime.max.replace(tzinfo=pytz.UTC)

            if not ts:
                return sentinel

            # If it's already a datetime, use it
            if isinstance(ts, datetime):
                dt = ts
            else:
                # Try to parse various ISO-like strings
                try:
                    dt = parse_datetime(ts)
                except Exception:
                    dt = None

                if dt is None:
                    try:
                        dt = datetime.fromisoformat(ts)
                    except Exception:
                        return sentinel

            # Ensure dt is timezone-aware (use UTC for naive datetimes)
            if dt.tzinfo is None:
                try:
                    dt = timezone.make_aware(dt, pytz.UTC)
                except Exception:
                    dt = dt.replace(tzinfo=pytz.UTC)

            return dt

        msgs_sorted = sorted(msgs, key=_parse_ts)
        return JsonResponse({'messages': msgs_sorted})
    except Exception as e:
        logger.exception("get_call_remarks failed for id=%s", id)
        return JsonResponse({'error': str(e)}, status=500)

def send_manager_email_on_api_update(entry, remarks):
    """
    Send manager email when API receives specific remarks
    """
    # Check if remarks match the trigger conditions
    trigger_remarks = [
        "Assigned to Danlaw – Contact Update",
        "Assigned to Danlaw - new"
    ]

    if not any(trigger in remarks for trigger in trigger_remarks):
        return False

    try:

        # Prepare context for email template
        context = {
            'entry': entry,
            'site_domain': settings.SITE_DOMAIN,  # Add this to settings.py
        }

        # Render HTML email
        html_message = render_to_string(
            'direct_calls/manager_email.html',
            context
        )
        plain_message = strip_tags(html_message)

        # Send email to manager
        subject = f'New Update has - Request ID: {entry.unique_id}'
        recipient_email = entry.submitted_to_email or entry.complaint_assigned_to_email

        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient_email],
            html_message=html_message,
            fail_silently=False,
        )

        return True
    except Exception as e:
        print(f"Error sending manager email: {str(e)}")
        return False


# Your API view that receives the remarks
@csrf_exempt
def api_update_direct_call(request):
    """
    API endpoint to update direct call records
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            unique_id = data.get('unique_id')
            remarks = data.get('remarks', '')

            # Get the direct call entry
            entry = DirectCall.objects.get(unique_id=unique_id)

            # Update entry fields
            entry.remarks = remarks
            # Update other fields as needed
            entry.save()

            # Send manager email if remarks match trigger conditions
            if remarks:
                send_manager_email_on_api_update(entry, remarks)

            return JsonResponse({
                'status': 'success',
                'message': 'Record updated successfully',
                'id': entry.id
            })
        except DirectCall.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Record not found'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)