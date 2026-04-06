from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.add_data_record, name='add_data_record'),
    path('search/', views.search_data, name='search_data'),
    path('api/fetch/', views.fetch_external_data, name='fetch_external_data'),
]