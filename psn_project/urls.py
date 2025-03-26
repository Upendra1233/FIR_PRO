from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('psnapp.urls')),
    path('sr_request/', include('sr_request.urls')),  # Include SR Request app URLs
    path('mapping_process/', include('mapping_process.urls')),  # Include Mapping Process app URLs
]