from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Spacer
from reportlab.lib import colors
from reportlab.lib.units import inch
import pytz
from datetime import datetime

def generate_device_repair_request_pdf(data, file_path):
    doc = SimpleDocTemplate(file_path, pagesize=letter, topMargin=0.5 * inch, bottomMargin=0.5 * inch)
    elements = []

    # Define IST timezone
    ist = pytz.timezone('Asia/Kolkata')

    # Helper function to convert datetime to IST
    def convert_to_ist(dt):
        if isinstance(dt, datetime):  # If it's a datetime object
            return dt.astimezone(ist).strftime('%Y-%m-%d %H:%M:%S')
        return 'N/A'

    # Convert manager and HOD approval datetimes to IST
    manager_approval_datetime = convert_to_ist(data.get('manager_approval_datetime', None))
    hod_approval_datetime = convert_to_ist(data.get('hod_approval_datetime', None))

    # Header
    logo_image_path = "C:\\Users\\Admin\\Downloads\\DANLAW RAW LOGO.jpg"
    logo_image = Image(logo_image_path, 1.5 * inch, 0.5 * inch)  # Adjust size as needed

    header_data = [
        [logo_image, "", "FIR", ""],
        ["Product Code", data.get('device_model', 'N/A'), "Centralised ID", data.get('centralised_id', 'N/A')],
        ["Customer", "A.L", "Format Req. No.", "ASS/011/08/21 Ver-2"],
        ["Document by", "After Sales Support Team", "Date", data.get('engineer_requested_date', 'N/A')]
    ]
    col_widths = [1.5 * inch, 2 * inch, 2 * inch, 2 * inch]  # Consistent column widths
    header_table = Table(header_data, colWidths=col_widths)
    header_table.setStyle(TableStyle([
        ('SPAN', (0, 0), (1, 0)),  # Span the logo across two columns
        ('SPAN', (2, 0), (3, 0)),  # Span the title across two columns
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (2, 0), (3, 0), 'Helvetica-Bold'),  # Bold font for "FIR"
        ('FONTSIZE', (2, 0), (3, 0), 16),  # Increased font size for "FIR"
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),  # Reduced font size
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),  # Reduced padding
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(header_table)

    # Spacer to reduce space between header and table
    elements.append(Spacer(1, 0.1 * inch))

    # Table Header
    table_header = ["SL No.", "Description", "Details"]
    table_data = [table_header]

    # Table Content
    for i, (description, detail) in enumerate(data.get('details', {}).items(), start=1):
        table_data.append([str(i), description, str(detail) if detail is not None else 'N/A'])

    table = Table(table_data, colWidths=[0.5 * inch, 3.5 * inch, 3.5 * inch])  # Consistent column widths
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),  # Reduced font size
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),  # Reduced padding
    ]))
    elements.append(table)

    # Footer
    signature_image_path = "C:\\Users\\Admin\\Downloads\\SR SIGNATURE.png"
    signature_image = Image(signature_image_path, 0.8 * inch, 0.4 * inch)  # Reduced size

    # Extract manager email name
    manager_email = data.get('manager_email', 'N/A')
    manager_email_name = manager_email.split('@')[0] if '@' in manager_email else manager_email

    footer_data = [
        ["Approved By:", "Name", "Date", "Signature"],
        ["Initiated by- Service Eng.", data.get('service_engineer_name', 'N/A'), data.get('engineer_requested_date', 'N/A'), data.get('service_engineer_name', 'N/A')],
        ["Service Manager", 'Kunal', '.','.'],
        ["Sales & Service Head", "Rajendran Subramanian", '.', '.']
    ]
    footer_table = Table(footer_data, colWidths=[2 * inch, 2 * inch, 1.5 * inch, 2 * inch])  # Reduced third column width
    footer_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),  # Reduced font size
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),  # Reduced padding
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(footer_table)

    doc.build(elements)