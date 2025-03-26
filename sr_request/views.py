from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from .forms import SRRequestForm, SRDetailsForm
from .models import SRRequest
import logging

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
            subject = f"Approval Needed for SR Request {sr_request.id}"
            recipient_email = settings.HOD_EMAIL  # Manager's email from settings
            cc_emails = [sr_request.engineer_email, 'dilipkumarn@danlawtech.com','sales@danlawtech.com']  # Add CC email addresses
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

    # Send email to engineer with the second form URL
    subject = f"Action Required: Fill Additional Details for SR Request {sr_request.psn}"
    recipient_email = 'dilipkumarn@danlawtech.com' # Engineer's email from the model
    cc_emails = ['dilipkumarn@danlawtech.com',sr_request.engineer_email, 'sales@danlawtech.com']
    context = {
        'sr_request': sr_request,
        'form_url': f"http://127.0.0.1:8000/sr_request/details/{sr_request.id}/",
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
                    subject = f"SR Request {sr_request.id} - Status Closed Notification"
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

    if request.method == 'POST':
        form = SRRequestForm(request.POST, instance=sr_request)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'Form updated successfully!'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = SRRequestForm(instance=sr_request)
    return render(request, 'sr_request/sr_request_form.html', {'form': form, 'sr_request': sr_request, 'edit_mode': True})

def view_request_details(request, request_id):
    sr_request = get_object_or_404(SRRequest, id=request_id)
    return render(request, 'sr_request/view_request_details.html', {'sr_request': sr_request})

def send_manager_email(sr_request):
    subject = f"New SR Request Submitted - Request No: {sr_request.unique_id}"
    recipient_email = settings.HOD_EMAIL  # Manager's email from settings
    cc_emails = [sr_request.engineer_email, 'dilipkumarn@danlawtech.com', 'sales@danlawtech.com']
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