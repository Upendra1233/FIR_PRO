from django.urls import path
from . import views
from .views import download_billing_data_csv

urlpatterns = [
    path('add-billing-data/', views.add_billing_data, name='add_billing_data'),
    path('real_time/', views.bill_real_time_data, name='bill_real_time_data'),
    path('fetch/', views.fetch_billing_data, name='fetch_billing_data'),
    path('get_unique_field_values/', views.get_unique_field_values, name='get_unique_field_values'),
    path('download-invoice/', views.download_invoice_csv, name='download_invoice_csv'),
    path('add-billing-data/<int:pk>/', views.add_billing_data_detail, name='add_billing_data_detail'),  # <-- Add this line
    path('download_csv/', views.download_csv, name='download_csv'),  # <-- Excel view
    path('download_billing_data_csv/', download_billing_data_csv, name='download_billing_data_csv'),  # <-- CSV view
]