from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.http import JsonResponse
from django.utils import timezone

from account.models import User
from .models import AssessmentTemplate, PatientAssessment
from .forms import (
    AssessmentTemplateForm, PatientAssessmentForm, AssessmentFilterForm
)


class AssessmentPermissionMixin:
    """Permission checking for assessment views"""
    
    def check_assessment_permission(self, user, required_roles=None):
        if required_roles is None:
            required_roles = ['admin', 'doctor', 'therapist', 'nurse', 'case_manager']
        
        if user.role not in required_roles:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("您沒有權限執行此操作")


# ==================== Assessment Template Views ====================

class AssessmentTemplateListView(LoginRequiredMixin, ListView):
    """List all assessment templates"""
    model = AssessmentTemplate
    template_name = 'assessments/template_list.html'
    context_object_name = 'templates'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = AssessmentTemplate.objects.all()
        
        # Non-admin users only see active templates
        if self.request.user.role != 'admin':
            queryset = queryset.filter(status='active')
        
        # Filter by category
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        return queryset.annotate(
            usage_count=Count('responses')
        ).order_by('category', 'name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = AssessmentTemplate.CATEGORY_CHOICES
        context['selected_category'] = self.request.GET.get('category', '')
        context['can_manage'] = self.request.user.role == 'admin'
        return context


class AssessmentTemplateDetailView(LoginRequiredMixin, DetailView):
    """View assessment template details"""
    model = AssessmentTemplate
    template_name = 'assessments/template_detail.html'
    context_object_name = 'template'


class AssessmentTemplateCreateView(LoginRequiredMixin, AssessmentPermissionMixin, CreateView):
    """Create new assessment template (admin only)"""
    model = AssessmentTemplate
    form_class = AssessmentTemplateForm
    template_name = 'assessments/template_form.html'
    success_url = reverse_lazy('assessments:template_list')
    
    def dispatch(self, request, *args, **kwargs):
        self.check_assessment_permission(request.user, required_roles=['admin'])
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, '評估範本已建立')
        return super().form_valid(form)


class AssessmentTemplateUpdateView(LoginRequiredMixin, AssessmentPermissionMixin, UpdateView):
    """Update assessment template (admin only)"""
    model = AssessmentTemplate
    form_class = AssessmentTemplateForm
    template_name = 'assessments/template_form.html'
    success_url = reverse_lazy('assessments:template_list')
    
    def dispatch(self, request, *args, **kwargs):
        self.check_assessment_permission(request.user, required_roles=['admin'])
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        messages.success(self.request, '評估範本已更新')
        return super().form_valid(form)


# ==================== Patient Assessment Views ====================

class PatientAssessmentListView(LoginRequiredMixin, AssessmentPermissionMixin, ListView):
    """List patient assessments with filtering"""
    model = PatientAssessment
    template_name = 'assessments/assessment_list.html'
    context_object_name = 'assessments'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = PatientAssessment.objects.select_related(
            'patient', 'template', 'assessed_by'
        )
        
        # Role-based filtering
        user = self.request.user
        if user.role == 'patient':
            queryset = queryset.filter(patient=user)
        elif user.role == 'caregiver':
            # Caregivers see assessments for their assigned patients
            from clinical.models import PatientRecord
            patient_ids = PatientRecord.objects.filter(
                caregiver=user
            ).values_list('patient_id', flat=True)
            queryset = queryset.filter(patient_id__in=patient_ids)
        elif user.role == 'case_manager':
            # Case managers see assessments for their managed patients
            from clinical.models import PatientRecord
            patient_ids = PatientRecord.objects.filter(
                case_manager=user
            ).values_list('patient_id', flat=True)
            queryset = queryset.filter(patient_id__in=patient_ids)
        
        # URL parameter for specific patient
        patient_id = self.kwargs.get('patient_id')
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        
        # Apply filters from form
        form = AssessmentFilterForm(self.request.GET)
        if form.is_valid():
            if form.cleaned_data.get('patient'):
                queryset = queryset.filter(patient=form.cleaned_data['patient'])
            if form.cleaned_data.get('template'):
                queryset = queryset.filter(template=form.cleaned_data['template'])
            if form.cleaned_data.get('category'):
                queryset = queryset.filter(template__category=form.cleaned_data['category'])
            if form.cleaned_data.get('status'):
                queryset = queryset.filter(status=form.cleaned_data['status'])
            if form.cleaned_data.get('date_from'):
                queryset = queryset.filter(assessment_date__date__gte=form.cleaned_data['date_from'])
            if form.cleaned_data.get('date_to'):
                queryset = queryset.filter(assessment_date__date__lte=form.cleaned_data['date_to'])
        
        return queryset.order_by('-assessment_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = AssessmentFilterForm(self.request.GET)
        context['can_create'] = self.request.user.role in [
            'admin', 'doctor', 'therapist', 'nurse', 'case_manager'
        ]
        
        # If viewing specific patient
        patient_id = self.kwargs.get('patient_id')
        if patient_id:
            context['patient'] = get_object_or_404(User, pk=patient_id, role='patient')
        
        return context


class PatientAssessmentDetailView(LoginRequiredMixin, DetailView):
    """View assessment details"""
    model = PatientAssessment
    template_name = 'assessments/assessment_detail.html'
    context_object_name = 'assessment'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get previous assessments of same type for comparison
        assessment = self.object
        context['previous_assessments'] = PatientAssessment.objects.filter(
            patient=assessment.patient,
            template=assessment.template,
            status='completed',
            assessment_date__lt=assessment.assessment_date
        ).order_by('-assessment_date')[:5]
        
        return context


class PatientAssessmentCreateView(LoginRequiredMixin, AssessmentPermissionMixin, CreateView):
    """Create new patient assessment"""
    model = PatientAssessment
    form_class = PatientAssessmentForm
    template_name = 'assessments/assessment_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.check_assessment_permission(request.user)
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['patient_id'] = self.request.GET.get('patient')
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['templates'] = AssessmentTemplate.objects.filter(status='active')
        
        # Pre-selected patient
        patient_id = self.request.GET.get('patient')
        if patient_id:
            context['selected_patient'] = get_object_or_404(User, pk=patient_id, role='patient')
        
        return context
    
    def form_valid(self, form):
        form.instance.assessed_by = self.request.user
        messages.success(self.request, '評估已建立')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('assessments:assessment_detail', kwargs={'pk': self.object.pk})


class PatientAssessmentUpdateView(LoginRequiredMixin, AssessmentPermissionMixin, UpdateView):
    """Update patient assessment"""
    model = PatientAssessment
    form_class = PatientAssessmentForm
    template_name = 'assessments/assessment_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.check_assessment_permission(request.user)
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, '評估已更新')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('assessments:assessment_detail', kwargs={'pk': self.object.pk})


# ==================== API Views ====================

@login_required
def get_template_items(request, pk):
    """API: Get assessment template items for dynamic form rendering"""
    template = get_object_or_404(AssessmentTemplate, pk=pk)
    return JsonResponse({
        'id': template.id,
        'name': template.name,
        'code': template.code,
        'category': template.category,
        'max_score': template.max_score,
        'min_score': template.min_score,
        'higher_is_better': template.higher_is_better,
        'items': template.items,
        'score_interpretation': template.score_interpretation,
    })


@login_required
def patient_assessment_history(request, patient_id):
    """API: Get assessment history for a patient"""
    assessments = PatientAssessment.objects.filter(
        patient_id=patient_id,
        status='completed'
    ).select_related('template').order_by('-assessment_date')[:20]
    
    data = [{
        'id': a.id,
        'template_name': a.template.name,
        'template_code': a.template.code,
        'category': a.template.get_category_display(),
        'assessment_date': a.assessment_date.isoformat(),
        'total_score': float(a.total_score) if a.total_score else None,
        'interpretation': a.interpretation,
    } for a in assessments]
    
    return JsonResponse({'assessments': data})