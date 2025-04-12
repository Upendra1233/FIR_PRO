from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('', include('psnapp.urls')),  # Include psnapp URLs under /menu/
    path('sr_request/', include('sr_request.urls')),  # Include SR Request app URLs
    path('mapping_process/', include('mapping_process.urls')),  # Include Mapping Process app URLs
    path('direct_calls/', include('direct_calls.urls')),  # Include the direct_calls app URLs
    path('billing-data/', include('billing_data.urls')),
]