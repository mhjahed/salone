# dashboard/urls.py
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.manager_dashboard, name='manager_dashboard'),
    path('analytics/', views.manager_analytics, name='manager_analytics'),
    path('export/', views.export_dashboard_data, name='export_dashboard_data'),
]