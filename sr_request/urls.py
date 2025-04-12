from django.urls import path
from . import views

urlpatterns = [
    path('form/', views.sr_request_form, name='sr_request_form'),
    path('approve/<int:request_id>/', views.approve_request, name='approve_request'),
    path('reject/<int:request_id>/', views.reject_request, name='reject_request'),
    path('details/<int:request_id>/', views.sr_details_form, name='sr_request_details'),  # Use a single pattern
    path('edit/<int:request_id>/', views.edit_sr_request_form, name='edit_sr_request_form'),
    path('success/', views.sr_request_success, name='sr_request_success'),
    path('sr_request/download/', views.download_sr_requests, name='download_sr_requests'),
    path('new_details/<int:request_id>/', views.new_sr_details_form, name='new_sr_details_form'),

]