# services/urls.py
from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('', views.service_list, name='service_list'),
    path('<int:pk>/', views.service_detail, name='service_detail'),
    path('manager/add/', views.manager_add_service, name='manager_add_service'),
    path('manager/edit/<int:pk>/', views.manager_edit_service, name='manager_edit_service'),
    path('manager/delete/<int:pk>/', views.manager_delete_service, name='manager_delete_service'),
]