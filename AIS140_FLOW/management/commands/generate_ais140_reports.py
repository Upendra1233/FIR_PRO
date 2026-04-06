import os
import logging
from datetime import datetime, timedelta, time
from django.core.management.base import BaseCommand

from django.utils.timezone import now, make_naive, make_aware
from django.db.models import Q
from AIS140_FLOW.models import AIS140Request
from openpyxl import Workbook
from psn_project.email_utils import send_email_with_config

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Generate AIS140 comprehensive reports and email them'

    def add_arguments(self, parser):
        parser.add_argument('--output_dir', type=str, default='media/reports/', help='Output directory')

    def handle(self, *args, **options):
        output_dir = options['output_dir']

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        try:
            # Generate Excel file
            filepath = self.generate_comprehensive_excel(output_dir)
            self.stdout.write(self.style.SUCCESS(f'Report generated: {filepath}'))
            
            # Send email
            self.send_email_report(filepath)
            
        except Exception as e:
            logger.exception("Error in AIS140 report generation")
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))

    def generate_comprehensive_excel(self, output_dir):
        """Generate comprehensive report with Report and Data sheets"""
        
        # Get yesterday's date
        yesterday = (now() - timedelta(days=1)).date()
        logger.info(f"Starting AIS140 report generation for date {yesterday}")
        
        # Create timezone-aware datetime boundaries for yesterday
        yesterday_start = make_aware(datetime.combine(yesterday, time.min))
        yesterday_end = make_aware(datetime.combine(yesterday, time.max))
        logger.info(f"Date range: {yesterday_start} to {yesterday_end}")
        start = datetime.combine(yesterday, datetime.min.time())
        end = start + timedelta(days=1)        
        # Get all states
        states = AIS140Request.objects.filter(
            state__isnull=False
        ).exclude(state='').values_list('state', flat=True).distinct().order_by('state')
        
        report_data = []
        
        for state in states:
            try:
                state_records = AIS140Request.objects.filter(state=state)
                
                row = {
                    'state': state,

                    'new_requests': state_records.filter(
                        date_of_request__gte=start,
                        date_of_request__lt=end
                    ).count(),
                    'pending': state_records.filter(date_of_request__date__lt=yesterday, completion_status='Pending').count(),
                    'temp_cert_done': state_records.filter(completion_status='Temporary').count(),
                    'third_party': state_records.filter(Q(d1__contains='D1-Third Party Device'), completion_status='Pending').count(),
                    'sim_exp': state_records.filter(Q(d1__contains='D1-SIM Expired'), completion_status='Pending').count(),
                    'wrong_contact': state_records.filter(Q(d1__contains='D1-Contact Detail Wrong'), completion_status='Pending').count(),
                    'customer_not_answering': state_records.filter(Q(d1__contains='D1-Customer not Answering'), completion_status='Pending').count(),                    
                    'top_up_req': state_records.filter(Q(d1__contains='D1-Top Up to be Done'), completion_status='Pending').count(),
                    'sos_not_fitted': state_records.filter(Q(d1__contains='D1-SOS Switch not fitted'), completion_status='Pending').count(),
                    'sos_not_working': state_records.filter(Q(d1__contains='D1-SOS not working'), completion_status='Pending').count(),

                    'body_building': state_records.filter(d1__contains='D1-Body Building', completion_status='Pending').count(),
                    'veh_in_body_building': state_records.filter(Q(d1__contains='D1-Vehicle in Body Building'), completion_status='Pending').count(),
                    'device_not_powering': state_records.filter(Q(d1__contains='D1-Device Getting Not Powering ON'), completion_status='Pending').count(),
                    'device_not_working': state_records.filter(Q(d1__contains='D1-Device not working'), completion_status='Pending').count(),
                    'no_driver_support': state_records.filter(Q(d1__contains='D1-No Driver Support'), completion_status='Pending').count(),

                }
                row['total'] = row['new_requests'] + row['pending']
                row['al_total'] = row.get('third_party', 0) + row.get('sim_exp', 0) + row.get('top_up_req', 0) + row.get('wrong_contact', 0) + row.get('customer_not_answering', 0)
                row['c_total'] = (row.get('sos_not_fitted', 0) + row.get('sos_not_working', 0) + row.get('body_building', 0)
                                + row.get('device_not_powering', 0) + row.get('no_driver_support', 0) + row.get('veh_in_body_building', 0))
                row['d_total'] = row.get('total', 0) - row.get('temp_cert_done', 0) - row.get('al_total', 0) - row.get('c_total', 0)

                report_data.append(row)
                logger.info(f"Processed state: {state} - {row['total']} total requests")
            except Exception:
                logger.exception(f"Error processing state: {state}")
                continue
        
        # Calculate grand totals
        grand_totals = {
            'state': 'Grand Total',
            'new_requests': sum(r.get('new_requests', 0) for r in report_data),
            'pending': sum(r.get('pending', 0) for r in report_data),
            'total': sum(r.get('total', 0) for r in report_data),
            'temp_cert_done': sum(r.get('temp_cert_done', 0) for r in report_data),
            'third_party': sum(r.get('third_party', 0) for r in report_data),
            'sim_exp': sum(r.get('sim_exp', 0) for r in report_data),
            'wrong_contact': sum(r.get('wrong_contact', 0) for r in report_data),
            'customer_not_answering': sum(r.get('customer_not_answering', 0) for r in report_data),
            'top_up_req': sum(r.get('top_up_req', 0) for r in report_data),
            'sos_not_fitted': sum(r.get('sos_not_fitted', 0) for r in report_data),
            'sos_not_working': sum(r.get('sos_not_working', 0) for r in report_data),

            'no_driver_support': sum(r.get('no_driver_support', 0) for r in report_data),

            'al_total': sum(r.get('al_total', 0) for r in report_data),
            'c_total': sum(r.get('c_total', 0) for r in report_data),
            'd_total': sum(r.get('d_total', 0) for r in report_data),
        }
        
        # Create workbook with Report and Data sheets
        wb = Workbook()
        ws_report = wb.active
        ws_report.title = "Report"
        
        # Write headers
        headers = [
            'State', 'New Requests', 'Old Pending', 'Total', 'Temp Cert Done',
            'Third Party', 'SIM Exp', 'Wrong Contact', 'Customer Not Answering',
            'Top Up Req', 'AL Total', 'SOS Not Fitted', 'SOS Not Working',
            'Body Building', 'No Driver Support', 'C Total', 'D Total'
        ]
        
        ws_report.append(headers)
        
        # Write data
        for row in report_data:
            ws_report.append([
                row.get('state'), row.get('new_requests'), row.get('pending'),
                row.get('total'), row.get('temp_cert_done'),
                row.get('third_party'), row.get('sim_exp'), row.get('wrong_contact'),
                row.get('customer_not_answering'), row.get('top_up_req'), row.get('al_total'),
                row.get('sos_not_fitted'), row.get('sos_not_working'),
                row.get('body_building'), row.get('no_driver_support'),
                row.get('c_total'), row.get('d_total')
            ])
        
        # Write grand totals
        ws_report.append([
            grand_totals.get('state'), grand_totals.get('new_requests'),
            grand_totals.get('pending'), grand_totals.get('total'),
            grand_totals.get('temp_cert_done'), grand_totals.get('third_party'),
            grand_totals.get('sim_exp'), grand_totals.get('wrong_contact'),
            grand_totals.get('customer_not_answering'), grand_totals.get('top_up_req'),
            grand_totals.get('al_total'), grand_totals.get('sos_not_fitted'),
            grand_totals.get('sos_not_working'), grand_totals.get('body_building'),
            grand_totals.get('no_driver_support'), grand_totals.get('c_total'), grand_totals.get('d_total')
        ])
        
        # Create Data sheet
        ws_data = wb.create_sheet("Data")
        all_records = AIS140Request.objects.all()
        data_headers = ['Unique ID', 'Date of Request', 'State', 'Chassis No', 'Engine No', 
                       'PSN No', 'Vehicle No', 'Customer Name', 'D1 Remarks', 'D2 Remarks', 
                       'Completion Status', 'Completion Date']
        ws_data.append(data_headers)
        
        for record in all_records:
            try:
                date_of_request = make_naive(record.date_of_request) if record.date_of_request else None
                completion_date = make_naive(record.completion_date) if record.completion_date else None
                
                ws_data.append([
                    record.unique_id, 
                    date_of_request, 
                    record.state, 
                    record.vin_no,
                    record.engine, 
                    record.psn, 
                    record.vehicle_no, 
                    record.customer_name,
                    record.d1, 
                    record.d2, 
                    record.completion_status, 
                    completion_date
                ])
            except Exception:
                identifier = getattr(record, 'unique_id', getattr(record, 'id', 'unknown'))
                logger.exception(f"Error processing record {identifier}")
                continue
        
        # Save file
        filename = f"AIS140_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        filepath = os.path.join(output_dir, filename)
        try:
            wb.save(filepath)
        except Exception:
            logger.exception(f"Failed to save Excel report to {filepath}")
            raise
        
        logger.info(f"AIS140 report saved to {filepath}")
        return filepath

    def send_email_report(self, filepath):
        """Send the Excel report via email using a verified sender"""
        subject = f"AIS140 Daily Report - {datetime.now().strftime('%Y-%m-%d')}"
        plain_message = "Please find attached the AIS140 comprehensive report with daily metrics."
        html_message = f"<p>{plain_message}</p><p>Attached: {os.path.basename(filepath)}</p>"

        recipient_list = ["upendram@danlawtech.com"]
        cc_list = ['sales@danlawtech.com', 'dilipkumarn@danlawtech.com', 'narendrareddyg@danlawtech.com', 'rajendran@danlawtech.com']

        # Use the helper which accepts attachments
        success = send_email_with_config(
            subject=subject,
            html_message=html_message,
            recipient_list=recipient_list,
            cc_list=cc_list,
            attachments=[filepath],
            config_type='AIS140'
        )

        if success:
            self.stdout.write(self.style.SUCCESS('Email sent successfully'))
            logger.info(f'AIS140 Report email sent to {recipient_list}')
        else:
            self.stdout.write(self.style.ERROR('Error sending email'))
            logger.error('Error sending AIS140 report email')
            raise Exception('Failed to send AIS140 report email')