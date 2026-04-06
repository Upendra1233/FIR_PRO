from django.core.management.base import BaseCommand
from direct_calls.utils import send_direct_call_status_report

class Command(BaseCommand):
    help = 'Send Direct Call Status Auto Report'

    def handle(self, *args, **kwargs):
        send_direct_call_status_report()
        self.stdout.write(self.style.SUCCESS('Report sent!'))