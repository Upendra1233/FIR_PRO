from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('form/', views.manager_form, name='manager_form'),
    path('engineer_form/<int:id>/', views.engineer_form, name='engineer_form'),
    path('approve_request/<int:call_id>/', views.approve_request, name='approve_request'),
    path('download-csv/', views.download_csv, name='download_csv'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)