from django.core.management.base import BaseCommand
from direct_calls.models import DirectCall
from django.db import models

class Command(BaseCommand):
    help = "Update clean_call_status for all DirectCall records"

    def handle(self, *args, **kwargs):
        # Update clean_call_status for records with call_status 'FIR' or 'FIR-Resolved'
        DirectCall.objects.filter(call_status__in=['FIR', 'FIR-Resolved']).update(clean_call_status='Resolved')

        # For other records, set clean_call_status to the same value as call_status
        DirectCall.objects.exclude(call_status__in=['FIR', 'FIR-Resolved']).update(clean_call_status=models.F('call_status'))

        self.stdout.write(self.style.SUCCESS("Successfully updated clean_call_status for all records."))