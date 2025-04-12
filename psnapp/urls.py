# filepath: psnapp/urls.py
from django.urls import path
from psnapp import views

urlpatterns = [
    path('', views.homepage, name='homepage'),  # Map root URL to the homepage view
    path('fir_form/', views.psn_form, name='psn_form'),
    path('success/', views.success, name='success'),
    path('thank_you/', views.thank_you, name='thank_you'),
    path('approve_request/<int:id>/', views.approve_request, name='approve_request'),
    path('reject_request/<int:id>/', views.reject_request, name='reject_request'),
    path('approve_hod_request/<int:id>/', views.approve_hod_request, name='approve_hod_request'),
    path('reject_hod_request/<int:id>/', views.reject_hod_request, name='reject_hod_request'),
    path('engineer_response/<int:id>/', views.engineer_response, name='engineer_response'),
    path('request_details/<int:id>/', views.request_details, name='request_details'),
    path('psn_form_edit/<int:id>/', views.psn_form_edit, name='psn_form_edit'),
    path('download_data/', views.downloaddata, name='downloaddata'),
]
