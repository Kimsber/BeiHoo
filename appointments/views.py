from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q, Count
from datetime import timedelta, datetime, time as dt_time
from collections import defaultdict

from .models import Appointment, ServiceType, AppointmentNote
from account.models import User


@login_required
def check_in_appointment(request, appointment_id):
    """Check in an appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Only staff can check in
    if not request.user.is_clinician and request.user.role not in ['nurse', 'admin']:
        raise PermissionDenied
    
    if appointment.check_in(request.user):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'status': appointment.status})
        return redirect(request.META.get('HTTP_REFERER', 'dashboard:home'))
    
    return JsonResponse({'success': False, 'error': 'Cannot check in'}, status=400)


@login_required
def complete_appointment(request, appointment_id):
    """Complete an appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Only the practitioner or admin can complete
    if appointment.practitioner != request.user and request.user.role != 'admin':
        raise PermissionDenied
    
    if appointment.complete():
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'status': appointment.status})
        return redirect(request.META.get('HTTP_REFERER', 'dashboard:home'))
    
    return JsonResponse({'success': False, 'error': 'Cannot complete'}, status=400)


@login_required
def cancel_appointment(request, appointment_id):
    """Cancel an appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check permissions
    if (appointment.practitioner != request.user and 
        appointment.patient != request.user and 
        request.user.role not in ['admin', 'nurse']):
        raise PermissionDenied
    
    reason = request.POST.get('reason', '')
    if appointment.cancel(reason):
        # Add note
        AppointmentNote.objects.create(
            appointment=appointment,
            author=request.user,
            note_type='cancellation',
            content=reason or '預約已取消'
        )
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'status': appointment.status})
        return redirect(request.META.get('HTTP_REFERER', 'dashboard:home'))
    
    return JsonResponse({'success': False, 'error': 'Cannot cancel'}, status=400)


@login_required
def appointment_detail(request, appointment_id):
    """View appointment details"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check permissions
    if (appointment.practitioner != request.user and 
        appointment.patient != request.user and 
        request.user.role not in ['admin', 'nurse']):
        raise PermissionDenied
    
    context = {
        'appointment': appointment,
        'notes': appointment.notes.all(),
    }
    
    return render(request, 'appointments/appointment_detail.html', context)


def get_appointment_schedule_data(date_start, date_end, practitioners=None):
    """
    Get appointment schedule data for grid display
    Returns organized data structure for template rendering
    """
    appointments = Appointment.objects.filter(
        appointment_date__range=[date_start, date_end]
    ).select_related('patient', 'practitioner', 'service_type')
    
    if practitioners:
        appointments = appointments.filter(practitioner__in=practitioners)
    
    # Organize by date and practitioner
    schedule_by_date = defaultdict(lambda: defaultdict(list))
    
    for appt in appointments:
        schedule_by_date[appt.appointment_date][appt.practitioner.id].append(appt)
    
    return schedule_by_date


def get_time_slots(start_hour=8, end_hour=18, interval_minutes=30):
    """Generate time slots for the day"""
    slots = []
    current = datetime.combine(datetime.today(), dt_time(start_hour, 0))
    end = datetime.combine(datetime.today(), dt_time(end_hour, 0))
    
    while current <= end:
        slots.append(current.time())
        current += timedelta(minutes=interval_minutes)
    
    return slots


@login_required
def appointment_schedule_grid(request):
    """
    Full appointment schedule grid view for admin
    Shows all appointments in a time-slot based grid
    """
    if request.user.role not in ['admin', 'nurse']:
        raise PermissionDenied
    
    # Get date range (default: today + 6 days)
    today = timezone.now().date()
    date_param = request.GET.get('date', str(today))
    try:
        start_date = datetime.strptime(date_param, '%Y-%m-%d').date()
    except:
        start_date = today
    
    view_mode = request.GET.get('view', 'week')  # week or day
    
    if view_mode == 'day':
        end_date = start_date
        dates = [start_date]
    else:  # week
        end_date = start_date + timedelta(days=6)
        dates = [start_date + timedelta(days=i) for i in range(7)]
    
    # Get all active practitioners
    practitioners = User.objects.filter(
        role__in=['doctor', 'therapist'],
        is_active=True
    ).order_by('role', 'last_name', 'first_name')
    
    # Get appointments
    appointments = Appointment.objects.filter(
        appointment_date__range=[start_date, end_date],
        status__in=['booked', 'arrived', 'fulfilled']
    ).select_related('patient', 'practitioner', 'service_type').order_by('appointment_date', 'start_time')
    
    # Organize by date and practitioner
    schedule = defaultdict(lambda: defaultdict(list))
    for appt in appointments:
        schedule[appt.appointment_date][appt.practitioner.id].append(appt)
    
    # Build schedule grid
    schedule_grid = []
    for date in dates:
        day_data = {
            'date': date,
            'is_today': date == today,
            'practitioners_schedule': []
        }
        
        for practitioner in practitioners:
            day_appts = schedule[date].get(practitioner.id, [])
            day_data['practitioners_schedule'].append({
                'practitioner': practitioner,
                'appointments': sorted(day_appts, key=lambda x: x.start_time)
            })
        
        schedule_grid.append(day_data)
    
    # Statistics
    total_appointments = appointments.count()
    today_appointments = appointments.filter(appointment_date=today).count()
    arrived_count = appointments.filter(status='arrived').count()
    completed_count = appointments.filter(status='fulfilled').count()
    
    context = {
        'schedule_grid': schedule_grid,
        'practitioners': practitioners,
        'start_date': start_date,
        'end_date': end_date,
        'today': today,
        'view_mode': view_mode,
        'total_appointments': total_appointments,
        'today_appointments': today_appointments,
        'arrived_count': arrived_count,
        'completed_count': completed_count,
        'prev_week': start_date - timedelta(days=7),
        'next_week': start_date + timedelta(days=7),
    }
    
    return render(request, 'appointments/schedule_grid.html', context)