# appointments/urls.py
from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('', views.booking, name='booking'),
    path('confirm/<int:appointment_id>/', views.confirm_appointment, name='confirm_appointment'),
    path('invoice/<int:appointment_id>/', views.appointment_invoice, name='appointment_invoice'),
    path('manager/slots/', views.manager_manage_slots, name='manager_manage_slots'),
    path('manager/appointments/', views.manager_appointments, name='manager_appointments'),
    path('manager/appointment/<int:pk>/update/', views.manager_update_appointment, name='manager_update_appointment'),
    path('manager/customers/print/', views.manager_print_customers, name='manager_print_customers'),
]