from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # Ensure this is included only once
    path('mapping_process/', include('mapping_process.urls')),  # Include your app's URLs
]

