# direct_calls/management/commands/generate_daily_reports.py
from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.db.models import Count
from direct_calls.models import DirectCall
import csv
import os
from django.conf import settings
from datetime import datetime

class Command(BaseCommand):
    help = 'Pre-generate daily summary reports'

    def handle(self, *args, **kwargs):
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Generate CSV summary
        csv_path = os.path.join(settings.MEDIA_ROOT, f'daily_summary_{today}.csv')
        
        queryset = DirectCall.objects.values('call_status').annotate(count=Count('id'))
        
        with open(csv_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['call_status', 'count'])
            writer.writeheader()
            for row in queryset:
                writer.writerow(row)
        
        # Cache the result
        cache.set(f'daily_report_{today}', csv_path, 86400)  # 24 hours
        
        self.stdout.write(self.style.SUCCESS(f'Report generated: {csv_path}'))