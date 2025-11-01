# appointments/admin.py
from django.contrib import admin
from .models import TimeSlot, Appointment

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['date', 'start_time', 'end_time', 'is_available']
    list_filter = ['date', 'is_available']
    search_fields = ['date']

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['customer', 'service', 'time_slot', 'status', 'total_amount']
    list_filter = ['status', 'created_at', 'time_slot__date']
    search_fields = ['customer__username', 'service__title']
    filter_horizontal = ['addons']