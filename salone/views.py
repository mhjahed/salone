# salone/views.py
from django.shortcuts import render
from services.models import Service

def home(request):
    # Get 8 most recently added active services as "popular"
    popular_services = Service.objects.filter(is_active=True).order_by('-created_at')[:8]
    return render(request, 'home.html', {'popular_services': popular_services})