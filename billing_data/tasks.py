from datetime import datetime, timedelta
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from .models import BillingData

from celery import shared_task
from celery.schedules import crontab

@shared_task
def send_yesterdays_invoices():
    yesterday = datetime.now().date() - timedelta(days=1)
    invoices = BillingData.objects.filter(invoice_date=yesterday)

    if not invoices.exists():
        return

    for invoice in invoices:
        html_content = render_to_string('billing_data/mail_invoice_template.html', {
            'invoice': invoice
        })
        subject = f"Invoice {invoice.invoice_no} - {invoice.customer_name}"
        msg = EmailMultiAlternatives(
            subject,
            "Please see the attached invoice.",
            settings.DEFAULT_FROM_EMAIL,
            ['sales@danlawtech.com'],  # Or your recipient list
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()

@shared_task
def send_due_date_reminders():
    today = datetime.now().date()
    threshold_date = today - timedelta(days=7)
    # Filter invoices with payment_status "Pending" and due_date <= threshold_date
    invoices = BillingData.objects.filter(
        payment_status="Pending",
        due_date__lte=threshold_date
    )

    if not invoices.exists():
        return

    for invoice in invoices:
        html_content = render_to_string('billing_data/due_date_reminder_template.html', {
            'invoice': invoice
        })
        subject = f"Payment Due Reminder: Invoice {invoice.invoice_no} - {invoice.customer_name}"
        msg = EmailMultiAlternatives(
            subject,
            "This is a payment due reminder.",
            settings.DEFAULT_FROM_EMAIL,
            ['sales@danlawtech.com'],  # Or use [invoice.customer_email] if you want to send to customer
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()

# Example Celery Beat schedule (usually in celery.py or settings.py)
CELERY_BEAT_SCHEDULE = {
    'send-yesterdays-invoices-every-morning': {
        'task': 'billing_data.tasks.send_yesterdays_invoices',
        'schedule': crontab(hour=17, minute=21),  # 5:21 PM every day
    },
    'send-due-date-reminders-every-morning': {
        'task': 'billing_data.tasks.send_due_date_reminders',
        'schedule': crontab(hour=22, minute=51),  # 10:51 PM every day
    },
}