from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.timezone import now
from .forms import MappingProcessForm
from .models import MappingProcess  # Import the MappingProcess model

def mapping_process_form(request):
    if request.method == 'POST':
        post_data = request.POST.copy()
        print("POST data:", post_data)  # Log the POST data

        # Replace "Others" values with the custom input
        if post_data.get('old_device_telco_status') == 'Others':
            post_data['old_device_telco_status'] = post_data.get('old_device_telco_status_other', '').strip()
        if post_data.get('new_device_telco_status') == 'Others':
            post_data['new_device_telco_status'] = post_data.get('new_device_telco_status_other', '').strip()
        if post_data.get('old_device_return_location') == 'Others':
            post_data['old_device_return_location'] = post_data.get('old_device_return_location_other', '').strip()
        if post_data.get('req_raised_by') == 'Others':
            post_data['req_raised_by'] = post_data.get('req_raised_by_other', '').strip()
        if post_data.get('current_card_status_of_new_device') == 'Others':
            post_data['current_card_status_of_new_device'] = post_data.get('current_card_status_of_new_device_other', '').strip()
        if post_data.get('activation_status_of_new_device') == 'Others':
            post_data['activation_status_of_new_device'] = post_data.get('activation_status_of_new_device_other', '').strip()

        form = MappingProcessForm(post_data)
        if form.is_valid():
            instance = form.save()  # Save the form data to the database
            print("Data saved successfully:", instance)

            # Prepare email data
            subject = f"New Mapping Process Submitted - {instance.old_psn} to {instance.new_psn}"
            manager_email = ["settings.HOD_EMAIL","sales@danlawtech.com"]  # Replace with the manager's email
            approve_url = f"http://127.0.0.1:8000/mapping_process/approve/{instance.id}/"  # Replace with your approve URL
            reject_url = f"http://127.0.0.1:8000/mapping_process/reject/{instance.id}/"  # Replace with your reject URL

            # Render the email template
            email_body = render_to_string('mapping_process/email_template.html', {
                'entry': instance,
                'approve_url': approve_url,
                'reject_url': reject_url,
            })

            # Send the email
            email = EmailMessage(subject, email_body, to=["settings.HOD_EMAIL"],cc=["narendrareddyg@danlawtech.com","kunal@danlawtech.com"])
            email.content_subtype = 'html'  # Set the email content type to HTML
            email.send()

            return JsonResponse({'success': True})
        else:
            print("Form errors:", form.errors)  # Log form errors
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = MappingProcessForm()
    return render(request, 'mapping_process/mapping_process_form.html', {'form': form})

def approve_request(request, request_id):
    # Approve the request
    instance = get_object_or_404(MappingProcess, id=request_id)
    instance.manager_approval_status = 'Approved'
    instance.manager_approval_time = now()  # Set the current time
    instance.save()  # Save the changes
    return HttpResponse(f"Request {request_id} has been approved.")

def reject_request(request, request_id):
    # Reject the request
    instance = get_object_or_404(MappingProcess, id=request_id)
    instance.manager_approval_status = 'Rejected'
    instance.manager_approval_time = now()  # Set the current time
    instance.save()  # Save the changes
    return HttpResponse(f"Request {request_id} has been rejected.")
