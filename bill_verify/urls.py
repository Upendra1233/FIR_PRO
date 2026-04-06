from django.urls import path 
from . import views
from django.conf import settings
app_name = 'bill_verify'

urlpatterns = [
    path('bill-verify/', views.bill_verify_view, name='billform'),
    path('real-time/', views.real_time_billing, name='real_time_billing'),
    path('get_unique_field_values/', views.get_unique_field_values, name='get_unique_field_values'),
    path('fetch/', views.fetch_billing_data, name='fetch_billing_data'),
    path('download_csv/', views.download_csv, name='download_csv'),
    path('form/<int:id>/', views.bill_verify_edit, name='form'),  # <-- This must point to bill_verify_edit
]