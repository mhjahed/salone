# services/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Service, Addon
from .forms import ServiceForm, AddonFormSet

def service_list(request):
    services = Service.objects.filter(is_active=True)
    return render(request, 'services/service_list.html', {'services': services})

def service_detail(request, pk):
    service = get_object_or_404(Service, pk=pk, is_active=True)
    return render(request, 'services/service_detail.html', {'service': service})

@login_required
def manager_add_service(request):
    if not request.user.profile.is_manager:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')
    
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES)
        formset = AddonFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            service = form.save()
            addons = formset.save(commit=False)
            for addon in addons:
                addon.service = service
                addon.save()
            messages.success(request, 'Service created successfully!')
            return redirect('services:service_detail', pk=service.pk)
    else:
        form = ServiceForm()
        formset = AddonFormSet()
    return render(request, 'services/manager_service_form.html', {
        'form': form,
        'formset': formset,
        'title': 'Add New Service'
    })

@login_required
def manager_edit_service(request, pk):
    if not request.user.profile.is_manager:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')
    
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES, instance=service)
        formset = AddonFormSet(request.POST, instance=service)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Service updated successfully!')
            return redirect('services:service_detail', pk=service.pk)
    else:
        form = ServiceForm(instance=service)
        formset = AddonFormSet(instance=service)
    return render(request, 'services/manager_service_form.html', {
        'form': form,
        'formset': formset,
        'title': 'Edit Service',
        'service': service
    })

@login_required
def manager_delete_service(request, pk):
    if not request.user.profile.is_manager:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')
    
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        service.delete()
        messages.success(request, 'Service deleted successfully!')
        return redirect('services:service_list')
    return render(request, 'services/manager_service_confirm_delete.html', {'service': service})