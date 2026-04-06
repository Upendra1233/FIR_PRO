from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Spacer
from reportlab.lib import colors
from reportlab.lib.units import inch
import pytz
from datetime import datetime
from django.conf import settings  # Import settings to access STATICFILES_DIRS or STATIC_ROOT
from django.templatetags.static import static  # Import static to resolve static file paths

def wrap_text(text, line_length=30):
    """
    Wraps the given text to the specified line length.
    Inserts a newline character after every `line_length` characters.
    """
    if not text:
        return ""
    return '\n'.join([text[i:i+line_length] for i in range(0, len(text), line_length)])

def generate_device_repair_request_pdf(data, file_path, date_of_closure=None):
    doc = SimpleDocTemplate(file_path, pagesize=letter, topMargin=0.5 * inch, bottomMargin=0.5 * inch)
    elements = []

    # Header
    logo_image_path = "C:\\Users\\Admin\\Downloads\\DANLAW RAW LOGO.jpg"
    logo_image = Image(logo_image_path, 1.5 * inch, 0.5 * inch)

    header_data = [
        [logo_image, "", data.get('centralised_id', 'N/A'), ""],
        ["Product Code", data.get('device_model', 'N/A'), "Centralised ID", data.get('unique_id', 'N/A')],
        ["Customer", "A.L", "Format Req. No.", "ASS/011/08/21 Ver-2"],
        ["Document by", "After Sales Support Team", "Date", data.get('engineer_requested_date', 'N/A')]
    ]
    col_widths = [1.5 * inch, 2 * inch, 2 * inch, 2 * inch]
    header_table = Table(header_data, colWidths=col_widths)
    header_table.setStyle(TableStyle([
        ('SPAN', (0, 0), (1, 0)),
        ('SPAN', (2, 0), (3, 0)),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (2, 0), (3, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (2, 0), (3, 0), 16),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 0.2 * inch))

    # Table Content
    table_header = ["SL No.", "Description", "Details"]
    table_data = [table_header]
    for i, (description, detail) in enumerate(data.get('details', {}).items(), start=1):
        # Wrap the text for the "Details" column
        wrapped_detail = wrap_text(str(detail) if detail is not None else 'N/A')
        table_data.append([str(i), description, wrapped_detail])

    table = Table(table_data, colWidths=[0.5 * inch, 3.5 * inch, 3.5 * inch])
    table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ]))
    elements.append(table)
 
    # Footer
    # Handle date_of_closure separately
    if isinstance(date_of_closure, datetime):  # Format if it's a datetime object
        date_of_closure = date_of_closure.strftime('%d-%m-%Y')
    elif not date_of_closure:  # Default to 'N/A' if not provided
        date_of_closure = 'N/A'

    footer_data = [           
        ["Approved By:", "Name", "Date", "Signature"],
        ["Service Engineer", data.get('service_engineer_name', 'N/A'), data.get('engineer_requested_date', 'N/A'), data.get('service_engineer_name', 'N/A')],
        ["Manager", "Kunal" if data.get('call_type', '') == "Direct Call" else "Narendra Reddy", "N/A", "Kunal" if data.get('call_type', '') == "Direct Call" else "Narendra Reddy"],
        ["Sales & Service Head", "Rajendran Subramanian", data.get('date_of_closure', 'N/A'), ""]
    ]
    footer_table = Table(footer_data, colWidths=[2 * inch, 2 * inch, 1.5 * inch, 2 * inch])
    footer_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(footer_table)

    doc.build(elements)