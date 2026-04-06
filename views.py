from datetime import date, timedelta

def fetch_billing_data(request):
    # ...existing code...
    grn_no = request.GET.get('grn_no', '').strip()  # <-- Add this line
    due_date_range = request.GET.get('due_date_range')
    today = date.today()

    # ...existing code...

    if grn_no:
        queryset = queryset.filter(grn_no__icontains=grn_no)  # <-- Add this block

    if due_date_range:
        if due_date_range == 'overdue_7':
            queryset = queryset.filter(due_date__lt=today - timedelta(days=7))
        elif due_date_range == 'overdue_15':
            queryset = queryset.filter(due_date__lt=today - timedelta(days=15))
        elif due_date_range == 'overdue_30':
            queryset = queryset.filter(due_date__lt=today - timedelta(days=30))
        elif due_date_range == 'due_7':
            queryset = queryset.filter(due_date__gte=today, due_date__lte=today + timedelta(days=7))
        elif due_date_range == 'due_15':
            queryset = queryset.filter(due_date__gte=today, due_date__lte=today + timedelta(days=15))
        elif due_date_range == 'due_30':
            queryset = queryset.filter(due_date__gte=today, due_date__lte=today + timedelta(days=30))
        elif due_date_range == 'due_60':
            queryset = queryset.filter(due_date__gte=today, due_date__lte=today + timedelta(days=60))
    # ...existing code...