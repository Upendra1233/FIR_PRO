from django.urls import path
from . import views

urlpatterns = [
    path('add-billing-data/', views.add_billing_data, name='add_billing_data'),
]