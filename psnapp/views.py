import random
from django.core.mail import EmailMessage, send_mail
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from .models import PSNEntry  # Correct import
from .forms import PSNEntryForm, EngineerResponseForm  # Correct imports
from django.contrib import messages
import csv
from django.middleware.csrf import get_token
from django.template.loader import render_to_string
import logging
from datetime import datetime, date  # Import both datetime and date
import pytz
import os
from .generate_pdf import generate_device_repair_request_pdf

logger = logging.getLogger(__name__)

def generate_unique_number():
    last_entry = PSNEntry.objects.order_by('-unique_number').first()
    if last_entry:
        return last_entry.unique_number + 1
    else:
        return 10000  # Starting point if no entries exist

def generate_centralised_id():
    current_date = timezone.now()
    year = current_date.strftime('%y')
    month = current_date.strftime('%m')
    last_entry = PSNEntry.objects.filter(centralised_id__startswith=f"DTIL{year}{month}").order_by('-centralised_id').first()
    if last_entry and last_entry.centralised_id[8:].isdigit():
        sequence_number = int(last_entry.centralised_id[8:]) + 1
    else:
        sequence_number = 1
    centralised_id = f"DTIL{year}{month}{sequence_number:04d}"
    return centralised_id

def home(request):
    entries = PSNEntry.objects.all()
    return render(request, 'psnapp/home.html', {'entries': entries})

def entry_detail(request, id):
    entry = get_object_or_404(PSNEntry, id=id)
    if entry.is_processed:
        return HttpResponse('This request has already been processed.', status=400)
    if request.method == 'POST':
        form = EngineerResponseForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            entry.is_processed = True
            entry.save()
            messages.success(request, 'The form has been submitted successfully.')
            return redirect('home')
    else:
        form = EngineerResponseForm(instance=entry)
    return render(request, 'psnapp/entry_detail.html', {'form': form, 'entry': entry})

def psn_form(request):
    if request.method == 'POST':
        form = PSNEntryForm(request.POST, request.FILES)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.unique_id = generate_unique_id(entry)
            entry.save()
            if entry.resolved_or_not == 'No':
                send_summary_email(entry)
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = PSNEntryForm()
    return render(request, 'psnapp/psn_form.html', {'form': form})

def send_summary_email(entry):
    subject = f'New FIR Entry Submitted - Request No: {entry.unique_id}'
    message = render_to_string('psnapp/manager_email.html', {
        'entry': entry,
        'approve_url': f"http://127.0.0.1:8000/approve_request/{entry.id}/",
        'reject_url': f"http://127.0.0.1:8000/reject_request/{entry.id}/",
        'view_details_url': f"http://127.0.0.1:8000/request_details/{entry.id}/"
    })
    recipient_list = [entry.manager_email]
    cc_list = [settings.HOD_EMAIL, entry.engineer_email, 'upendram@danlawtech.com']
    email = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list, cc=cc_list)
    email.content_subtype = 'html'  # To indicate the email content is HTML

    # Attach the uploaded file if it exists
    if entry.upload_file:
        email.attach_file(entry.upload_file.path)

    email.send()

def thank_you(request):
    return render(request, 'psnapp/thank_you.html')

def approve_request(request, id):
    entry = get_object_or_404(PSNEntry, id=id)
    
    # Check if the request has already been processed
    if entry.manager_approval_status in ['Approved', 'Rejected']:
        return HttpResponse('This request has already been processed.', status=400)

    entry.manager_approval_status = 'Approved'
    entry.manager_approval_datetime = timezone.now()
    entry.save()

    # Generate CSRF token
    csrf_token = get_token(request)

    # Send email to the engineer
    engineer_email = entry.engineer_email
    subject = f'FIR Request Approved - Action Required - Request No: {entry.unique_id}'
    message = render_to_string('psnapp/engineer_email.html', {
        'entry': entry,
        'csrf_token': csrf_token,
        'form_url': f"http://127.0.0.1:8000/engineer_response/{entry.id}/"
    })

    email = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, [engineer_email])
    email.content_subtype = 'html'  # To indicate the email content is HTML
    if entry.upload_file:
        email.attach_file(entry.upload_file.path)
    email.send()

    # Send email to the HOD
    hod_email = settings.HOD_EMAIL  # Email address of the HOD
    subject = 'FIR Request Approved by Manager - HOD Approval Required'
    message = render_to_string('psnapp/hod_email.html', {
        'entry': entry,
        'csrf_token': csrf_token,
        'approve_url': f"http://127.0.0.1:8000/approve_hod_request/{entry.id}/",
        'reject_url': f"http://127.0.0.1:8000/reject_hod_request/{entry.id}/",
         'view_details_url': f"http://127.0.0.1:8000/request_details/{entry.id}/"
    })
    email = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, [hod_email], cc=[engineer_email, entry.manager_email,'upendram@danlawtech.com'],)
    email.content_subtype = 'html'
    if entry.upload_file:
        email.attach_file(entry.upload_file.path)
    email.send()

    return HttpResponse('The request has been approved by the manager and sent to the HOD for approval. Mail has been sent to HOD, Once HOD approves, you and the Engineer will get an email.')

def reject_request(request, id):
    entry = get_object_or_404(PSNEntry, id=id)
    
    # Check if the request has already been processed
    if entry.manager_approval_status in ['Approved', 'Rejected']:
        return HttpResponse('This request has already been processed.', status=400)

    entry.manager_approval_status = 'Rejected'
    entry.manager_approval_datetime = timezone.now()
    entry.save()

    # Send email to the engineer
    engineer_email = entry.engineer_email
    subject = 'PSN Request Rejected'
    message = render_to_string('psnapp/engineer_rejection_email.html', {
        'entry': entry,
    })

    email = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, [engineer_email], cc=[entry.manager_email, settings.HOD_EMAIL,'upendram@danlawtech.com'])
    email.content_subtype = 'html'  # To indicate the email content is HTML
    email.send()

    return HttpResponse('The request has been rejected and the engineer has been notified. Action has been sent to the engineer.')

def approve_hod_request(request, id):
    entry = get_object_or_404(PSNEntry, id=id)
    if entry.hod_approval_status in ['Approved', 'Rejected']:
        return HttpResponse('This request has already been processed by the HOD.', status=400)
    entry.hod_approval_status = 'Approved'
    entry.hod_approval_datetime = timezone.now()
    entry.centralised_id = generate_centralised_id()
    entry.save()

    # Prepare data for PDF
    data = {
        'device_model': entry.device_model,
        'centralised_id': entry.centralised_id,
        'engineer_requested_date': entry.engineer_requested_date.strftime('%d-%m-%Y'),
        'details': {
            'Service Request Number': entry.centralised_id,
            'Date of communication failure': entry.last_communication_in_darby.strftime('%Y-%m-%d %H:%M:%S') if entry.last_communication_in_darby else 'N/A',
            'Device Model': entry.device_model,
            'Defective device PSN': entry.device_PSN,
            'VIN Number': entry.VIN_number,
            'Device IMEI': entry.device_IMEI,
            'Device CCID': entry.device_ICCID,
            'Date of Sale of Device': entry.date_of_sale_of_device.strftime('%d-%m-%Y') if entry.date_of_sale_of_device else 'N/A',
            'S Trigger Date': entry.s_trigger_date.strftime('%d-%m-%Y') if entry.s_trigger_date else 'N/A',
            'C Trigger Date': entry.c_trigger_date.strftime('%d-%m-%Y') if entry.c_trigger_date else 'N/A',
            'Commercial Expiry date': entry.commercial_expiry_date.strftime('%d-%m-%Y') if entry.commercial_expiry_date else 'N/A',
            'Active Profile (BSNL/Airtel/Dual)': entry.active_profile,
            'Vehicle Type / Model': entry.vehicle_type,
            'Failure Location Plant/ Field- Customer Address': entry.vehicle_running_location,
            'Kilometers/Hours': entry.vehicle_run,
            'Main Battery Voltage': entry.main_battery_voltage,
            'Service Engineer Name': entry.service_engineer_name,
            'Reason for Replacement/Repair': entry.engineer_recommendation,
            'Darby Last communication date': entry.last_communication_in_darby.strftime('%Y-%m-%d %H:%M:%S') if entry.last_communication_in_darby else 'N/A',
            'Device Replacement request Initiation date': entry.engineer_requested_date.strftime('%Y-%m-%d %H:%M:%S'),
            'Returnable / Non-Returnable': entry.engineer_recommendation,
        },
        'service_engineer_name': entry.service_engineer_name,
        'manager_email': entry.manager_email,
        'manager_approval_datetime': entry.manager_approval_datetime.strftime('%Y-%m-%d %H:%M:%S') if entry.manager_approval_datetime else 'N/A',
        'hod_approval_datetime': entry.hod_approval_datetime.strftime('%Y-%m-%d %H:%M:%S') if entry.hod_approval_datetime else 'N/A',
    }

    # Set the PDF file path with the desired filename format
    pdf_file_name = f"Device_{entry.engineer_recommendation}_{entry.centralised_id}.pdf"
    pdf_file_path = os.path.join('media', pdf_file_name)
    generate_device_repair_request_pdf(data, pdf_file_path)

    # Send email with PDF attachment
    email = EmailMessage(
        'Device Repair Request',
        'Please find the attached Device Repair Request.',
        settings.DEFAULT_FROM_EMAIL,
        [entry.engineer_email],  # To: Engineer's email
        cc=[settings.HOD_EMAIL]  # CC: Manager and HOD emails
    )
    email.attach_file(pdf_file_path)
    if entry.upload_file:
        email.attach_file(entry.upload_file.path)
    email.send()

    return HttpResponse('Thanks for approval. Engineer will receive confirmation to fill the additional details.')

def reject_hod_request(request, id):
    entry = get_object_or_404(PSNEntry, id=id)
    if entry.hod_approval_status in ['Approved', 'Rejected']:
        return HttpResponse('This request has already been processed by the HOD.', status=400)
    entry.hod_approval_status = 'Rejected'
    entry.hod_approval_datetime = timezone.now()
    entry.save()
    
    engineer_email = entry.engineer_email
    manager_email = entry.manager_email
    hod_email = settings.HOD_EMAIL

    subject = 'PSN Request Rejected by HOD'
    message = render_to_string('psnapp/engineer_rejection_email.html', {'entry': entry})
    
    email = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, [engineer_email], cc=[manager_email, hod_email,'upendram@danlawtech.com'])
    email.content_subtype = 'html'
    email.send()
    
    return HttpResponse('The request has been rejected by the HOD and the engineer has been notified.')

def download_data(request):
    # Get the Indian Standard Time (IST) timezone
    ist = pytz.timezone('Asia/Kolkata')

    # Create the HttpResponse object with the appropriate CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="FIR_ENTRIES.csv"'

    writer = csv.writer(response)
    # Write the header row
    writer.writerow([
        'Date of Complaint', 'Centralised ID', 'Unique ID', 'Customer Raised Issue', 'Complaint Raised By',
        'Complaint Raised Name', 'Contact Number', 'Complaint Raised Through', 'Service Engineer Name',
        'Device Model', 'Device PSN', 'VIN Number', 'Firmware', 'Configuration', 'Device IMEI', 'Device ICCID',
        'Date of Sale of Device', 'Telco Status', 'Active Profile', 'Vehicle Sale Date', 'S Trigger Date',
        'C Trigger Date', 'Commercial Expiry Date', 'First Communication in Darby', 'Last Communication in Darby',
        'Vehicle Type', 'Vehicle Running Location', 'Vehicle Run', 'Kilometers/Hours', 'Main Battery Voltage',
        'Vehicle Support Date', 'Issue Identified', 'External Modification', 'Issue Analysis', 'Resolved or Not',
        'Issue Description', 'Engineer Recommendation', 'Engineer Email', 'Manager Remarks', 'Manager Email',
        'Manager Approval Datetime', 'HOD Remarks', 'HOD Approval Status', 'HOD Approval Datetime', 'Device to be Sent',
        'Upload File', 'Unique ID'
    ])

    entries = PSNEntry.objects.all()
    for entry in entries:
        # Helper function to handle datetime conversion
        def convert_to_ist(dt):
            if isinstance(dt, datetime):  # If it's a datetime object
                return dt.astimezone(ist).strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(dt, date):  # If it's a date object
                dt_with_time = datetime.combine(dt, datetime.min.time())  # Add time (midnight)
                return ist.localize(dt_with_time).strftime('%Y-%m-%d %H:%M:%S')
            return 'N/A'

        # Convert all datetime fields to IST
        date_of_complaint = convert_to_ist(entry.date_of_complaint)
        date_of_sale_of_device = convert_to_ist(entry.date_of_sale_of_device)
        vehicle_sale_date = convert_to_ist(entry.vehicle_sale_date)
        s_trigger_date = convert_to_ist(entry.s_trigger_date)
        c_trigger_date = convert_to_ist(entry.c_trigger_date)
        commercial_expiry_date = convert_to_ist(entry.commercial_expiry_date)
        first_communication_in_darby = convert_to_ist(entry.first_communication_in_darby)
        last_communication_in_darby = convert_to_ist(entry.last_communication_in_darby)
        vehicle_support_date = convert_to_ist(entry.vehicle_support_date)
        manager_approval_datetime = convert_to_ist(entry.manager_approval_datetime)
        hod_approval_datetime = convert_to_ist(entry.hod_approval_datetime)

        # Write the row
        writer.writerow([
            date_of_complaint,
            entry.centralised_id,
            entry.unique_id,
            entry.complaint_raised_name,
            entry.complaint_raised_by,
            entry.complaint_raised_name,
            entry.contact_number,
            entry.complaint_raised_through,
            entry.service_engineer_name,
            entry.device_model,
            entry.device_PSN,
            entry.VIN_number,
            entry.firmware,
            entry.configuration,
            entry.device_IMEI,
            entry.device_ICCID,
            date_of_sale_of_device,
            entry.telco_status,
            entry.active_profile,
            vehicle_sale_date,
            s_trigger_date,
            c_trigger_date,
            commercial_expiry_date,
            first_communication_in_darby,
            last_communication_in_darby,
            entry.vehicle_type,
            entry.vehicle_running_location,
            entry.vehicle_run,
            entry.kilometers_hours,
            entry.main_battery_voltage,
            vehicle_support_date,
            entry.issue_identified,
            entry.external_modification,
            entry.issue_analysis,
            entry.resolved_or_not,
            entry.issue_description,
            entry.engineer_recommendation,
            entry.engineer_email,
            entry.manager_remarks,
            entry.manager_email,
            manager_approval_datetime,
            entry.hod_remarks,
            entry.hod_approval_status,
            hod_approval_datetime,
            entry.device_to_be_sent,
            entry.upload_file.url if entry.upload_file else 'N/A',
            entry.unique_id
        ])

    return response

def engineer_response(request, id):
    entry = get_object_or_404(PSNEntry, id=id)
    if entry.is_processed:
        return HttpResponse('This request has already been processed.', status=400)
    if request.method == 'POST':
        form = EngineerResponseForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            entry.is_processed = True
            entry.save()
            messages.success(request, 'The form has been submitted successfully.')
            return redirect('home')
    else:
        form = EngineerResponseForm(instance=entry)
    return render(request, 'psnapp/engineer_response.html', {'form': form, 'entry': entry})

def thank_you(request):
    return render(request, 'psnapp/thank_you.html')

def form_submission_view(request):
    if request.method == 'POST':
        form = PSNEntryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Engineer has submitted the form. Your manager is reviewing it soon.')
            return redirect('thank_you')  # Replace with your actual success URL
    else:
        form = PSNEntryForm()
    return render(request, 'form_template.html', {'form': form})

def filter_entries(request):
    filtered_entries = PSNEntry.objects.filter(unique_id__startswith='123')
    return render(request, 'psnapp/filtered_entries.html', {'entries': filtered_entries})

def download_psn_entries(request):
    entries = PSNEntry.objects.all()
    response_content = []

    for entry in entries:
        try:
            date_of_complaint = entry.date_of_complaint.isoformat() if entry.date_of_complaint else 'N/A'

            date_of_sale_of_device = entry.date_of_sale_of_device.isoformat() if entry.date_of_sale_of_device else 'N/A'
            s_trigger_date = entry.s_trigger_date.isoformat() if entry.s_trigger_date else 'N/A'
            c_trigger_date = entry.c_trigger_date.isoformat() if entry.c_trigger_date else 'N/A'
            commercial_expiry_date = entry.commercial_expiry_date.isoformat() if entry.commercial_expiry_date else 'N/A'
            first_communication_on_darby = entry.first_communication_on_darby.isoformat() if entry.first_communication_on_darby else 'N/A'
            last_communication_on_darby = entry.last_communication_on_darby.isoformat() if entry.last_communication_on_darby else 'N/A'
            vehicle_support_date = entry.vehicle_support_date.isoformat() if entry.vehicle_support_date else 'N/A'
            vehicle_sale_date = entry.vehicle_sale_date.isoformat() if entry.vehicle_sale_date else 'N/A'
            date_of_closure = entry.date_of_closure.isoformat() if entry.date_of_closure else 'N/A'
        except AttributeError as e:
            return HttpResponse(f"Error: {e}", status=500)

        response_content.append(f"{date_of_complaint}, {date_of_sale_of_device}, {s_trigger_date}, {c_trigger_date}, {commercial_expiry_date}, {first_communication_on_darby}, {last_communication_on_darby}, {vehicle_support_date}, {vehicle_sale_date}, {date_of_closure}\n")

    response = HttpResponse(response_content, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="psn_entries.csv"'
    return response

def success(request):
    return render(request, 'psnapp/success.html')

def request_details(request, id):
    entry = get_object_or_404(PSNEntry, id=id)  # Fetch the PSNEntry instance by ID
    edit_mode = request.GET.get('edit', 'false') == 'true'  # Check if edit mode is enabled

    if request.method == 'POST' and edit_mode:
        if entry.hod_approval_status == 'Approved':
            messages.error(request, 'This entry has been approved by the HOD and cannot be edited.')
        else:
            form = PSNEntryForm(request.POST, request.FILES, instance=entry)  # Bind the form to the existing instance
            if form.is_valid():
                form.save()  # Save the updated data
                messages.success(request, 'The entry has been updated successfully.')
                return redirect('request_details', id=entry.id)  # Redirect to the same page to reflect changes
            else:
                messages.error(request, 'There was an error updating the entry. Please check the form.')
    else:
        form = PSNEntryForm(instance=entry)  # Populate the form with existing data

    return render(request, 'psnapp/psn_form_edit.html', {'form': form, 'entry': entry, 'edit_mode': edit_mode})

def psn_entry_create(request):
    if request.method == 'POST':
        form = PSNEntryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('psn_entry_list')
    else:
        form = PSNEntryForm()
    return render(request, 'psnapp/psn_entry_form.html', {'form': form})

def psn_entry_update(request, pk):
    psn_entry = get_object_or_404(PSNEntry, pk=pk)
    if request.method == 'POST':
        form = PSNEntryForm(request.POST, instance=psn_entry)
        if form.is_valid():
            form.save()
            return redirect('psn_entry_list')
    else:
        form = PSNEntryForm(instance=psn_entry)
    return render(request, 'psnapp/psn_entry_form.html', {'form': form})

def psn_entry_list(request):
    psn_entries = PSNEntry.objects.all()
    return render(request, 'psnapp/psn_entry_list.html', {'psn_entries': psn_entries})

def generate_unique_id(entry):
    service_engineer_initial = entry.service_engineer_name[0].upper()
    current_date = timezone.now()
    year = current_date.strftime('%y')
    month = current_date.strftime('%m')
    last_entry = PSNEntry.objects.filter(unique_id__startswith=service_engineer_initial + year + month).order_by('-unique_id').first()
    if last_entry and last_entry.unique_id[6:].isdigit():
        sequence_number = int(last_entry.unique_id[6:]) + 1
    else:
        sequence_number = 0
    unique_id = f"{service_engineer_initial}{year}{month}{sequence_number:04d}"
    return unique_id

def psn_form_edit(request, id):
    entry = get_object_or_404(PSNEntry, id=id)
    if request.method == 'POST':
        if entry.hod_approval_status == 'Approved':
            messages.error(request, 'This entry has been approved by the HOD and cannot be edited.')
        else:
            form = PSNEntryForm(request.POST, request.FILES, instance=entry)
            if form.is_valid():
                form.save()
                messages.success(request, 'The entry has been updated successfully.')
                return redirect('request_details', id=entry.id)
            else:
                messages.error(request, 'There was an error updating the entry. Please check the form.')
    else:
        form = PSNEntryForm(instance=entry)
    return render(request, 'psnapp/psn_form_edit.html', {'form': form, 'entry': entry})