from django.urls import path
from . import views

urlpatterns = [
    path('form/', views.sr_request_form, name='sr_request_form'),
    path('approve/<int:request_id>/', views.approve_request, name='approve_request'),
    path('reject/<int:request_id>/', views.reject_request, name='reject_request'),
    path('details/<int:request_id>/', views.sr_details_form, name='sr_details_form'),
        path('edit/<int:request_id>/', views.edit_sr_request_form, name='edit_sr_request_form'), 
    path('success/', views.sr_request_success, name='sr_request_success'),  # URL for the success page
]