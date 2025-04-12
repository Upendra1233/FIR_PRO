from django.shortcuts import render, redirect
from .forms import BillingDataForm
from django.contrib import messages

def add_billing_data(request):
    if request.method == 'POST':
        form = BillingDataForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Billing data saved successfully!')
            return redirect('add_billing_data')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BillingDataForm()
    return render(request, 'billing_data/bd_entry_form.html', {'form': form})

def bd_entry_form(request):
    return render(request, 'billing_data/bd_entry_form.html')


