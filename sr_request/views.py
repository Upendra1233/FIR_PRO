from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from .forms import SRRequestForm, SRDetailsForm, NewSRDetailsForm
from .models import SRRequest
import logging
from django.utils.timezone import now
import csv
from datetime import datetime
from django.urls import reverse
from django.utils.http import urlencode

logger = logging.getLogger(__name__)

def sr_request_form(request):
    if request.method == 'POST':
        # Create a mutable copy of POST data to modify it
        post_data = request.POST.copy()

        # Check and replace "Others" values with the custom input
        if post_data.get('engineer') == 'Others':
            post_data['engineer'] = post_data.get('engineer_other', '').strip()
        if post_data.get('category') == 'Others':
            post_data['category'] = post_data.get('category_other', '').strip()
        if post_data.get('plan') == 'Others':
            post_data['plan'] = post_data.get('plan_other', '').strip()
        if post_data.get('billing_to') == 'Others':
            post_data['billing_to'] = post_data.get('billing_to_other', '').strip()
         
        # Pass the modified data to the form
        form = SRRequestForm(post_data)
        if form.is_valid():
            sr_request = form.save()

            # Send email to manager
            subject = f"Approval Needed for SR Request {sr_request.unique_id}"
            recipient_email = 'upendram@danlawtech.com'  # Manager's email from settings
            cc_emails = [sr_request.engineer_email,'sales@danlawtech.com']  # Add CC email addresses
            context = {
                'sr_request': sr_request,
                'view_details_url': f"http://127.0.0.1:8000/sr_request/view/{sr_request.id}/",
                'edit_url': f"http://127.0.0.1:8000/sr_request/edit/{sr_request.id}/",
                'approve_url': f"http://127.0.0.1:8000/sr_request/approve/{sr_request.id}/",
                'reject_url': f"http://127.0.0.1:8000/sr_request/reject/{sr_request.id}/",
            }
            email_body = render_to_string('sr_request/manager_email.html', context)
            email = EmailMessage(subject, email_body, to=[recipient_email], cc=cc_emails)
            email.content_subtype = 'html'
            email.send()

            return JsonResponse({'success': True, 'message': 'Form submitted successfully!'})
        else:
            print(form.errors)
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = SRRequestForm()
    return render(request, 'sr_request/sr_request_form.html', {'form': form})

def sr_request_success(request):
    return render(request, 'sr_request/success.html')

def approve_request(request, request_id):
    sr_request = get_object_or_404(SRRequest, id=request_id)
    sr_request.status = 'Approved'
    sr_request.save()

    # Generate the full URL for the new_sr_details_form
    base_url = request.build_absolute_uri('/')[:-1]  # Get the base URL (e.g., http://127.0.0.1:8000)
    form_url = f"{base_url}{reverse('new_sr_details_form', kwargs={'request_id': sr_request.id})}"

    # Send email to engineer with the form URL
    subject = f"Action Required: Fill Additional Details for SR Request {sr_request.unique_id} ON {sr_request.psn}"
    recipient_email = 'upendram@danlawtech.com'  # Engineer's email
    cc_emails = ['upendram@danlawtech.com', sr_request.engineer_email, 'sales@danlawtech.com']
    context = {
        'sr_request': sr_request,
        'form_url': form_url,  # Pass the resolved URL to the template
    }
    email_body = render_to_string('sr_request/engineer_email.html', context)
    email = EmailMessage(subject, email_body, to=[recipient_email], cc=cc_emails)
    email.content_subtype = 'html'
    email.send()

    return JsonResponse({'success': True, 'message': 'Request approved and email sent to engineer.'})

def reject_request(request, request_id):
    sr_request = get_object_or_404(SRRequest, id=request_id)
    sr_request.status = 'Rejected'
    sr_request.save()
    return JsonResponse({'success': True, 'message': 'Request rejected.'})

def sr_details_form(request, request_id):
    sr_request = get_object_or_404(SRRequest, id=request_id)

    # Check if the status is 'Closed'
    if sr_request.status == 'Closed':
        return JsonResponse({'success': False, 'message': 'This form is no longer editable as the status is Closed.'}, status=403)

    if request.method == 'POST':
        form = SRDetailsForm(request.POST, instance=sr_request)
        if form.is_valid():
            sr_request = form.save()

            # Check if the status is now set to 'Closed'
            if sr_request.status == 'Closed':
                try:
                    # Send email to the engineer
                    subject = f"SR Request {sr_request.unique_id} - Status Closed Notification"
                    recipient_email = sr_request.engineer_email  # Engineer's email from the model
                    if not recipient_email:
                        logger.error("Recipient email is missing.")
                        return JsonResponse({'success': False, 'message': 'Recipient email is missing.'}, status=400)

                    context = {
                        'sr_request': sr_request,
                    }
                    email_body = render_to_string('sr_request/manager_notification.html', context)
                    email = EmailMessage(subject, email_body, to=[recipient_email], cc=['sales@danlawtech.com'])
                    email.content_subtype = 'html'
                    email.send()
                    logger.info(f"Email sent successfully to {recipient_email}")
                except Exception as e:
                    logger.error(f"Failed to send email: {e}")
                    return JsonResponse({'success': False, 'message': f'Failed to send email: {e}'}, status=500)

            return JsonResponse({'success': True, 'message': 'Details submitted successfully!'})
        else:
            logger.error(f"Form errors: {form.errors}")
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = SRDetailsForm(instance=sr_request)
    return render(request, 'sr_request/sr_details_form.html', {'form': form, 'sr_request': sr_request})

def edit_sr_request_form(request, request_id):
    sr_request = get_object_or_404(SRRequest, id=request_id)

    # Check if the status is 'Approved'
    if sr_request.status == 'Approved':
        # Render the form as read-only
        form = SRRequestForm(instance=sr_request)
        for field in form.fields.values():
            field.widget.attrs['readonly'] = True
            field.widget.attrs['disabled'] = True
        return render(request, 'sr_request/sr_details_form.html', {'form': form, 'sr_request': sr_request, 'edit_mode': False, 'read_only': True})

    if request.method == 'POST':
        form = SRRequestForm(request.POST, instance=sr_request)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'Form updated successfully!'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = SRRequestForm(instance=sr_request)

    return render(request, 'sr_request/sr_details_form.html', {'form': form, 'sr_request': sr_request, 'edit_mode': True})

def view_request_details(request, request_id):
    sr_request = get_object_or_404(SRRequest, id=request_id)
    return render(request, 'sr_request/view_request_details.html', {'sr_request': sr_request})

def send_manager_email(sr_request):
    subject = f"New SR Request Submitted - Request No: {sr_request.unique_id}"
    recipient_email = "upendram@danlawtech.com"  # Manager's email from settings
    cc_emails = [sr_request.engineer_email, 'sales@danlawtech.com']
    context = {
        'sr_request': sr_request,
        'view_details_url': f"http://127.0.0.1:8000/sr_request/view/{sr_request.id}/",
        'edit_url': f"http://127.0.0.1:8000/sr_request/edit/{sr_request.id}/",
        'approve_url': f"http://127.0.0.1:8000/sr_request/approve/{sr_request.id}/",
        'reject_url': f"http://127.0.0.1:8000/sr_request/reject/{sr_request.id}/",
    }
    email_body = render_to_string('sr_request/manager_email.html', context)
    email = EmailMessage(subject, email_body, to=[recipient_email], cc=cc_emails)
    email.content_subtype = 'html'
    email.send()

def approve_manager_request(request, id):
    logger.info(f"approve_manager_request called for ID: {id}")
    logger.info(f"Approving request with ID: {id}")

    # Fetch the SRRequest object
    sr_request = get_object_or_404(SRRequest, id=id)

    # Log the current status and datetime
    logger.info(f"Before update: Status={sr_request.manager_approval_status}, Datetime={sr_request.manager_approval_datetime}")

    # Update the manager approval fields
    sr_request.manager_approval_status = 'Approved'
    sr_request.manager_approval_datetime = now()

    # Save the updated fields
    sr_request.save()

    # Log the updated status and datetime
    logger.info(f"After update: Status={sr_request.manager_approval_status}, Datetime={sr_request.manager_approval_datetime}")

    # Return a success response
    return HttpResponse('Manager has approved the request.')

def download_sr_requests(request):
    # Generate a dynamic filename with the current date and time
    timestamp = datetime.now().strftime('%d_%m_%Y_%H_%M')
    filename = f"SR_Requests_{timestamp}.csv"

    # Create the HttpResponse object with the appropriate CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # Create a CSV writer
    writer = csv.writer(response)

    # Write the header row
    writer.writerow([
        'ID', 'Request ID','Date', 'Category', 'PSN', 'ICICID', 'Engineer', 'Requestor Comments',
        'Plan', 'Existing Validity', 'Requestor Validity Start Date', 'Requestor Validity End Date',
        'Billing To', 'SIM Status During Request', 'Remarks', 'HOD Remarks', 'Status',
        'New SR No', 'SR Date', 'SR Success Date', 'Engineer Email',
        'Manager Approval Status', 'Manager Approval Datetime'
    ])

    # Write data rows
    sr_requests = SRRequest.objects.all()
    for sr_request in sr_requests:
        writer.writerow([
            sr_request.id,
            sr_request.unique_id,
            sr_request.date.strftime('%Y-%m-%d %H:%M:%S') if sr_request.date else 'N/A',
            sr_request.category,
            sr_request.psn,
            sr_request.icicid,
            sr_request.engineer,
            sr_request.requestor_comments,
            sr_request.plan,
            sr_request.existing_validity.strftime('%Y-%m-%d %H:%M:%S') if sr_request.existing_validity else 'N/A',
            sr_request.requestor_validity_start_date.strftime('%Y-%m-%d %H:%M:%S') if sr_request.requestor_validity_start_date else 'N/A',
            sr_request.requestor_validity_end_date.strftime('%Y-%m-%d %H:%M:%S') if sr_request.requestor_validity_end_date else 'N/A',
            sr_request.billing_to,
            sr_request.sim_status_during_request,
            sr_request.remarks,
            sr_request.hod_remarks,
            sr_request.status,
            sr_request.new_sr_no,
            sr_request.sr_date.strftime('%Y-%m-%d %H:%M:%S') if sr_request.sr_date else 'N/A',
            sr_request.sr_success_date.strftime('%Y-%m-%d %H:%M:%S') if sr_request.sr_success_date else 'N/A',
            sr_request.engineer_email,
            sr_request.manager_approval_status,
            sr_request.manager_approval_datetime.strftime('%Y-%m-%d %H:%M:%S') if sr_request.manager_approval_datetime else 'N/A',
        ])

    return response

def new_sr_details_form(request, request_id):
    sr_request = get_object_or_404(SRRequest, id=request_id)

    # Check if the status is 'Closed'
    read_only = sr_request.status == 'Closed'

    if request.method == 'POST' and not read_only:
        form = NewSRDetailsForm(request.POST, instance=sr_request)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'Details submitted successfully!'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = NewSRDetailsForm(instance=sr_request)

    return render(request, 'sr_request/new_sr_details_form.html', {'form': form, 'sr_request': sr_request, 'read_only': read_only})