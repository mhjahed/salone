# services/admin.py
from django.contrib import admin
from .models import Service, Addon

class AddonInline(admin.TabularInline):
    model = Addon
    extra = 1

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'duration', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'summary']
    inlines = [AddonInline]

@admin.register(Addon)
class AddonAdmin(admin.ModelAdmin):
    list_display = ['name', 'service', 'price']
    list_filter = ['service']
    search_fields = ['name']