from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from .forms import LeaveRequestForm
from .models import LeaveRequest

def leave_request_view(request):
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave_request = form.save()
            # Send email for approval
            subject = "Leave Request Approval Needed"
            email_context = {
                'leave_request': leave_request,
                'approve_url': f"https://danlawtechu.pythonanywhere.com/sat_leave/approve/{leave_request.id}/",
                'reject_url': f"https://danlawtechu.pythonanywhere.com/sat_leave/reject/{leave_request.id}/",
            }
            message = render_to_string('emails/leave_request_email.html', email_context)
            recipient_list = [leave_request.manager, 'sales@danlawtech.com']
            cc_list = [leave_request.engineer] 
            email = EmailMessage(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                recipient_list,
                cc=cc_list
            )
            email.content_subtype = 'html'  # Set the email content type to HTML
            email.send()
 
             
            messages.success(request, 'Your form is submitted! An email has been sent for approval.')
            return redirect('leave_request')  # Redirect to the same page
    else:
        form = LeaveRequestForm()
    return render(request, 'sat_leave_form.html', {'form': form})

def approve_leave_request(request, leave_request_id):
    leave_request = get_object_or_404(LeaveRequest, id=leave_request_id)
    
    # Check if the request has already been processed
    if leave_request.action.strip().lower() != 'pending':
        return render(request, 'sat_leave_action.html', {'leave_request': leave_request, 'action': 'already_processed'})
    
    # Process the approval
    leave_request.approved_by = leave_request.manager
    leave_request.action = 'approved'  # Save the action as 'approved'
    leave_request.save()
    
    # Send email to Engineer about approval
    subject = "Leave Request Approved"
    message = f"Your leave request for {leave_request.date_of_leave} has been approved by {leave_request.manager}."
    recipient_list = [leave_request.engineer]
    cc_list = [leave_request.engineer,leave_request.manager]

    email = EmailMessage(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        recipient_list,
        cc=cc_list
    )
    email.send()    
    # Show success message for approval
    return render(request, 'sat_leave_action.html', {'leave_request': leave_request, 'action': 'approved'})

def reject_leave_request(request, leave_request_id):
    leave_request = get_object_or_404(LeaveRequest, id=leave_request_id)
    
    # Check if the request has already been processed
    if leave_request.action.strip().lower() != 'pending':
        return render(request, 'sat_leave_action.html', {'leave_request': leave_request, 'action': 'already_processed'})
    
    # Process the rejection
    leave_request.approved_by = "Rejected"
    leave_request.action = 'rejected'  # Save the action as 'rejected'
    leave_request.save()
    
    # Send email to Engineer about rejection
    subject = "Leave Request Rejected"
    message = f"Your leave request for {leave_request.date_of_leave} has been rejected by {leave_request.manager}."
    recipient_list = [leave_request.engineer]   
    cc_list = [leave_request.engineer,leave_request.manager]

    email = EmailMessage(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        recipient_list,
        cc=cc_list
    )
    email.send()
    
    # Show success message for rejection
    return render(request, 'sat_leave_action.html', {'leave_request': leave_request, 'action': 'rejected'})
