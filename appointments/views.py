# appointments/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Sum, Count
from datetime import datetime, date, timedelta
from .models import TimeSlot, Appointment
from .forms import AppointmentForm
from services.models import Service, Addon
import openpyxl
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
from django.contrib.auth.models import User

@login_required
def booking(request):
    service_id = request.GET.get('service')
    service = None
    form = None
    
    if service_id:
        service = get_object_or_404(Service, pk=service_id, is_active=True)
        if request.method == 'POST':
            form = AppointmentForm(request.POST, service_id=service_id)
            if form.is_valid():
                appointment = form.save(commit=False)
                appointment.customer = request.user
                appointment.status = 'pending'
                
                # Calculate total amount
                total = float(service.price)
                selected_addons = form.cleaned_data['addons']
                for addon in selected_addons:
                    total += float(addon.price)
                appointment.total_amount = total
                
                appointment.save()
                appointment.addons.set(selected_addons)
                
                messages.success(request, 'Appointment requested successfully! Please confirm.')
                return redirect('appointments:confirm_appointment', appointment_id=appointment.id)
        else:
            form = AppointmentForm(service_id=service_id)
    
    services = Service.objects.filter(is_active=True)
    return render(request, 'appointments/booking.html', {
        'services': services,
        'service': service,
        'form': form,
    })

@login_required
def confirm_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, pk=appointment_id, customer=request.user)
    if request.method == 'POST':
        # In real app, you'd integrate payment here
        appointment.status = 'confirmed'
        appointment.save()
        
        # Mark time slot as unavailable
        appointment.time_slot.is_available = False
        appointment.time_slot.save()
         
        messages.success(request, 'Appointment confirmed successfully!')
        return redirect('appointments:appointment_invoice', appointment_id=appointment.id)
                  
    
    return render(request, 'appointments/confirm_appointment.html', {'appointment': appointment})

@login_required
def appointment_invoice(request, appointment_id):
    appointment = get_object_or_404(Appointment, pk=appointment_id, customer=request.user)
    return render(request, 'appointments/invoice.html', {'appointment': appointment})

@login_required
def manager_manage_slots(request):
    if not request.user.profile.is_manager:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')
    
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        interval = int(request.POST.get('interval', 30))
        
        if start_date and end_date and start_time and end_time:
            start_dt = datetime.combine(date.fromisoformat(start_date), datetime.strptime(start_time, '%H:%M').time())
            end_dt = datetime.combine(date.fromisoformat(end_date), datetime.strptime(end_time, '%H:%M').time())
            
            current_date = date.fromisoformat(start_date)
            end_date_obj = date.fromisoformat(end_date)
            
            while current_date <= end_date_obj:
                current_time = datetime.strptime(start_time, '%H:%M').time()
                end_time_obj = datetime.strptime(end_time, '%H:%M').time()
                
                while current_time < end_time_obj:
                    start_time_obj = current_time
                    end_datetime = datetime.combine(current_date, current_time) + timedelta(minutes=interval)
                    end_time_obj = end_datetime.time()
                    
                    if end_time_obj > datetime.strptime(end_time, '%H:%M').time():
                        break
                    
                    TimeSlot.objects.get_or_create(
                        date=current_date,
                        start_time=start_time_obj,
                        end_time=end_time_obj,
                        defaults={'is_available': True}
                    )
                    
                    current_time = end_time_obj
                
                current_date += timedelta(days=1)
            
            messages.success(request, 'Time slots generated successfully!')
            return redirect('appointments:manager_manage_slots')
    
    slots = TimeSlot.objects.filter(date__gte=date.today()).order_by('date', 'start_time')[:50]
    return render(request, 'appointments/manager_manage_slots.html', {'slots': slots})

@login_required
def manager_appointments(request):
    if not request.user.profile.is_manager:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')
    
    status_filter = request.GET.get('status', '')
    date_filter = request.GET.get('date', '')
    
    appointments = Appointment.objects.all().order_by('-created_at')
    
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    if date_filter:
        appointments = appointments.filter(time_slot__date=date.fromisoformat(date_filter))
    
    return render(request, 'appointments/manager_appointments.html', {
        'appointments': appointments,
        'status_filter': status_filter,
        'date_filter': date_filter,
    })

@login_required
def manager_update_appointment(request, pk):
    if not request.user.profile.is_manager:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')
    
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Appointment.STATUS_CHOICES):
            old_status = appointment.status
            appointment.status = new_status
            appointment.save()
            
            # If confirming, mark slot unavailable; if cancelling, mark available
            if new_status == 'confirmed' and old_status != 'confirmed':
                appointment.time_slot.is_available = False
                appointment.time_slot.save()
            elif new_status == 'cancelled' and old_status == 'confirmed':
                appointment.time_slot.is_available = True
                appointment.time_slot.save()
            
            messages.success(request, 'Appointment updated successfully!')
        return redirect('appointments:manager_appointments')
    
    return redirect('appointments:manager_appointments')

@login_required
def manager_print_customers(request):
    if not request.user.profile.is_manager:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')
    
    customer_id = request.GET.get('customer_id')
    if customer_id:
        customers = [get_object_or_404(User, pk=customer_id)]
    else:
        customers = User.objects.filter(appointment__isnull=False).distinct()
    
    # Generate Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Customers"
    
    headers = ['ID', 'Username', 'Email', 'First Name', 'Last Name', 'Phone', 'Total Appointments', 'Total Spent']
    ws.append(headers)
    
    for user in customers:
        total_appointments = Appointment.objects.filter(customer=user).count()
        total_spent = Appointment.objects.filter(customer=user).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        phone = user.profile.phone if hasattr(user, 'profile') else ''
        ws.append([
            user.id,
            user.username,
            user.email,
            user.first_name,
            user.last_name,
            phone,
            total_appointments,
            float(total_spent),
        ])
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=customers_report.xlsx'
    wb.save(response)
    return response