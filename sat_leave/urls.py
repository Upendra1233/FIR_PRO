from django.urls import path
from . import views

urlpatterns = [
    path('leave-request/', views.leave_request_view, name='leave_request'),
    path('approve/<int:leave_request_id>/', views.approve_leave_request, name='approve_leave_request'),
    path('reject/<int:leave_request_id>/', views.reject_leave_request, name='reject_leave_request'),
]