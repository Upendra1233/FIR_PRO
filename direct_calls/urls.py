from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('form/', views.manager_form, name='manager_form'),
    path('engineer_form/<int:id>/', views.engineer_form, name='engineer_form'),
    path('manager_form/<int:id>/', views.manager_form, name='manager_form'),

    path('download_csv/', views.download_csv, name='download_csv'),
    path('real_time_data/', views.real_time_data, name='real_time_data'),
    path('check_for_updates/', views.check_for_updates, name='check_for_updates'),
    path('device-repair-form/<int:call_id>/', views.device_repair_form, name='device_repair_form'),
    path('submit_feedback/<int:call_id>/', views.submit_feedback, name='submit_feedback'),
    path('fetch_records_with_fields/', views.fetch_records_with_fields, name='fetch_records_with_fields'),
    path('get_unique_field_values/', views.get_unique_field_values, name='get_unique_field_values'),
    path('alt-device-form/<int:id>/', views.alt_device_form, name='alt_device_form_with_id'),
    path('device_tracking/', views.device_tracking, name='device_tracking'),
    path('fetch_filter_field_values/', views.fetch_filter_field_values, name='fetch_filter_field_values'),
    path('fetch_records_with_fields/', views.fetch_records_with_fields, name='fetch_records_with_fields'),
    path('fetch_device_tracking_records/', views.fetch_device_tracking_records, name='fetch_device_tracking_records'),
    path('part-e-form/', views.part_e_form, name='part_e_form'),
    path('part-e-form/<int:id>/', views.part_e_form, name='part_e_form_with_id'),
    path('part-e-form/<int:id>/', views.part_e_form, name='part_e_form'),
    path('part-f-form/<int:id>/', views.part_f_form, name='part_f_form'),
    path('part_b_a/<int:id>/', views.part_b_a, name='part_b_a'),
    path('part-b-a-realtime/', views.part_b_a_realtime, name='part_b_a_realtime'),
    path('api/darby-communication/<int:id>/', views.fetch_darby_communication, name='fetch_darby_communication'),
    path('api/create-ticket-prod/', views.api_create_ticket, name='api_create_ticket'),
    path('device_tracking_plant/', views.device_tracking_plant, name='device_tracking_plant'),
    path('device_tracking_plant_shipment/', views.device_tracking_plant_shippment, name='device_tracking_plant_shipment'),
    path('api/ialert-callback/', views.ialert_callback_and_forward, name='ialert_callback_and_forward'),
    path('call/<int:id>/remarks/', views.get_call_remarks, name='get_call_remarks'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

