from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),  # Ensure this is included only once
    path('mapping_process/', include('mapping_process.urls')),  # Include your app's URLs
    path('sat_leave/', views.sat_leave_form, name='sat_leave_form'),
    path('sat_leave/success/', views.sat_leave_success, name='sat_leave_success'),
]

