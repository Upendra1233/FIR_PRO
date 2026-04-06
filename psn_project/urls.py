from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf.urls.static import static
from direct_calls.views import push_entry_to_ialert_view 
from psn_project import settings
from . import views as project_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', project_views.site_login, name='site_login'),
    path('logout/', project_views.site_logout, name='site_logout'),
    path('', include('psnapp.urls')),  # Include psnapp URLs under /menu/
    path('sr_request/', include('sr_request.urls')),  # Include SR Request app URLs
    path('mapping_process/', include('mapping_process.urls')),  # Include Mapping Process app URLs
    path('direct_calls/', include('direct_calls.urls')),  # Include t   he direct_calls app URLs
    path('billing_data/', include('billing_data.urls')),  # Include billing_data app's URLs
    path('ais140/', include('AIS140_FLOW.urls')),  # Include AIS140_FLOW app URLs
    path('sat_leave/', include('sat_leave.urls')),  # Include sat_leave app URLs
    path('data_search/', include('data_search.urls')),  # Include data_search app URLs
    path('bill_verify/', include('bill_verify.urls')),  # Include bill_verify app URLs
    path('trip_app/', include('trip_app.urls')),  # Include trip_app URLs
    path('api/push-entry-to-ialert/<int:id>/', push_entry_to_ialert_view, name='push_entry_to_ialert_root'), 
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
