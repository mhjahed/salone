# dashboard/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Sum, Count, Q
from datetime import date, timedelta
from datetime import datetime
import openpyxl
from appointments.models import Appointment
from services.models import Service, Addon
from django.contrib.auth.models import User
from django.shortcuts import redirect

@login_required
def manager_dashboard(request):
    if not request.user.profile.is_manager:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')
    
    today = date.today()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Basic stats
    total_appointments = Appointment.objects.count()
    pending_appointments = Appointment.objects.filter(status='pending').count()
    confirmed_appointments = Appointment.objects.filter(status='confirmed').count()
    total_customers = User.objects.filter(appointment__isnull=False).distinct().count()
    total_revenue = Appointment.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    # Recent appointments
    recent_appointments = Appointment.objects.select_related('customer', 'service').order_by('-created_at')[:10]
    
    context = {
        'total_appointments': total_appointments,
        'pending_appointments': pending_appointments,
        'confirmed_appointments': confirmed_appointments,
        'total_customers': total_customers,
        'total_revenue': total_revenue,
        'recent_appointments': recent_appointments,
    }
    return render(request, 'dashboard/manager_dashboard.html', context)

@login_required
def manager_analytics(request):
    if not request.user.profile.is_manager:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')
    
    today = date.today()
    filter_type = request.GET.get('filter', 'week')
    
    if filter_type == 'month':
        start_date = today - timedelta(days=30)
        date_format = '%Y-%m-%d'
    elif filter_type == '3months':
        start_date = today - timedelta(days=90)
        date_format = '%Y-%m-%d'
    else:  # week
        start_date = today - timedelta(days=7)
        date_format = '%Y-%m-%d'
    
    # Appointments Summary
    appointments = Appointment.objects.filter(created_at__date__gte=start_date)
    daily_appointments = {}
    current_date = start_date
    while current_date <= today:
        daily_appointments[current_date.strftime(date_format)] = 0
        current_date += timedelta(days=1)
    
    for appt in appointments:
        date_str = appt.created_at.date().strftime(date_format)
        if date_str in daily_appointments:
            daily_appointments[date_str] += 1
    
    # Revenue by day
    daily_revenue = {}
    current_date = start_date
    while current_date <= today:
        daily_revenue[current_date.strftime(date_format)] = 0
        current_date += timedelta(days=1)
    
    for appt in appointments:
        date_str = appt.created_at.date().strftime(date_format)
        if date_str in daily_revenue:
            daily_revenue[date_str] += float(appt.total_amount)
    
    # Top Services
    top_services = Service.objects.annotate(
        total_bookings=Count('appointment'),
        total_revenue=Sum('appointment__total_amount')
    ).filter(total_bookings__gt=0).order_by('-total_bookings')[:5]
    
    # Addon Usage
    addon_usage = Addon.objects.annotate(
        times_used=Count('appointment')
    ).filter(times_used__gt=0).order_by('-times_used')[:5]
    
    # Customer Growth (last 6 months)
    customer_growth = []
    for i in range(6, 0, -1):
        month_start = today.replace(day=1) - timedelta(days=(i-1)*30)
        month_end = month_start.replace(day=28) + timedelta(days=4)  # Next month's 1st
        month_end = month_end.replace(day=1) - timedelta(days=1)
        
        new_customers = User.objects.filter(
            appointment__created_at__date__gte=month_start,
            appointment__created_at__date__lte=month_end
        ).distinct().count()
        
        customer_growth.append({
            'month': month_start.strftime('%b %Y'),
            'count': new_customers
        })
    
    context = {
        'filter_type': filter_type,
        'daily_appointments_labels': list(daily_appointments.keys()),
        'daily_appointments_data': list(daily_appointments.values()),
        'daily_revenue_labels': list(daily_revenue.keys()),
        'daily_revenue_data': list(daily_revenue.values()),
        'top_services': top_services,
        'addon_usage': addon_usage,
        'customer_growth_labels': [item['month'] for item in customer_growth],
        'customer_growth_data': [item['count'] for item in customer_growth],
    }
    return render(request, 'dashboard/manager_analytics.html', context)

@login_required
def export_dashboard_data(request):
    if not request.user.profile.is_manager:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')
    
    filter_type = request.GET.get('filter', 'week')
    today = date.today()
    
    if filter_type == 'month':
        start_date = today - timedelta(days=30)
    elif filter_type == '3months':
        start_date = today - timedelta(days=90)
    else:
        start_date = today - timedelta(days=7)
    
    appointments = Appointment.objects.filter(created_at__date__gte=start_date)
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Dashboard Report"
    
    headers = ['Date', 'Customer', 'Service', 'Addons', 'Total Amount', 'Status']
    ws.append(headers)
    
    for appt in appointments:
        addons_str = ", ".join([a.name for a in appt.addons.all()])
        ws.append([
            appt.created_at.strftime('%Y-%m-%d'),
            appt.customer.get_full_name() or appt.customer.username,
            appt.service.title,
            addons_str,
            float(appt.total_amount),
            appt.get_status_display(),
        ])
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=salone_dashboard_{filter_type}.xlsx'
    wb.save(response)
    return response