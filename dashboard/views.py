from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.conf import settings
from account.models import User, AuditLog

@login_required
def dashboard_home(request):
    """Route user to appropriate dashboard based on role"""
    dashboard_name = settings.ROLE_DASHBOARD_MAP.get(request.user.role, 'dashboard:patient')
    return redirect(dashboard_name)


@login_required
def admin_dashboard(request):
    """系統管理員儀表板"""
    if request.user.role != 'admin':
        raise PermissionDenied("您沒有權限訪問此頁面")
    
    context = {
        'title': '系統管理儀表板',
        'total_users': User.objects.count(),
        'total_patients': User.objects.filter(role='patient').count(),
        'total_doctors': User.objects.filter(role='doctor').count(),
        'total_therapists': User.objects.filter(role='therapist').count(),
        'total_nurses': User.objects.filter(role='nurse').count(),
        'recent_users': User.objects.all().order_by('-created_at')[:5],
        'recent_logs': AuditLog.objects.select_related('user').all()[:10],
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


@login_required
def doctor_dashboard(request):
    """醫師儀表板"""
    if request.user.role != 'doctor':
        raise PermissionDenied("您沒有權限訪問此頁面")
    
    context = {
        'title': '醫師儀表板',
        'doctor': request.user,
        'my_patients_count': User.objects.filter(role='patient').count(),
        # Add: appointments, consultations, etc.
    }
    return render(request, 'dashboard/doctor_dashboard.html', context)


@login_required
def therapist_dashboard(request):
    """治療師儀表板"""
    if request.user.role != 'therapist':
        raise PermissionDenied("您沒有權限訪問此頁面")
    
    context = {
        'title': '治療師儀表板',
        'therapist': request.user,
        'my_patients_count': User.objects.filter(role='patient').count(),
        # Add: therapy sessions, rehabilitation plans, etc.
    }
    return render(request, 'dashboard/therapist_dashboard.html', context)


@login_required
def nurse_dashboard(request):
    """護理師儀表板"""
    if request.user.role != 'nurse':
        raise PermissionDenied("您沒有權限訪問此頁面")
    
    context = {
        'title': '護理師儀表板',
        'nurse': request.user,
        'patients_count': User.objects.filter(role='patient').count(),
        # Add: patient care tasks, medication schedules, etc.
    }
    return render(request, 'dashboard/nurse_dashboard.html', context)


@login_required
def patient_dashboard(request):
    """病患儀表板"""
    if request.user.role != 'patient':
        raise PermissionDenied("您沒有權限訪問此頁面")
    
    context = {
        'title': '我的健康儀表板',
        'patient': request.user,
        # Add: appointments, therapy sessions, progress reports, etc.
    }
    return render(request, 'dashboard/patient_dashboard.html', context)


@login_required
def researcher_dashboard(request):
    """研究員儀表板"""
    if request.user.role != 'researcher':
        raise PermissionDenied("您沒有權限訪問此頁面")
    
    context = {
        'title': '研究員儀表板',
        'researcher': request.user,
        'total_patients': User.objects.filter(role='patient').count(),
        # Add: research data, analytics, reports, etc.
    }
    return render(request, 'dashboard/researcher_dashboard.html', context)