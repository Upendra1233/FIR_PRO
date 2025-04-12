from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.core.mail import EmailMessage, send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.timezone import now, localtime
from .forms import MappingProcessForm
from .models import MappingProcess  # Import the MappingProcess model
from pytz import timezone

def mapping_process_form(request):
    if request.method == 'POST':
        # Create a mutable copy of POST data to handle "Others" values
        post_data = request.POST.copy()

        # Handle "Others" values for dropdowns
        dropdown_fields_with_others = [
            'req_raised_by',
            'old_device_telco_status',
            'old_device_return_location',
            'current_card_status_of_new_device',
            'activation_status_of_new_device',
            'new_device_telco_status',
        ]

        for field in dropdown_fields_with_others:
            if post_data.get(field) == 'Others':
                post_data[field] = post_data.get(f'{field}_other', '')

        # Pass the modified data to the form
        form = MappingProcessForm(post_data)
        if form.is_valid():
            instance = form.save()  # Save the form data to the database
            print(f"Form saved successfully. Ticket ID: {instance.ticket_id}")

            # Generate URLs for approval and rejection
            approve_url = request.build_absolute_uri(f"/mapping_process/approve/{instance.id}/")
            reject_url = request.build_absolute_uri(f"/mapping_process/reject/{instance.id}/")
            view_url = request.build_absolute_uri(f"/mapping_process/view/{instance.id}/")

            # Send email to the manager
            subject = f"Approval Needed for Mapping Request {instance.ticket_id}"
            recipient_email = "sales@danlawtech.com"  # Manager's email
            context = {
                'entry': instance,
                'approve_url': approve_url,
                'reject_url': reject_url,
                'view_url': view_url,
            }
            email_body = render_to_string('mapping_process/email_template.html', context)
            email = EmailMessage(subject, email_body, to=[recipient_email])
            email.content_subtype = 'html'  # Set the email content type to HTML
            email.send()

            return JsonResponse({'success': True, 'message': 'Form submitted successfully!'})
        else:
            print("Form errors:", form.errors)  # Log form errors
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = MappingProcessForm()
    return render(request, 'mapping_process/mapping_process_form.html', {'form': form})

def mapping_process_editable_form(request, process_id):
    instance = get_object_or_404(MappingProcess, id=process_id)
    if request.method == 'POST':
        form = MappingProcessForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'Form updated successfully!'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = MappingProcessForm(instance=instance)
    return render(request, 'mapping_process/mapping_process_editable_form.html', {'form': form, 'instance': instance})

def approve_request(request, request_id):
    instance = get_object_or_404(MappingProcess, id=request_id)
    instance.manager_approval_status = 'Approved'
    instance.manager_approval_time = now()

    # Convert to IST and format datetime
    ist_timezone = timezone('Asia/Kolkata')
    manager_approval_time_ist = instance.manager_approval_time.astimezone(ist_timezone)
    instance.manager_approval_time = manager_approval_time_ist.replace(microsecond=0)  # Remove microseconds
    instance.save()

    # Notify the engineer about the approval
    if instance.submitted_by:
        subject = f"Request {instance.ticket_id} Approved"
        message = f"""
        Dear Engineer,

        The request with ID {instance.ticket_id} has been approved by the manager.
        Action Taken: Approved
        Approval Time: {manager_approval_time_ist.strftime('%Y-%m-%d %H:%M:%S')} IST
        Remarks: {instance.hod_remarks}

        Please proceed with the next steps as per the approval.
        Best regards,
        Your Team
        """
        email = EmailMessage(subject, message, to=[instance.submitted_by, "sales@danlawtech.com"])
        email.send()

    return HttpResponse(f"Request {instance.ticket_id} has been approved.")

def reject_request(request, request_id):
    instance = get_object_or_404(MappingProcess, id=request_id)
    instance.manager_approval_status = 'Rejected'
    instance.manager_approval_time = now()

    # Convert to IST and format datetime
    ist_timezone = timezone('Asia/Kolkata')
    manager_approval_time_ist = instance.manager_approval_time.astimezone(ist_timezone)
    instance.manager_approval_time = manager_approval_time_ist.replace(microsecond=0)  # Remove microseconds
    instance.save()

    # Notify the engineer about the rejection
    if instance.submitted_by:
        subject = f"Request {instance.ticket_id} Rejected"
        message = f"""
        Dear Engineer,

        The request with ID {instance.ticket_id} has been rejected by the manager.
        Action Taken: Rejected
        Rejection Time: {manager_approval_time_ist.strftime('%Y-%m-%d %H:%M:%S')} IST
        Remarks: {instance.hod_remarks}

        Please take the necessary actions as per the rejection.
        Best regards,
        Your Team
        """
        email = EmailMessage(subject, message, to=[instance.submitted_by, "sales@danlawtech.com"])
        email.send()

    return HttpResponse(f"Request {instance.ticket_id} has been rejected.")

import csv
from django.http import HttpResponse
from .models import MappingProcess

def download_data(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'Mapping_Process_Data_{timestamp}.csv'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # Create a CSV writer
    writer = csv.writer(response)

    # Write the header row in the specified order
    writer.writerow([
        'Request ID',
        'Mapping Requested status',
        'Manager Approval Datetime',
        'Mapping Requested Date',
        'Request Raised By',
        'VIN',
        'Old PSN',
        'Date of Old Device Sales',
        '1st S Activation of Old Device',
        '1st C Activation of Old Device',
        'Old Device Telco Status',
        'Old Device Validity',
        'Old Device Return Location',
        'Current Card Status of New Device',
        'Activation Status of New Device',
        'New Device Telco Status',
        'Current Validity Status of New Device',
        'Added Validity for New Device',
        'New PSN',
        'Submitted By',
        'HOD Remarks',
        'Mapping Done By',
        'Mapping Completion Date',
        'Warranty of the Device',
    ])

    # Write the data rows in the specified order
    for entry in MappingProcess.objects.all():
        writer.writerow([
            entry.ticket_id,
            entry.manager_approval_status,
            entry.manager_approval_time.astimezone(timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S') if entry.manager_approval_time else '',
            entry.mapping_req_received_date.astimezone(timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S') if entry.mapping_req_received_date else '',
            entry.req_raised_by,
            entry.vin,
            entry.old_psn,
            entry.date_of_old_device_sales.strftime('%Y-%m-%d') if entry.date_of_old_device_sales else '',
            entry.first_s_activation_of_old_device.strftime('%Y-%m-%d') if entry.first_s_activation_of_old_device else '',
            entry.first_c_activation_of_old_device.strftime('%Y-%m-%d') if entry.first_c_activation_of_old_device else '',
            entry.old_device_telco_status,
            entry.old_device_validity.strftime('%Y-%m-%d') if entry.old_device_validity else '',
            entry.old_device_return_location,
            entry.current_card_status_of_new_device,
            entry.activation_status_of_new_device,
            entry.new_device_telco_status,
            entry.current_validity_status_of_new_device.strftime('%Y-%m-%d') if entry.current_validity_status_of_new_device else '',
            entry.added_validity_for_new_device,
            entry.new_psn,
            entry.submitted_by,
            entry.hod_remarks,
            entry.mapping_done_by,
            entry.mapping_completion_date.strftime('%Y-%m-%d') if entry.mapping_completion_date else '',
            entry.warranty_of_the_device.strftime('%Y-%m-%d') if entry.warranty_of_the_device else '',
        ])

    return response
