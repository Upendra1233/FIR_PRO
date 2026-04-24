from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [    
    path('part_a_form/', views.part_a_form, name='part_a_form'),
    path('part_a_form/<int:id>/', views.part_a_form, name='part_a_form'),

    path('part_b_form/<int:id>/', views.part_b_form, name='part_b_form'),
    path('success/', views.success_page, name='success_page'),
    path('download-part-b-csv/', views.download_part_b_csv, name='download_part_b_csv'),
    path('download-full-csv/', views.download_full_csv, name='download_full_csv'),
    path('ais140/real_time_page/', views.real_time_page, name='real_time_page'),
    path('api/create-ais140-ticket/', views.api_create_ais140_ticket, name='api_create_ais140_ticket'),
    path('api/update-ais140-remarks/', views.api_update_ais140_remarks, name='api_update_ais140_remarks'),
    path('fetch_darby_communication_ais140/<int:id>/', views.fetch_darby_communication_ais140, name='fetch_darby_communication_ais140'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

