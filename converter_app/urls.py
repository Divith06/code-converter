# backend/converter_app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('convert/', views.convert_code, name='convert'),
    path('run_source/', views.run_source_code, name='run_source'),
    path('run_converted/', views.run_converted_code, name='run_converted'),
]
