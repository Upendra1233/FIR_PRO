from django.shortcuts import render, get_object_or_404, redirect
from django.core.mail import EmailMessage
from django.conf import settings
from django.http import JsonResponse
from .forms import DirectCallForm, ManagerForm, EngineerForm
from .models import DirectCall
import logging
from django.template.loader import render_to_string
import csv
from django.http import HttpResponse
from datetime import datetime, timedelta
from django.utils.timezone import localtime, now
import traceback
from pytz import timezone
from django.contrib import messages
logger = logging.getLogger(__name__)

def direct_call_form(request):
    if request.method == 'POST':
        try:
            form = DirectCallForm(request.POST, request.FILES)
            if form.is_valid():
                entry = form.save(commit=False)  # Don't save to the database yet
                current_time = now()
                ist_time = current_time + timedelta(hours=5, minutes=30)
                entry.submitted_at = ist_time  # Set the adjusted time
                entry.date_of_complaint = datetime.now()
                entry.save()  # Save the object to the database

                # Convert submitted_at to local time (IST) for logging and response
                submitted_at_ist = localtime(entry.submitted_at)
                logger.info(f"Submitted at (IST): {submitted_at_ist}")
                return JsonResponse({
                    'success': True,
                    'message': 'Form submitted successfully!',
                    'unique_id': entry.unique_id,
                    'submitted_at': submitted_at_ist.strftime('%Y-%m-%d %H:%M:%S')  # Format as string
                })
            else:
                return JsonResponse({'success': False, 'errors': form.errors})
        except Exception as e:
            logger.error(f"Unexpected error in direct_call_form: {e}")
            return JsonResponse({'success': False, 'message': 'An unexpected error occurred. Please try again.'})
    else:
        form = DirectCallForm()
    return render(request, 'direct_calls/direct_calls_form.html', {'form': form})

def manager_form(request):
    if request.method == 'POST':
        try:
            post_data = request.POST.copy()

            dropdown_fields = ['complaint_raised', 'complaint_raised_through', 'complaint_assigned_to', 'call_type']
            for field in dropdown_fields:
                if post_data.get(field) == 'others':
                    post_data[field] = post_data.get(f"{field}_other", 'others')


            form = ManagerForm(post_data, request.FILES)
            if form.is_valid():
                entry = form.save()

                # Prepare email data for engineer and sales
                context = {
                    'entry': entry,
                    'site_domain': request.build_absolute_uri('/').rstrip('/')
                }
                subject = f"{entry.unique_id} CRSC Assigned to {entry.complaint_assigned_to} ON {entry.vin}"
                email_body = render_to_string('direct_calls/manager_email.html', context)

                # Email recipients
                engineer_email = entry.submitted_to_email
                sales_emails = [
                    'upendram@danlawtech.com',
                    'sales@danlawtech.com'# Add the additional email here
                ]

                # Send email to engineer and sales
                email = EmailMessage(
                    subject,
                    email_body,
                    settings.DEFAULT_FROM_EMAIL,
                    [engineer_email],  # To address
                    cc=sales_emails    # CC addresses
                )
                email.content_subtype = 'html'

                # Attach the uploaded file if it exists
                uploaded_file = request.FILES.get('upload_file')  # Ensure the field name matches
                if uploaded_file:
                    try:
                        email.attach(uploaded_file.name, uploaded_file.read(), uploaded_file.content_type)
                        logger.info(f"File {uploaded_file.name} attached successfully.")
                    except Exception as e:
                        logger.error(f"Failed to attach file: {e}")
                else:
                    logger.warning("No file uploaded to attach.")

                # Send the email
                try:
                    email.send()
                    logger.info(f"Email sent successfully to engineer and sales: {sales_emails}")
                except Exception as e:
                    logger.error(f"Error sending email: {e}")

                # Prepare email data for customer
                customer_subject = f"Ticket Created: {entry.unique_id} for Your Request"
                customer_email_body = render_to_string('direct_calls/customer_email.html', context)

                # Send email to customer
                customer_email = entry.customer_mail_id
                if customer_email:  # Ensure customer email exists
                    customer_email_message = EmailMessage(
                        customer_subject,
                        customer_email_body,
                        settings.DEFAULT_FROM_EMAIL,
                        [customer_email]
                    )
                    customer_email_message.content_subtype = 'html'
                    customer_email_message.send()
                    logger.info(f"Email sent successfully to customer: {customer_email}")

            else:
                logger.error(f"Form errors: {form.errors}")
                return JsonResponse({'success': False, 'errors': form.errors})

        except Exception as e:
            logger.error(f"Unexpected error in manager_form: {traceback.format_exc()}")
            return JsonResponse({'success': False, 'message': 'An unexpected error occurred. Please try again.'})

    else:
        form = ManagerForm()

    return render(request, 'direct_calls/manager_form.html', {'form': form})

def engineer_form(request, id):
    entry = get_object_or_404(DirectCall, id=id)
    is_closed = entry.call_status in ["Resolved", "Closed"]

    if request.method == 'POST' and not is_closed:
        post_data = request.POST.copy()
        form = EngineerForm(post_data, instance=entry)

        if form.is_valid():
            entry = form.save(commit=False)
            call_status = post_data.get('call_status')
            entry.call_status = call_status

            # If call is resolved or closed
            if call_status in ['Resolved', 'Closed']:
                entry.date_of_closure = now()

                # Prepare email context
                context = {
                    'entry': entry,
                    'site_domain': request.build_absolute_uri('/').rstrip('/')
                }

                subject = f"CRSC {call_status}: {entry.unique_id} - {entry.vin}"
                email_body = render_to_string('direct_calls/manager_call_closed_email.html', context)

                try:
                    # Define the recipient and CC emails
                    engineer_email = entry.submitted_to_email  # Engineer's email
                    cc_emails = ['sales@danlawtech.com', 'mupendramzvpsp@gmail.com']  # CC emails

                    # Create and send the email
                    email = EmailMessage(
                        subject=subject,
                        body=email_body,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[engineer_email],  # Primary recipient
                        cc=cc_emails          # CC recipients
                    )
                    email.content_subtype = 'html'
                    email.send()
                    logger.info(f"{call_status} email sent to engineer ({engineer_email}) and CC ({cc_emails}) for: {entry.unique_id}")
                except Exception as e:
                    logger.error(f"Failed to send {call_status} email to engineer and CC: {e}")

            # Save the form data
            entry.save()
            return JsonResponse({'success': True, 'message': 'Form submitted successfully!'})

        else:
            logger.error(f"Form errors: {form.errors}")
            return JsonResponse({'success': False, 'errors': form.errors})

    else:
        form = EngineerForm(instance=entry)

        # If call is closed or resolved, make the form non-editable
        if is_closed:
            for field in form.fields:
                form.fields[field].widget.attrs['readonly'] = True
            form.fields['call_status'].widget.attrs['disabled'] = True

    return render(request, 'direct_calls/engineer_form.html', {
        'form': form,
        'entry': entry,
        'is_closed': is_closed,
    })


def approve_request(request, call_id):
    try:
        # Fetch the DirectCall object
        direct_call = get_object_or_404(DirectCall, id=call_id)
        direct_call.call_status = 'Approved'  # Update the status
        direct_call.save()

        # Send email to the engineer with the form URL
        subject = f"Customer Resolution Service Support Direct call Assigned to {direct_call.complaint_assigned_to} ON {direct_call.vin} ID: {direct_call.unique_id}"
        recipient_email = direct_call.submitted_to_email  # Engineer's email from the model
        cc_emails = ['manager@example.com', recipient_email]  # Add CC emails if needed
        context = {
            'direct_call': direct_call,
            'form_url': f"http://127.0.0.1:8000/direct_calls/engineer_form/{direct_call.id}/",
        }
        email_body = render_to_string('direct_calls/engineer_email.html', context)
        email = EmailMessage(subject, email_body, to=[recipient_email], cc=cc_emails)
        email.content_subtype = 'html'
        email.send()

        return JsonResponse({'success': True, 'message': 'Request approved and email sent to engineer.'})
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return JsonResponse({'success': False, 'message': 'An unexpected error occurred. Please try again.'})


import csv
from django.http import HttpResponse
from .models import DirectCall
from pytz import timezone
def download_csv(request):
    response = HttpResponse(content_type='text/csv')
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'Direct_calls_Data_{timestamp}.csv'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # Define the field names in the desired order.
    fieldnames = [
        'unique_id', 'date_of_complaint', 'complaint_raised_from_location', 'customer_raised_issue', 'complaint_raised',
        'complaint_raised_by', 'contact_number', 'customer_mail_id', 'complaint_raised_through',
        'complaint_received_by', 'vin', 'complaint_assigned_to', 'submitted_to_email',
        'engineer_contact_number', 'upload_file', 'psn', 'device_model', 'telco_status',
        'active_profile', 'activation_start_date', 'activation_end_date', 'vehicle_sale_date',
        'first_communication_in_darby', 'last_communication_in_darby', 'vehicle_type', 'vehicle_run',
        'kilometers_hours', 'main_battery_voltage', 'vehicle_running_location', 'state', 'region',
        'contact_person_name', 'contact_person_number', 'contact_category', 'issue_identified',
        'issue_analysis', 'exist_software', 'updated_software', 'final_action_taken',
        'finalised_issue_category','upload_file_01', 'call_status', 'date_of_closure'
    ]

    # Create a CSV writer object.
    writer = csv.DictWriter(response, fieldnames=fieldnames)
    writer.writeheader()

    # Define the IST timezone.
    ist = timezone('Asia/Kolkata')

    # Fetch all DirectCall objects and write their data to the CSV.
    for call in DirectCall.objects.all():
        writer.writerow({
            'unique_id': call.unique_id,
            'date_of_complaint': call.date_of_complaint.astimezone(ist).strftime('%Y-%m-%d %H:%M:%S') if call.date_of_complaint else '',
            'complaint_raised_from_location': call.complaint_raised_from_location,
            'customer_raised_issue': call.customer_raised_issue,
            'complaint_raised': call.complaint_raised,
            'complaint_raised_by': call.complaint_raised_by,
            'contact_number': call.contact_number,
            'customer_mail_id': call.customer_mail_id,
            'complaint_raised_through': call.complaint_raised_through,
            'complaint_received_by': call.complaint_received_by,
            'vin': call.vin,
            'complaint_assigned_to': call.complaint_assigned_to,
            'submitted_to_email': call.submitted_to_email,
            'engineer_contact_number': call.engineer_contact_number,
            'upload_file': call.upload_file.url if call.upload_file else '',
            'psn': call.psn,
            'device_model': call.device_model,
            'telco_status': call.telco_status,
            'active_profile': call.active_profile,
            'activation_start_date': call.activation_start_date.astimezone(ist).strftime('%Y-%m-%d %H:%M:%S') if call.activation_start_date else '',
            'activation_end_date': call.activation_end_date.astimezone(ist).strftime('%Y-%m-%d %H:%M:%S') if call.activation_end_date else '',
            'vehicle_sale_date': call.vehicle_sale_date.strftime('%Y-%m-%d') if call.vehicle_sale_date else '',
            'first_communication_in_darby': call.first_communication_in_darby.astimezone(ist).strftime('%Y-%m-%d %H:%M:%S') if call.first_communication_in_darby else '',
            'last_communication_in_darby': call.last_communication_in_darby.astimezone(ist).strftime('%Y-%m-%d %H:%M:%S') if call.last_communication_in_darby else '',
            'vehicle_type': call.vehicle_type,
            'vehicle_run': call.vehicle_run,
            'kilometers_hours': call.kilometers_hours,
            'main_battery_voltage': call.main_battery_voltage,
            'vehicle_running_location': call.vehicle_running_location,
            'state': call.state,
            'region': call.region,
            'contact_person_name': call.contact_person_name,
            'contact_person_number': call.contact_person_number,
            'contact_category': call.contact_category,
            'issue_identified': call.issue_identified,
            'issue_analysis': call.issue_analysis,
            'exist_software': call.exist_software,
            'updated_software': call.updated_software,
            'final_action_taken': call.final_action_taken,
            'finalised_issue_category': call.finalised_issue_category,
            'upload_file_01': call.upload_file_01.url if call.upload_file_01 else '',
            'call_status': call.call_status,
            'date_of_closure': call.date_of_closure.astimezone(ist).strftime('%Y-%m-%d %H:%M:%S') if call.date_of_closure else '',
        })

    return response

