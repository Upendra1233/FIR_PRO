# filepath: c:\Users\Admin\Desktop\FIR_PRO\mapping_process\management\commands\clean_duplicates.py
from django.core.management.base import BaseCommand
from mapping_process.models import MappingProcess
from django.db.models import Count

class Command(BaseCommand):
    help = 'Clean up duplicate records in the MappingProcess model'

    def handle(self, *args, **kwargs):
        duplicates = MappingProcess.objects.values('ticket_id').annotate(count=Count('id')).filter(count__gt=1)
        for duplicate in duplicates:
            MappingProcess.objects.filter(ticket_id=duplicate['ticket_id'])[1:].delete()  # Keep the first record, delete the rest
        self.stdout.write(self.style.SUCCESS('Duplicate records cleaned up successfully.'))