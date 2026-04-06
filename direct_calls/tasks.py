# direct_calls/tasks.py
from celery import shared_task
import os
from django.conf import settings
from .models import DirectCall
from .generate_device_repair_request_pdf import generate_device_repair_request_pdf
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def generate_fir_pdf_async(self, call_id):
    """Generate FIR PDF asynchronously."""
    try:
        entry = DirectCall.objects.get(id=call_id)
        data = {
            'centralised_id': entry.centralised_id,
            'device_model': entry.device_model,
            # ... rest of data dict ...
        }
        pdf_file_name = f"FIR_{entry.engineer_recommendation}_{entry.unique_id}.pdf"
        pdf_file_path = os.path.join(settings.MEDIA_ROOT, pdf_file_name)
        generate_device_repair_request_pdf(data, pdf_file_path)
        
        # Update entry to mark PDF generated
        entry.pdf_generated = True
        entry.pdf_path = pdf_file_name
        entry.save(update_fields=['pdf_generated', 'pdf_path'])
        logger.info(f"FIR PDF generated successfully for {call_id}")
        return {'success': True, 'file': pdf_file_name}
    except Exception as exc:
        logger.exception(f"Failed to generate PDF for {call_id}")
        raise self.retry(exc=exc, countdown=60)  # Retry after 60s

@shared_task
def send_email_with_attachment_async(call_id, email_type):
    """Send email with PDF attachment asynchronously."""
    try:
        entry = DirectCall.objects.get(id=call_id)
        # Email logic here...
        logger.info(f"Email {email_type} sent for {call_id}")
    except Exception as e:
        logger.exception(f"Failed to send email {email_type} for {call_id}")