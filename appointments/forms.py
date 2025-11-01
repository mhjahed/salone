# appointments/forms.py
from django import forms
from .models import Appointment
from services.models import Addon
from datetime import date
from .models import TimeSlot


class AppointmentForm(forms.ModelForm):
    addons = forms.ModelMultipleChoiceField(
        queryset=Addon.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Appointment
        fields = ['service', 'time_slot', 'addons']
        widgets = {
            'service': forms.HiddenInput(),
            'time_slot': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        service_id = kwargs.pop('service_id', None)
        super().__init__(*args, **kwargs)
        if service_id:
            self.fields['addons'].queryset = Addon.objects.filter(service_id=service_id)
        
        # Only show available future time slots
        self.fields['time_slot'].queryset = TimeSlot.objects.filter(
            is_available=True,
            date__gte=date.today()
        ).order_by('date', 'start_time')