from django.core.management.base import BaseCommand
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from billing_data.models import BillingData
from datetime import datetime, timedelta
import schedule
import time
from collections import defaultdict

def send_yesterdays_shipments():
    print("Running send_yesterdays_shipments")
    yesterday = datetime.now().date() - timedelta(days=2)
    invoices = BillingData.objects.filter(invoice_date=yesterday)
    print(f"Found {invoices.count()} invoices for yesterday")
    for invoice in invoices:
        if invoice.shipment_emails:
            to_emails = [e.strip() for e in invoice.shipment_emails.split(';') if e.strip()]
            cc_emails = ["sales@danlawtech.com"]
            html_content = render_to_string('billing_data/mail_invoice_template.html', {'billing_data': invoice, 'mail_type': 'shipment'})
            subject = f"Shipment Invoice Notification - {invoice.invoice_no}"
            msg = EmailMultiAlternatives(
                subject,
                "Please see the attached invoice.",
                settings.DEFAULT_FROM_EMAIL,
                to_emails,
                cc=cc_emails,
            )
            msg.attach_alternative(html_content, "text/html")
            try:
                msg.send()
                print(f"Sent shipment email for invoice {invoice.invoice_no}")
            except Exception as e:
                print(f"Failed to send shipment email for invoice {invoice.invoice_no}: {e}")

def send_due_date_reminders():
    print("Running send_due_date_reminders")
    today = datetime.now().date()
    next_seven_days = today + timedelta(days=7)
    invoices = BillingData.objects.filter(
        payment_status__iexact="pending",
        due_date__gte=today,
        due_date__lte=next_seven_days
    )
    print(f"Found {invoices.count()} due reminders")

    # Group by (customer_name, location)
    grouped = defaultdict(list)
    email_map = {}
    for invoice in invoices:
        key = (invoice.customer_name, invoice.location)
        grouped[key].append(invoice)
        # Use the first due_emails found for this group
        if key not in email_map and invoice.due_emails:
            email_map[key] = [e.strip() for e in invoice.due_emails.split(';') if e.strip()]

    excluded_customers = {"Ashok Leyland Limited", "Royal Enfield"}

    for key, invoice_list in grouped.items():
        customer_name = key[0]
        if customer_name in excluded_customers:
            print(f"Skipping due date reminder for excluded customer: {customer_name}")
            continue
        to_emails = email_map.get(key)
        if not to_emails:
            continue
        cc_emails = ["sales@danlawtech.com"]
        # Pass the list of invoices to the template
        html_content = render_to_string(
            'billing_data/due_date_reminder_template.html',
            {
                'invoice_list': invoice_list,
                'mail_type': 'due',
                'customer_name': key[0],
                'location': key[1],
            }
        )
        subject = f"Payment Due Reminder: {key[0]} - {key[1]}"
        msg = EmailMultiAlternatives(
            subject,
            "This is a payment due reminder.",
            settings.DEFAULT_FROM_EMAIL,
            to_emails,
            cc=cc_emails,
        )
        msg.attach_alternative(html_content, "text/html")
        try:
            msg.send()
            print(f"Sent due date reminder for {key[0]} - {key[1]}")
        except Exception as e:
            print(f"Failed to send due date reminder for {key[0]} - {key[1]}: {e}")
class Command(BaseCommand):
    help = 'Send scheduled emails for shipments and due date reminders'

    def handle(self, *args, **kwargs):
        send_yesterdays_shipments()
        send_due_date_reminders()
        self.stdout.write(self.style.SUCCESS('Scheduled emails sent.'))
