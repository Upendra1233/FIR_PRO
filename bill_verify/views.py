from django.shortcuts import render, redirect, get_object_or_404
from .forms import BillVerifyForm
import csv
from django.http import HttpResponse, JsonResponse
from .models import BillVerify
from django.contrib import messages
from datetime import datetime

def bill_verify_view(request):
    if request.method == "POST":
        form = BillVerifyForm(request.POST)
        if form.is_valid():
            bill_obj = form.save(commit=False)
            # Calculate and set total_po_qty before saving
            try:
                tenure = int(bill_obj.tenure or 0)
                service_qty = int(bill_obj.service_qty or 0)
                bill_obj.total_po_qty = tenure * service_qty
            except Exception:
                bill_obj.total_po_qty = 0  # fallback if conversion fails

            # Calculate total_balance_qty
            try:
                invoice_qtys = [int(x) for x in (bill_obj.invoice_qty or '').split() if x.isdigit()]
                bill_obj.total_balance_qty = bill_obj.total_po_qty - sum(invoice_qtys)
            except Exception:
                bill_obj.total_balance_qty = bill_obj.total_po_qty  # fallback if conversion fails

            if not bill_obj.unique_id:
                now = datetime.now()
                yymm = now.strftime("%y%m")
                count = BillVerify.objects.filter(
                    unique_id__startswith=f"DTILBV-{yymm}"
                ).count() + 1
                nnnn = str(count).zfill(4)
                bill_obj.unique_id = f"DTILBV-{yymm}{nnnn}"
            bill_obj.save()
            messages.success(request, "Form submitted successfully!")
            return redirect('bill_verify:billform')
        else:
            return render(request, 'bill_verify/billform.html', {'form': form})
    else:
        form = BillVerifyForm()
    return render(request, 'bill_verify/billform.html', {'form': form})

def real_time_billing(request):
    return render(request, 'bill_verify/real_time_billing.html')

def get_unique_field_values(request):
    customer_names = list(BillVerify.objects.values_list('customer_name', flat=True).distinct())
    bill_years = list(BillVerify.objects.values_list('bill_year', flat=True).distinct())
    service_lines = list(BillVerify.objects.values_list('service_line', flat=True).distinct())
    return JsonResponse({
        'customer_names': [c for c in customer_names if c],
        'bill_years': [b for b in bill_years if b],
        'service_lines': [s for s in service_lines if s],
    })

def fetch_billing_data(request):
    unique_id = (request.GET.get('unique_id') or '').strip()
    customer_name = (request.GET.get('customer_name') or '').strip()
    bill_year = (request.GET.get('bill_year') or '').strip()
    invoice_no = (request.GET.get('invoice_no') or '').strip()
    from_date = (request.GET.get('from_date') or '').strip()
    to_date = (request.GET.get('to_date') or '').strip()
    final_po = (request.GET.get('final_po') or '').strip()
    po_no = (request.GET.get('po_no') or '').strip()
    service_line = (request.GET.get('service_line') or '').strip()

    try:
        page = int(request.GET.get('page', 1))
        if page < 1:
            page = 1
    except Exception:
        page = 1
    page_size = 25

    qs = BillVerify.objects.all()

    # Use case-insensitive contains for text filters to match frontend behaviour
    if unique_id:
        qs = qs.filter(unique_id__icontains=unique_id)
    if customer_name:
        qs = qs.filter(customer_name__icontains=customer_name)
    if service_line:
        qs = qs.filter(service_line__icontains=service_line)
    if bill_year:
        qs = qs.filter(bill_year__icontains=bill_year)
    if invoice_no:
        qs = qs.filter(invoice_number__icontains=invoice_no)
    if final_po:
        qs = qs.filter(final_po__icontains=final_po)
    if po_no:
        qs = qs.filter(po_no__icontains=po_no)

    # Date range filters - accept 'YYYY-MM-DD' from frontend date inputs
    # Use __gte/__lte which work with DateField/DateTimeField (Django accepts 'YYYY-MM-DD' strings)
    if from_date:
        try:
            qs = qs.filter(invoice_date__gte=from_date)
        except Exception:
            pass
    if to_date:
        try:
            qs = qs.filter(invoice_date__lte=to_date)
        except Exception:
            pass

    total = qs.count()
    total_pages = (total // page_size) + (1 if total % page_size else 0)
    start = (page - 1) * page_size
    end = start + page_size
    qs_page = qs.order_by('-invoice_date')[start:end]

    data = []
    for obj in qs_page:
        list_of_invoice_numbers = [x for x in (obj.invoice_number or '').split() if x]
        list_of_invoice_dates = [x for x in (obj.invoice_date or '').split() if x] if isinstance(obj.invoice_date, str) else []
        list_of_invoice_qtys = [x for x in (obj.invoice_qty or '').split() if x]
        list_of_billed_for = [x for x in (obj.billed_for or '').split() if x]

        max_invoices = max(
            len(list_of_invoice_numbers),
            len(list_of_invoice_dates),
            len(list_of_invoice_qtys),
            len(list_of_billed_for)
        )
        while len(list_of_invoice_numbers) < max_invoices:
            list_of_invoice_numbers.append('')
        while len(list_of_invoice_dates) < max_invoices:
            list_of_invoice_dates.append('')
        while len(list_of_invoice_qtys) < max_invoices:
            list_of_invoice_qtys.append('')
        while len(list_of_billed_for) < max_invoices:
            list_of_billed_for.append('')

        data.append({
            'id': obj.id,
            'unique_id': obj.unique_id,
            'customer_name': obj.customer_name,
            'final_po': obj.final_po,
            'po_no': obj.po_no,
            'service_line': obj.service_line,
            'profile_type': obj.profile_type,
            'tenure': obj.tenure,
            'bill_year': obj.bill_year,
            'start_month': obj.start_month.strftime('%Y-%m-%d') if obj.start_month else '',
            'end_month': obj.end_month.strftime('%Y-%m-%d') if obj.end_month else '',
            'invoice_number': list_of_invoice_numbers,
            'invoice_date': list_of_invoice_dates,
            'invoice_qty': list_of_invoice_qtys,
            'billed_for': list_of_billed_for,
        })

    return JsonResponse({
        'data': data,
        'current_page': page,
        'total_pages': total_pages,
        'has_previous': page > 1,
        'has_next': page < total_pages,
    })

def download_csv(request):
    """
    Export CSV using the same filters as the UI. Handles string filters (icontains)
    and date range (YYYY-MM-DD). Ensures only filtered qs rows are exported.
    """
    unique_id = (request.GET.get('unique_id') or '').strip()
    customer_name = (request.GET.get('customer_name') or '').strip()
    service_line = (request.GET.get('service_line') or '').strip()
    bill_year = (request.GET.get('bill_year') or '').strip()
    invoice_no = (request.GET.get('invoice_no') or '').strip()
    from_date = (request.GET.get('from_date') or '').strip()
    to_date = (request.GET.get('to_date') or '').strip()
    final_po = (request.GET.get('final_po') or '').strip()
    po_no = (request.GET.get('po_no') or '').strip()

    qs = BillVerify.objects.all()

    if unique_id:
        qs = qs.filter(unique_id__icontains=unique_id)
    if customer_name:
        qs = qs.filter(customer_name__icontains=customer_name)
    if service_line:
        qs = qs.filter(service_line__icontains=service_line)
    if bill_year:
        qs = qs.filter(bill_year__icontains=bill_year)
    if invoice_no:
        qs = qs.filter(invoice_number__icontains=invoice_no)
    if final_po:
        qs = qs.filter(final_po__icontains=final_po)
    if po_no:
        qs = qs.filter(po_no__icontains=po_no)

    # date filtering: parse YYYY-MM-DD and apply
    from_date_obj = None
    to_date_obj = None
    try:
        if from_date:
            from_date_obj = datetime.strptime(from_date, "%Y-%m-%d").date()
            qs = qs.filter(invoice_date__gte=from_date_obj)
        if to_date:
            to_date_obj = datetime.strptime(to_date, "%Y-%m-%d").date()
            qs = qs.filter(invoice_date__lte=to_date_obj)
    except Exception:
        # fallback: try raw string filter (Django can often handle YYYY-MM-DD strings)
        if from_date:
            try:
                qs = qs.filter(invoice_date__gte=from_date)
            except Exception:
                pass
        if to_date:
            try:
                qs = qs.filter(invoice_date__lte=to_date)
            except Exception:
                pass

    # Prepare CSV headers (determine max dynamic invoice columns from filtered qs)
    max_invoices = 1
    max_billed_for = 1
    for obj in qs:
        nums = (obj.invoice_number or '').split()
        billeds = (obj.billed_for or '').split()
        if len(nums) > max_invoices:
            max_invoices = len(nums)
        if len(billeds) > max_billed_for:
            max_billed_for = len(billeds)
    max_fields = max(max_invoices, max_billed_for)

    base_headers = [
        'Unique ID', 'Final PO', 'PO No', 'PO Date','Service Line', 'Service Activity', 'Serviced Qty','Tenure', 'Total PO Qty',
        'Customer Name', 'Profile Type', 'Customer Price', 'DTIL Price', 'Bill Year',
        'Start Month', 'End Month', 'Total Balance Qty'
    ]
    invoice_headers = []
    for i in range(1, max_fields + 1):
        invoice_headers += [
            f'Invoice Number {i}',
            f'Billed For {i}',
            f'Invoice Date {i}',
            f'Invoice Qty {i}'
        ]
    headers = base_headers + invoice_headers

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="bill_data.csv"'
    writer = csv.writer(response)
    writer.writerow(headers)

    for obj in qs.order_by('-invoice_date'):
        row = [
            obj.unique_id,
            obj.final_po,
            obj.po_no,
            obj.po_date,
            obj.service_line,
            obj.service_activity,
            obj.service_qty,
            obj.tenure,
            obj.total_po_qty,
            obj.customer_name,
            obj.profile_type,
            obj.customer_price,
            obj.DTIL_price,
            obj.bill_year,
            obj.start_month,
            obj.end_month,
            obj.total_balance_qty,
        ]
        numbers = (obj.invoice_number or '').split()
        billeds = (obj.billed_for or '').split()
        if isinstance(obj.invoice_date, str):
            dates = obj.invoice_date.split()
        elif obj.invoice_date is None:
            dates = []
        else:
            dates = [obj.invoice_date.strftime('%Y-%m-%d')]
        qtys = (obj.invoice_qty or '').split()

        while len(numbers) < max_fields:
            numbers.append('')
        while len(billeds) < max_fields:
            billeds.append('')
        while len(dates) < max_fields:
            dates.append('')
        while len(qtys) < max_fields:
            qtys.append('')

        for i in range(max_fields):
            row += [numbers[i], billeds[i], dates[i], qtys[i]]
        writer.writerow(row)

    return response

def bill_verify_detail(request, id):
    bill_obj = get_object_or_404(BillVerify, id=id)
    form = BillVerifyForm(instance=bill_obj)
    # Check for edit mode via query param
    detail_mode = not bool(request.GET.get('edit'))
    return render(request, 'bill_verify/billform.html', {
        'form': form,
        'detail_mode': detail_mode,
        'id': id
    })

def bill_verify_edit(request, id):
    bill_obj = get_object_or_404(BillVerify, id=id)
    if request.method == 'POST':
        form = BillVerifyForm(request.POST, instance=bill_obj)
        if form.is_valid():
            bill_obj = form.save(commit=False)
            # Preserve unique_id if already set
            if not bill_obj.unique_id:
                bill_obj.unique_id = BillVerify.objects.get(id=id).unique_id
            bill_obj.save()
            messages.success(request, "Form updated successfully!")
            return redirect('bill_verify:form', id=id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = BillVerifyForm(instance=bill_obj)
    detail_mode = not bool(request.GET.get('edit'))
    return render(request, 'bill_verify/billform.html', {
        'form': form,
        'detail_mode': detail_mode,
        'id': id
    })
