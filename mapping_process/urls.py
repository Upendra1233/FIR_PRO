from django.urls import path
from . import views

urlpatterns = [
    path('approve/<int:request_id>/', views.approve_request, name='approve_request'),
    path('reject/<int:request_id>/', views.reject_request, name='reject_request'),
    path('form/', views.mapping_process_form, name='mapping_process_form'),  # Add this if not already present
    path('mapping_process/download/', views.download_data, name='download_data'),
]