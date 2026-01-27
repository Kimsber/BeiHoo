from django import forms
from django.core.exceptions import ValidationError
from .models import Appointment, ServiceType, AppointmentNote
from account.models import User
from datetime import datetime, time as dt_time


class AppointmentForm(forms.ModelForm):
    """Form for creating and editing appointments"""
    
    patient = forms.ModelChoiceField(
        queryset=User.objects.filter(role='patient', is_active=True),
        label='病患',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    practitioner = forms.ModelChoiceField(
        queryset=User.objects.filter(role__in=['doctor', 'therapist'], is_active=True),
        label='醫療人員',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    service_type = forms.ModelChoiceField(
        queryset=ServiceType.objects.all(),
        label='服務類型',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    appointment_date = forms.DateField(
        label='日期',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    start_time = forms.TimeField(
        label='開始時間',
        widget=forms.TimeInput(attrs={
            'type': 'time',
            'class': 'form-control'
        })
    )
    
    end_time = forms.TimeField(
        label='結束時間',
        widget=forms.TimeInput(attrs={
            'type': 'time',
            'class': 'form-control'
        })
    )
    
    reason = forms.CharField(
        required=False,
        label='就診原因',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': '請描述就診原因或症狀...'
        })
    )
    
    class Meta:
        model = Appointment
        fields = ['patient', 'practitioner', 'service_type', 'appointment_date', 
                  'start_time', 'end_time', 'status', 'reason']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        practitioner = cleaned_data.get('practitioner')
        appointment_date = cleaned_data.get('appointment_date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        # Check if end_time is after start_time
        if start_time and end_time:
            if end_time <= start_time:
                raise ValidationError('結束時間必須晚於開始時間')
        
        # Check for overlapping appointments
        if practitioner and appointment_date and start_time and end_time:
            overlapping = Appointment.objects.filter(
                practitioner=practitioner,
                appointment_date=appointment_date,
                status__in=['proposed', 'pending', 'booked', 'arrived']
            ).exclude(pk=self.instance.pk if self.instance.pk else None)
            
            for appt in overlapping:
                # Check if time ranges overlap
                if not (end_time <= appt.start_time or start_time >= appt.end_time):
                    raise ValidationError(
                        f'此時段與現有預約衝突：{appt.start_time.strftime("%H:%M")} - {appt.end_time.strftime("%H:%M")}'
                    )
        
        return cleaned_data


class AppointmentFilterForm(forms.Form):
    """Form for filtering appointments"""
    
    date_from = forms.DateField(
        required=False,
        label='開始日期',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        label='結束日期',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    practitioner = forms.ModelChoiceField(
        queryset=User.objects.filter(role__in=['doctor', 'therapist'], is_active=True),
        required=False,
        label='醫療人員',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    service_type = forms.ModelChoiceField(
        queryset=ServiceType.objects.all(),
        required=False,
        label='服務類型',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    status = forms.ChoiceField(
        choices=[('', '所有狀態')] + Appointment.STATUS_CHOICES,
        required=False,
        label='狀態',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    search = forms.CharField(
        required=False,
        label='搜尋病患',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '搜尋病患姓名或帳號...'
        })
    )


class AppointmentNoteForm(forms.ModelForm):
    """Form for adding notes to appointments"""
    
    class Meta:
        model = AppointmentNote
        fields = ['note_type', 'content']
        widgets = {
            'note_type': forms.Select(attrs={'class': 'form-select'}),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': '請輸入備註內容...'
            })
        }


class QuickAppointmentForm(forms.Form):
    """Quick form for creating appointments with preset times"""
    
    patient = forms.ModelChoiceField(
        queryset=User.objects.filter(role='patient', is_active=True),
        label='病患',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    practitioner = forms.ModelChoiceField(
        queryset=User.objects.filter(role__in=['doctor', 'therapist'], is_active=True),
        label='醫療人員',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    service_type = forms.ModelChoiceField(
        queryset=ServiceType.objects.all(),
        label='服務類型',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    appointment_date = forms.DateField(
        label='日期',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    time_slot = forms.ChoiceField(
        label='時段',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Generate time slots (8:00 - 17:00, 30-minute intervals)
        time_slots = []
        for hour in range(8, 18):
            for minute in [0, 30]:
                time_obj = dt_time(hour, minute)
                time_slots.append((
                    time_obj.strftime('%H:%M'),
                    time_obj.strftime('%H:%M')
                ))
        self.fields['time_slot'].choices = time_slots