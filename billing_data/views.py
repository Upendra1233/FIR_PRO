from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from urllib3 import request
from .forms import BillingDataForm
from .models import BillingData
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Sum, F, Q
from django.db.models.functions import Lower, Trim
from datetime import timedelta, date
import csv
from datetime import datetime
import pandas as pd

def add_billing_data(request):
    if request.method == 'POST':
        form = BillingDataForm(request.POST)
        if form.is_valid():
            billing_data = form.save(commit=False)
            # Logic to calculate Theoretical Payment Due Date
            invoice_date = billing_data.invoice_date
            location = billing_data.location

            if invoice_date and location:
                if location == 'ALCOB':
                    billing_data.theoretical_payment_due_date = invoice_date + timedelta(days=18)
                elif location in ['Chennai', 'Ennore', 'Hosur', 'VVC']:
                    billing_data.theoretical_payment_due_date = invoice_date + timedelta(days=52)
                elif location in ['PantNagar', 'Alwar']:
                    billing_data.theoretical_payment_due_date = invoice_date + timedelta(days=55)

            billing_data.save()
            return render(request, 'billing_data/invoice_temp.html', {
                'form': BillingDataForm(),  # reset form
                'form_submitted': True
            })
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BillingDataForm()
    return render(request, 'billing_data/invoice_temp.html', {'form': form})

def bill_real_time_data(request):
    """
    Render the real-time billing data page.
    """
    return render(request, 'billing_data/bill_real_time_data.html')

def fetch_billing_data(request):
    """
    Fetch filtered billing data for the real-time table.
    """
    # Get filter parameters from the request
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    invoice_no = request.GET.get('invoice_no')
    customer_name = request.GET.get('customer_name')
    location = request.GET.get('location')
    part_sub_category = request.GET.get('part_sub_category')   # New filter
    payment_status = request.GET.get('payment_status')         # New filter
    due_date_from = request.GET.get('due_date_from')
    due_date_to = request.GET.get('due_date_to')
    received_date_from = request.GET.get('received_date_from')
    received_date_to = request.GET.get('received_date_to')
    product = request.GET.get('product')
    item_sub_category = request.GET.get('item_sub_category')
    part_no = request.GET.get('part_no')
    grn_no = request.GET.get('grn_no', '').strip()  # <-- Add this line
    due_date_range = request.GET.get('due_date_range')
    today = date.today()
    additional_fields = request.GET.getlist('fields[]')  # Get additional fields as a list
    page = int(request.GET.get('page', 1))
    # Filter the queryset based on the provided filters
    queryset = BillingData.objects.all()
    if from_date:
        queryset = queryset.filter(invoice_date__gte=from_date)
    if to_date:
        queryset = queryset.filter(invoice_date__lte=to_date)
    if invoice_no:
        queryset = queryset.filter(invoice_no__icontains=invoice_no)
    if customer_name and customer_name != 'All':
        queryset = queryset.filter(customer_name__icontains=customer_name)
    if location and location != 'All':
        queryset = queryset.filter(location__icontains=location)
    if part_sub_category and part_sub_category != 'All':   # Apply part_sub_category filter
        queryset = queryset.filter(part_sub_category__icontains=part_sub_category)
    if payment_status and payment_status != 'All':         # Apply payment_status filter
        queryset = queryset.filter(payment_status=payment_status)
    if due_date_from:
        queryset = queryset.filter(due_date__gte=due_date_from)
    if due_date_to:
        queryset = queryset.filter(due_date__lte=due_date_to)
    if received_date_from:
        queryset = queryset.filter(received_date__gte=received_date_from)
    if received_date_to:
        queryset = queryset.filter(received_date__lte=received_date_to)
    if product and product != 'All':
        queryset = queryset.filter(product__icontains=product)
    if item_sub_category and item_sub_category != 'All':
        queryset = queryset.filter(item_sub_category__icontains=item_sub_category)
    if part_no and part_no != 'All':
        queryset = queryset.filter(part_no__icontains=part_no)

    gap_filter = request.GET.get('gap_filter')

    if gap_filter and gap_filter != 'All':
        if gap_filter == 'gt0':
            queryset = queryset.filter(gap__gt=0)
        elif gap_filter == 'eq0':
            queryset = queryset.filter(gap=0)
        elif gap_filter == 'lt0':
            queryset = queryset.filter(gap__lt=0)

    grn_date_filter = request.GET.get('grn_date_filter')  # <-- Add this line
    if due_date_range:
        if due_date_range == 'overdue_7':
            queryset = queryset.filter(
                due_date__lt=today - timedelta(days=7),
                payment_status__iexact='Pending'
            )
        elif due_date_range == 'overdue_15':
            queryset = queryset.filter(
                due_date__lt=today - timedelta(days=15),
                payment_status__iexact='Pending'
            )
        elif due_date_range == 'overdue_30':
            queryset = queryset.filter(
                due_date__lt=today - timedelta(days=30),
                payment_status__iexact='Pending'
            )
        elif due_date_range == 'due_7':
            queryset = queryset.filter(
                due_date__gte=today,
                due_date__lte=today + timedelta(days=7),
                payment_status__iexact='Pending'
            )
        elif due_date_range == 'due_15':
            queryset = queryset.filter(
                due_date__gte=today,
                due_date__lte=today + timedelta(days=15),
                payment_status__iexact='Pending'
            )
        elif due_date_range == 'due_30':
            queryset = queryset.filter(
                due_date__gte=today,
                due_date__lte=today + timedelta(days=30),
                payment_status__iexact='Pending'
            )
        elif due_date_range == 'due_60':
            queryset = queryset.filter(
                due_date__gte=today,
                due_date__lte=today + timedelta(days=60),
                payment_status__iexact='Pending'
            )
    # Add GRN Date filter logic
    if grn_date_filter:
        if grn_date_filter == 'blank':
            queryset = queryset.filter(actual_grn_delivery_date__isnull=True)
        elif grn_date_filter == 'non_blank':
            queryset = queryset.filter(actual_grn_delivery_date__isnull=False)
    if grn_no:
        queryset = queryset.filter(grn_no__icontains=grn_no)  # <-- Add this block

    # Order by latest invoice_date first
    queryset = queryset.order_by('-invoice_date')

    # Paginate the results
    paginator = Paginator(queryset, 25)
    page_obj = paginator.get_page(page)

    # Prepare data for charts
    customer_chart = (
        queryset
        .values('customer_name')
        .annotate(total_value=Sum('total_invoice_value_with_gst'))
        .order_by('customer_name')
    )
    quantity_chart = (
        queryset
        .values('customer_name')
        .annotate(total_value=Sum('qty'))
        .order_by('customer_name')
    )
    product_chart = (
        queryset
        .values('product')
        .annotate(total_value=Sum('total_invoice_value_with_gst'))
        .order_by('product')
    )

    # Calculate total invoice value with GST
    total_invoice_value = queryset.aggregate(total=Sum('total_invoice_value_with_gst'))['total'] or 0
    total_qty = queryset.aggregate(total=Sum('qty'))['total'] or 0  # <-- Add this line
    # Prepare the data for the response
    data = []
    for record in page_obj.object_list:
        row = {
            'id': record.id,  # <-- Add this line
            'unique_id': record.unique_id,  # Unique ID field
            'invoice_no': record.invoice_no,
            'invoice_date': record.invoice_date,
            'part_no': record.part_no,
            'qty': record.qty,
            'customer_name': record.customer_name,
            'location': record.location,
            'part_sub_category': record.part_sub_category,
            'product': record.product,
            'invoice_value_without_gst': record.invoice_value_without_gst,
            'invoice_value_with_gst': record.total_invoice_value_with_gst,
            'credited_amount': record.credited_amount,
            'tds_amount': record.tds_amount,
            'gap': record.gap,
            'theoretical_payment_due_date': record.theoretical_payment_due_date,
            'due_date': record.due_date,
            'payment_status': record.payment_status,
            'received_date': record.received_date,
            'actual_grn_delivery_date': record.actual_grn_delivery_date,
            'grn_no': record.grn_no,
        }
        # Add additional fields dynamically
        for field in additional_fields:
            row[field] = getattr(record, field, '')
        data.append(row)
    response = {
        'data': data,
        'charts': {
            'customer': list(customer_chart),
            'quantity': list(quantity_chart),
            'product': list(product_chart),
        },
        "current_page": page_obj.number,
        "total_pages": paginator.num_pages,
        "has_previous": page_obj.has_previous(),
        "has_next": page_obj.has_next(),
        "total_count": paginator.count,
        "total_invoice_value_with_gst": total_invoice_value,
        "total_qty": total_qty,  # <-- Add this line
    }
    return JsonResponse(response)
def get_unique_field_values(request):
    """
    Fetch unique values for filters like customer name, location, part_sub_category, and payment_status.
    """
    customer_names = BillingData.objects.values_list('customer_name', flat=True).distinct()
    locations = BillingData.objects.values_list('location', flat=True).distinct()
    part_sub_categories = BillingData.objects.values_list('part_sub_category', flat=True).distinct()
    payment_statuses = BillingData.objects.values_list('payment_status', flat=True).distinct()
    products = BillingData.objects.values_list('product', flat=True).distinct()
    item_sub_categories = BillingData.objects.values_list('item_sub_category', flat=True).distinct()
    part_nos = BillingData.objects.values_list('part_no', flat=True).distinct()
    return JsonResponse({
        'customer_names': list(customer_names),
        'locations': list(locations),
        'part_sub_categories': list(part_sub_categories),
        'payment_statuses': list(payment_statuses),
        'products': list(products),
        'item_sub_categories': list(item_sub_categories),
        'part_nos': list(part_nos),
    })
def download_invoice_csv(request):
    invoices = BillingData.objects.all().order_by('-id')
    if not invoices.exists():
        return HttpResponse("No invoice data available.", content_type="text/plain")
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'Billing_data_{timestamp}.csv'
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)
    writer.writerow([
        "Customer's Name",
        "Location",
        "Part No.",
        "Quantity",
        "Invoice No.",
        "Invoice Date",
        "Product",
        "Category",
        "Part Sub Category",
        "Item Sub Category",
        "Docket No.",
        "Date of Shipment",
        "Transporter Name",
        "Theoretical Payment Due Date",
        "GRN No.",
        "Actual GRN/Delivery Date",
        "Due Date",
        "Total Invoice Value with GST",
        "Invoice Value without GST",
        "Credited Amount",
        "TDS Amount",
        "GAP",
        "Received Date",
        "Payment Status"
    ])
    # Write data rows
    for invoice in invoices:
        writer.writerow([
            invoice.customer_name,
            invoice.location,
            invoice.part_no,
            invoice.qty,
            invoice.invoice_no,
            invoice.invoice_date,
            invoice.product,
            invoice.category,
            invoice.part_sub_category,
            invoice.item_sub_category,
            invoice.docket_no,
            invoice.date_of_shipment,
            invoice.transporter_name,
            invoice.theoretical_payment_due_date,
            invoice.grn_no,
            invoice.actual_grn_delivery_date,
            invoice.due_date,
            invoice.total_invoice_value_with_gst,
            invoice.invoice_value_without_gst,
            invoice.credited_amount,
            invoice.tds_amount,
            invoice.gap,
            invoice.received_date,
            invoice.payment_status,
        ])
    return response
def download_billing_data_csv(request):
    # Get filter parameters from the request (same as fetch_billing_data)
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    invoice_no = request.GET.get('invoice_no')
    customer_name = request.GET.get('customer_name')
    location = request.GET.get('location')
    part_sub_category = request.GET.get('part_sub_category')
    payment_status = request.GET.get('payment_status')
    due_date_from = request.GET.get('due_date_from')
    due_date_to = request.GET.get('due_date_to')
    received_date_from = request.GET.get('received_date_from')
    received_date_to = request.GET.get('received_date_to')
    product = request.GET.get('product')
    item_sub_category = request.GET.get('item_sub_category')
    part_no = request.GET.get('part_no')
    gap_filter = request.GET.get('gap_filter')
    grn_date_filter = request.GET.get('grn_date_filter')
    grn_no = request.GET.get('grn_no', '').strip()
    queryset = BillingData.objects.all()

    if from_date:
        queryset = queryset.filter(invoice_date__gte=from_date)
    if to_date:
        queryset = queryset.filter(invoice_date__lte=to_date)
    if invoice_no:
        queryset = queryset.filter(invoice_no__icontains=invoice_no)
    if grn_no:
        queryset = queryset.filter(grn_no__icontains=grn_no)
    if customer_name and customer_name != 'All':
        queryset = queryset.filter(customer_name__icontains=customer_name)
    if location and location != 'All':
        queryset = queryset.filter(location__icontains=location)
    if part_sub_category and part_sub_category != 'All':
        queryset = queryset.filter(part_sub_category__icontains=part_sub_category)
    if payment_status and payment_status != 'All':
        queryset = queryset.filter(payment_status=payment_status)
    if due_date_from:
        queryset = queryset.filter(due_date__gte=due_date_from)
    if due_date_to:
        queryset = queryset.filter(due_date__lte=due_date_to)
    if received_date_from:
        queryset = queryset.filter(received_date__gte=received_date_from)
    if received_date_to:
        queryset = queryset.filter(received_date__lte=received_date_to)
    if product and product != 'All':
        queryset = queryset.filter(product__icontains=product)
    if item_sub_category and item_sub_category != 'All':
        queryset = queryset.filter(item_sub_category__icontains=item_sub_category)
    if part_no and part_no != 'All':
        queryset = queryset.filter(part_no__icontains=part_no)
    if gap_filter and gap_filter != 'All':
        if gap_filter == 'gt0':
            queryset = queryset.filter(gap__gt=0)
        elif gap_filter == 'eq0':
            queryset = queryset.filter(gap=0)
        elif gap_filter == 'lt0':
            queryset = queryset.filter(gap__lt=0)
    if grn_date_filter:
        if grn_date_filter == 'blank':
            queryset = queryset.filter(actual_grn_delivery_date__isnull=True)
        elif grn_date_filter == 'non_blank':
            queryset = queryset.filter(actual_grn_delivery_date__isnull=False)

    queryset = queryset.order_by('-invoice_date')

    # Get additional fields from GET
    additional_fields = request.GET.getlist('fields[]') or request.GET.getlist('fields')

    # Define base fields and headers
    base_fields = [
        ('unique_id', 'Unique ID'),
        ('invoice_no', 'Invoice No'),
        ('invoice_date', 'Invoice Date'),
        ('part_no', 'Part No'),
        ('qty', 'Qty'),
        ('customer_name', 'Customer Name'),
        ('location', 'Location'),
        ('part_sub_category', 'Part Sub Category'),
        ('product', 'Product'),
        ('total_invoice_value_with_gst', 'Value With GST'),
        ('credited_amount', 'Credited Val'),
        ('tds_amount', 'TDS Val'),
        ('gap', 'GAP'),
        ('due_date', 'Due Date'),
        ('payment_status', 'Payment Status'),
        ('received_date', 'Received Date'),
        ('actual_grn_delivery_date', 'GRN Date'),
        ('grn_no', 'GRN No'),
    ]

    # Add additional fields to header
    for field in additional_fields:
        # Use a readable header
        header = field.replace('_', ' ').title()
        base_fields.append((field, header))

    # Prepare CSV
    now = datetime.now()
    filename = now.strftime("Billing_data_%d_%m_%Y_%H_%M.csv")
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)

    # Write header
    writer.writerow([header for _, header in base_fields])

    # Write data
    for record in queryset:
        row = []
        for field, _ in base_fields:
            row.append(getattr(record, field, ''))
        writer.writerow(row)
    return response

def add_billing_data_detail(request, pk):
    billing_data = get_object_or_404(BillingData, pk=pk)
    if request.method == 'POST':
        form = BillingDataForm(request.POST, instance=billing_data)
        if form.is_valid():
            form.save()
            messages.success(request, 'Billing data updated successfully!')
            return redirect('add_billing_data_detail', pk=pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BillingDataForm(instance=billing_data)
    return render(request, 'billing_data/invoice_temp.html', {'form': form, 'billing_data': billing_data})

def download_csv(request):
    # Collect all filter parameters as in fetch_billing_data
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    invoice_no = request.GET.get('invoice_no')
    customer_name = request.GET.get('customer_name')
    location = request.GET.get('location')
    part_sub_category = request.GET.get('part_sub_category')
    payment_status = request.GET.get('payment_status')
    due_date_from = request.GET.get('due_date_from')
    due_date_to = request.GET.get('due_date_to')
    received_date_from = request.GET.get('received_date_from')
    received_date_to = request.GET.get('received_date_to')
    product = request.GET.get('product')
    item_sub_category = request.GET.get('item_sub_category')
    part_no = request.GET.get('part_no')
    gap_filter = request.GET.get('gap_filter')
    grn_date_filter = request.GET.get('grn_date_filter')
    grn_no = request.GET.get('grn_no', '').strip()
    additional_fields = request.GET.getlist('fields[]') or request.GET.getlist('fields')

    queryset = BillingData.objects.all()
    if from_date:
        queryset = queryset.filter(invoice_date__gte=from_date)
    if to_date:
        queryset = queryset.filter(invoice_date__lte=to_date)
    if invoice_no:
        queryset = queryset.filter(invoice_no__icontains=invoice_no)
    if grn_no:
        queryset = queryset.filter(grn_no__icontains=grn_no)
    if customer_name and customer_name not in ['', 'All']:
        queryset = queryset.filter(customer_name__icontains=customer_name)
    if location and location not in ['', 'All']:
        queryset = queryset.filter(location__icontains=location)
    if part_sub_category and part_sub_category not in ['', 'All']:
        queryset = queryset.filter(part_sub_category__icontains=part_sub_category)
    if payment_status and payment_status not in ['', 'All']:
        queryset = queryset.filter(payment_status=payment_status)
    if due_date_from:
        queryset = queryset.filter(due_date__gte=due_date_from)
    if due_date_to:
        queryset = queryset.filter(due_date__lte=due_date_to)
    if received_date_from:
        queryset = queryset.filter(received_date__gte=received_date_from)
    if received_date_to:
        queryset = queryset.filter(received_date__lte=received_date_to)
    if product and product not in ['', 'All']:
        queryset = queryset.filter(product__icontains=product)
    if item_sub_category and item_sub_category not in ['', 'All']:
        queryset = queryset.filter(item_sub_category__icontains=item_sub_category)
    if part_no and part_no not in ['', 'All']:
        queryset = queryset.filter(part_no__icontains=part_no)
    if gap_filter and gap_filter not in ['', 'All']:
        if gap_filter == 'gt0':
            queryset = queryset.filter(gap__gt=0)
        elif gap_filter == 'eq0':
            queryset = queryset.filter(gap=0) 
        elif gap_filter == 'lt0':
            queryset = queryset.filter(gap__lt=0)
    if grn_date_filter and grn_date_filter not in ['', 'All']:
        if grn_date_filter == 'blank':
            queryset = queryset.filter(actual_grn_delivery_date__isnull=True)
        elif grn_date_filter == 'non_blank':
            queryset = queryset.filter(actual_grn_delivery_date__isnull=False)

    queryset = queryset.order_by('-invoice_date')

    # Prepare raw data for page 1
    raw_data = []
    for record in queryset:
        row = {
            'Invoice No': record.invoice_no,
            'Invoice Date': record.invoice_date,
            'Part No': record.part_no,
            'Qty': record.qty,
            'Customer Name': record.customer_name,
            'Location': record.location,
            'Part Sub Category': record.part_sub_category,
            'Product': record.product,
            # IMPORTANT: Use this exact column name for pivot!
            'Total Invoice Value with GST': record.total_invoice_value_with_gst,
            'TDS Val': record.tds_amount,
            'Credited Val': record.credited_amount,
            'GAP': record.gap,
            'GRN No': record.grn_no,
            'GRN Date': record.actual_grn_delivery_date,
            'Due Date': record.due_date,
            'Payment Status': record.payment_status,
            'Received Date': record.received_date,
        }        # Add additional fields if needed
        for field in additional_fields:
            row[field.replace('_', ' ').title()] = getattr(record, field, '')
        raw_data.append(row)
    df = pd.DataFrame(raw_data)



    # Prepare pivot table for page 2
    if not df.empty and all(col in df.columns for col in ['Customer Name', 'Product', 'Location', 'Due Date', 'Total Invoice Value with GST']):
        df['due_date_str'] = pd.to_datetime(df['Due Date']).dt.strftime('%d-%m-%Y')
        pivot = pd.pivot_table(
            df,
            values='Total Invoice Value with GST',
            index=['Customer Name', 'Product', 'Location'],
            columns=['due_date_str'],
            aggfunc='sum',
            fill_value=0,
            margins=True,
            margins_name='Grand Total'
        )
        # Sort due_date_str columns in ascending order, keeping 'Grand Total' at the end
        cols = [col for col in pivot.columns if col != 'Grand Total']
        sorted_cols = sorted(cols, key=lambda x: datetime.strptime(x, '%d-%m-%Y'))
        if 'Grand Total' in pivot.columns:
            sorted_cols.append('Grand Total')
        pivot = pivot.reset_index()
        pivot = pivot[['Customer Name', 'Product', 'Location'] + sorted_cols]
        # Convert all value columns to Lakhs (divide by 100000)
        for col in sorted_cols:
            pivot[col] = pivot[col].apply(lambda x: round(x / 100000, 2) if pd.notnull(x) else x)
    else:
        pivot = pd.DataFrame()

    # Write both sheets to Excel
    import io
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Billing_Data')
        pivot.to_excel(writer, index=False, sheet_name='Summary')

    output.seek(0)
    now = datetime.now().strftime("%d_%m_%Y_%H_%M")
    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="billing_report_{now}.xlsx"'
    return response
