from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q, Count, Prefetch
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta

from account.models import User
from .models import (
    PatientRecord, MedicalRecord, RehabPlan, RehabSession,
    VitalSigns, Medication, MedicationAdministration,
    NursingNote, CarePlan, CarePlanGoal, CareRecord,
    IncidentReport, Equipment, EquipmentReservation
)
from .forms import (
    PatientRecordForm, MedicalRecordForm, RehabPlanForm, RehabSessionForm,
    VitalSignsForm, MedicationForm, NursingNoteForm, CarePlanForm,
    CarePlanGoalForm, CareRecordForm, IncidentReportForm,
    EquipmentForm, EquipmentReservationForm, PatientFilterForm
)
from .permissions import ClinicalPermissionMixin


# ==================== Patient Management ====================

class PatientListView(LoginRequiredMixin, ClinicalPermissionMixin, ListView):
    """List all patients with role-based filtering"""
    model = User
    template_name = 'clinical/patient_list.html'
    context_object_name = 'patients'
    paginate_by = 20
    
    def get_queryset(self):
        self.check_permission(self.request.user, required_roles=[
            'admin', 'doctor', 'therapist', 'nurse', 'case_manager', 'caregiver'
        ])
        
        queryset = User.objects.filter(role='patient', is_active=True).select_related('patient_record')
        
        # Apply role-based filtering
        queryset = self.filter_patients_by_role(queryset, self.request.user)
        
        # Apply filters from form
        form = PatientFilterForm(self.request.GET)
        if form.is_valid():
            status = form.cleaned_data.get('status')
            case_manager = form.cleaned_data.get('case_manager')
            caregiver = form.cleaned_data.get('caregiver')
            search = form.cleaned_data.get('search')
            
            if status:
                queryset = queryset.filter(patient_record__status=status)
            if case_manager:
                queryset = queryset.filter(patient_record__case_manager=case_manager)
            if caregiver:
                queryset = queryset.filter(patient_record__caregiver=caregiver)
            if search:
                queryset = queryset.filter(
                    Q(first_name__icontains=search) |
                    Q(last_name__icontains=search) |
                    Q(username__icontains=search) |
                    Q(patient_record__medical_record_number__icontains=search)
                )
        
        return queryset.order_by('-patient_record__admission_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = PatientFilterForm(self.request.GET)
        context['can_create'] = self.request.user.role == 'admin'
        context['total_patients'] = self.get_queryset().count()
        return context


class PatientDetailView(LoginRequiredMixin, ClinicalPermissionMixin, DetailView):
    """Detailed view of a patient with all records"""
    model = User
    template_name = 'clinical/patient_detail.html'
    context_object_name = 'patient'
    
    def get_object(self):
        patient = super().get_object()
        
        # Check permission to view this patient
        if not self.can_view_patient(self.request.user, patient):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("您沒有權限查看此病患資料")
        
        return patient
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = self.object
        
        # Get patient record
        try:
            context['patient_record'] = patient.patient_record
        except PatientRecord.DoesNotExist:
            context['patient_record'] = None
        
        # Get recent medical records
        context['medical_records'] = MedicalRecord.objects.filter(
            patient=patient
        ).order_by('-record_date', '-record_time')[:5]
        
        # Get active rehab plans
        context['rehab_plans'] = RehabPlan.objects.filter(
            patient=patient,
            status='active'
        )
        
        # Get recent vital signs
        context['recent_vitals'] = VitalSigns.objects.filter(
            patient=patient
        ).order_by('-recorded_at')[:5]
        
        # Get active medications
        context['medications'] = Medication.objects.filter(
            patient=patient,
            status='active'
        )
        
        # Get recent nursing notes
        context['nursing_notes'] = NursingNote.objects.filter(
            patient=patient
        ).order_by('-note_datetime')[:5]
        
        # Get active care plans
        context['care_plans'] = CarePlan.objects.filter(
            patient=patient,
            status='active'
        ).prefetch_related('goals')
        
        # Get recent care records
        context['care_records'] = CareRecord.objects.filter(
            patient=patient
        ).order_by('-record_date', '-record_time')[:10]
        
        # Get recent incidents
        context['incidents'] = IncidentReport.objects.filter(
            patient=patient
        ).order_by('-incident_datetime')[:5]
        
        # Permissions
        context['can_edit'] = self.can_edit_patient_record(self.request.user, patient)
        context['can_add_medical_record'] = self.can_create_medical_record(self.request.user)
        context['can_add_rehab_plan'] = self.can_create_rehab_plan(self.request.user)
        context['can_record_vitals'] = self.can_record_vitals(self.request.user)
        context['can_manage_medication'] = self.can_manage_medication(self.request.user)
        context['can_add_nursing_note'] = self.can_create_nursing_note(self.request.user)
        context['can_manage_care_plan'] = self.can_manage_care_plan(self.request.user)
        context['can_add_care_record'] = self.can_create_care_record(self.request.user)
        context['can_report_incident'] = self.can_report_incident(self.request.user)
        
        return context


class PatientRecordCreateView(LoginRequiredMixin, ClinicalPermissionMixin, CreateView):
    """Create patient record"""
    model = PatientRecord
    form_class = PatientRecordForm
    template_name = 'clinical/patient_record_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.check_permission(request.user, required_roles=['admin'])
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        messages.success(self.request, '病患記錄已成功建立')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('clinical:patient_detail', kwargs={'pk': self.object.patient.pk})


class PatientRecordUpdateView(LoginRequiredMixin, ClinicalPermissionMixin, UpdateView):
    """Update patient record"""
    model = PatientRecord
    form_class = PatientRecordForm
    template_name = 'clinical/patient_record_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.check_permission(request.user, required_roles=['admin'])
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        messages.success(self.request, '病患記錄已成功更新')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('clinical:patient_detail', kwargs={'pk': self.object.patient.pk})


# ==================== Medical Records ====================

class MedicalRecordListView(LoginRequiredMixin, ClinicalPermissionMixin, ListView):
    """List medical records"""
    model = MedicalRecord
    template_name = 'clinical/medical_record_list.html'
    context_object_name = 'medical_records'
    paginate_by = 20
    
    def get_queryset(self):
        self.check_permission(self.request.user, required_roles=[
            'admin', 'doctor', 'therapist', 'nurse'
        ])
        
        queryset = MedicalRecord.objects.select_related('patient', 'practitioner')
        
        # Filter by patient if provided
        patient_id = self.kwargs.get('patient_id')
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        
        # Role-based filtering
        if self.request.user.role in ['doctor', 'therapist']:
            queryset = queryset.filter(practitioner=self.request.user)
        
        return queryset.order_by('-record_date', '-record_time')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_create'] = self.can_create_medical_record(self.request.user)
        
        patient_id = self.kwargs.get('patient_id')
        if patient_id:
            context['patient'] = get_object_or_404(User, pk=patient_id, role='patient')
        
        return context


class MedicalRecordCreateView(LoginRequiredMixin, ClinicalPermissionMixin, CreateView):
    """Create medical record"""
    model = MedicalRecord
    form_class = MedicalRecordForm
    template_name = 'clinical/medical_record_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not self.can_create_medical_record(request.user):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("您沒有權限建立診療記錄")
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.practitioner = self.request.user
        messages.success(self.request, '診療記錄已成功建立')
        return super().form_valid(form)
    
    def get_initial(self):
        initial = super().get_initial()
        patient_id = self.request.GET.get('patient_id')
        if patient_id:
            initial['patient'] = patient_id
        return initial
    
    def get_success_url(self):
        return reverse_lazy('clinical:patient_detail', kwargs={'pk': self.object.patient.pk})


# ==================== Medical Records (continued) ====================

class MedicalRecordDetailView(LoginRequiredMixin, ClinicalPermissionMixin, DetailView):
    """View detailed medical record"""
    model = MedicalRecord
    template_name = 'clinical/medical_record_detail.html'
    context_object_name = 'medical_record'
    
    def get_object(self):
        obj = super().get_object()
        # Check if user can view this patient's records
        if not self.can_view_patient(self.request.user, obj.patient):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("您沒有權限查看此記錄")
        return obj


class MedicalRecordUpdateView(LoginRequiredMixin, ClinicalPermissionMixin, UpdateView):
    """Update medical record"""
    model = MedicalRecord
    form_class = MedicalRecordForm
    template_name = 'clinical/medical_record_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        # Only practitioner who created it or admin can edit
        if request.user.role != 'admin' and obj.practitioner != request.user:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("只有建立者或管理員可以編輯此記錄")
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        messages.success(self.request, '診療記錄已成功更新')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('clinical:patient_detail', kwargs={'pk': self.object.patient.pk})


# ==================== Rehab Plans ====================

class RehabPlanListView(LoginRequiredMixin, ClinicalPermissionMixin, ListView):
    """List rehab plans"""
    model = RehabPlan
    template_name = 'clinical/rehab_plan_list.html'
    context_object_name = 'rehab_plans'
    paginate_by = 20
    
    def get_queryset(self):
        self.check_permission(self.request.user, required_roles=[
            'admin', 'therapist', 'nurse', 'case_manager'
        ])
        
        queryset = RehabPlan.objects.select_related('patient', 'therapist')
        
        # Filter by patient if provided
        patient_id = self.kwargs.get('patient_id')
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        
        # Role-based filtering
        if self.request.user.role == 'therapist':
            queryset = queryset.filter(therapist=self.request.user)
        
        return queryset.order_by('-start_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_create'] = self.can_create_rehab_plan(self.request.user)
        
        patient_id = self.kwargs.get('patient_id')
        if patient_id:
            context['patient'] = get_object_or_404(User, pk=patient_id, role='patient')
        
        return context


class RehabPlanCreateView(LoginRequiredMixin, ClinicalPermissionMixin, CreateView):
    """Create rehab plan"""
    model = RehabPlan
    form_class = RehabPlanForm
    template_name = 'clinical/rehab_plan_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not self.can_create_rehab_plan(request.user):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("您沒有權限建立復健計畫")
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.therapist = self.request.user
        messages.success(self.request, '復健計畫已成功建立')
        return super().form_valid(form)
    
    def get_initial(self):
        initial = super().get_initial()
        patient_id = self.request.GET.get('patient_id')
        if patient_id:
            initial['patient'] = patient_id
        return initial
    
    def get_success_url(self):
        return reverse_lazy('clinical:rehab_plan_detail', kwargs={'pk': self.object.pk})


class RehabPlanDetailView(LoginRequiredMixin, ClinicalPermissionMixin, DetailView):
    """View rehab plan with sessions"""
    model = RehabPlan
    template_name = 'clinical/rehab_plan_detail.html'
    context_object_name = 'rehab_plan'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get all sessions for this plan
        context['sessions'] = RehabSession.objects.filter(
            rehab_plan=self.object
        ).order_by('-session_date', '-session_time')
        
        context['can_edit'] = (self.request.user.role == 'admin' or 
                              self.object.therapist == self.request.user)
        context['can_add_session'] = self.can_create_rehab_plan(self.request.user)
        
        return context


class RehabPlanUpdateView(LoginRequiredMixin, ClinicalPermissionMixin, UpdateView):
    """Update rehab plan"""
    model = RehabPlan
    form_class = RehabPlanForm
    template_name = 'clinical/rehab_plan_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if request.user.role != 'admin' and obj.therapist != request.user:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("只有建立者或管理員可以編輯此計畫")
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        messages.success(self.request, '復健計畫已成功更新')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('clinical:rehab_plan_detail', kwargs={'pk': self.object.pk})


# ==================== Rehab Sessions ====================

class RehabSessionCreateView(LoginRequiredMixin, ClinicalPermissionMixin, CreateView):
    """Create rehab session"""
    model = RehabSession
    form_class = RehabSessionForm
    template_name = 'clinical/rehab_session_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.rehab_plan = get_object_or_404(RehabPlan, pk=self.kwargs['plan_id'])
        
        if not self.can_create_rehab_plan(request.user):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("您沒有權限記錄療程")
        
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.rehab_plan = self.rehab_plan
        messages.success(self.request, '療程記錄已成功建立')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rehab_plan'] = self.rehab_plan
        return context
    
    def get_success_url(self):
        return reverse_lazy('clinical:rehab_plan_detail', kwargs={'pk': self.rehab_plan.pk})


# ==================== Vital Signs ====================

class VitalSignsListView(LoginRequiredMixin, ClinicalPermissionMixin, ListView):
    """List vital signs"""
    model = VitalSigns
    template_name = 'clinical/vital_signs_list.html'
    context_object_name = 'vital_signs'
    paginate_by = 20
    
    def get_queryset(self):
        self.check_permission(self.request.user, required_roles=[
            'admin', 'nurse', 'doctor', 'caregiver'
        ])
        
        queryset = VitalSigns.objects.select_related('patient', 'recorded_by')
        
        # Filter by patient if provided
        patient_id = self.kwargs.get('patient_id')
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        
        return queryset.order_by('-recorded_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_create'] = self.can_record_vitals(self.request.user)
        
        patient_id = self.kwargs.get('patient_id')
        if patient_id:
            context['patient'] = get_object_or_404(User, pk=patient_id, role='patient')
        
        return context


class VitalSignsCreateView(LoginRequiredMixin, ClinicalPermissionMixin, CreateView):
    """Record vital signs"""
    model = VitalSigns
    form_class = VitalSignsForm
    template_name = 'clinical/vital_signs_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not self.can_record_vitals(request.user):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("您沒有權限記錄生命徵象")
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.recorded_by = self.request.user
        messages.success(self.request, '生命徵象已成功記錄')
        return super().form_valid(form)
    
    def get_initial(self):
        initial = super().get_initial()
        patient_id = self.request.GET.get('patient_id')
        if patient_id:
            initial['patient'] = patient_id
        initial['recorded_at'] = timezone.now().strftime('%Y-%m-%dT%H:%M')
        return initial
    
    def get_success_url(self):
        return reverse_lazy('clinical:patient_detail', kwargs={'pk': self.object.patient.pk})


# ==================== Medications ====================

class MedicationListView(LoginRequiredMixin, ClinicalPermissionMixin, ListView):
    """List medications"""
    model = Medication
    template_name = 'clinical/medication_list.html'
    context_object_name = 'medications'
    paginate_by = 20
    
    def get_queryset(self):
        self.check_permission(self.request.user, required_roles=[
            'admin', 'doctor', 'nurse'
        ])
        
        queryset = Medication.objects.select_related('patient', 'prescribed_by')
        
        # Filter by patient if provided
        patient_id = self.kwargs.get('patient_id')
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        
        return queryset.order_by('-start_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_create'] = self.can_manage_medication(self.request.user)
        
        patient_id = self.kwargs.get('patient_id')
        if patient_id:
            context['patient'] = get_object_or_404(User, pk=patient_id, role='patient')
        
        return context


class MedicationCreateView(LoginRequiredMixin, ClinicalPermissionMixin, CreateView):
    """Create medication order"""
    model = Medication
    form_class = MedicationForm
    template_name = 'clinical/medication_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not self.can_manage_medication(request.user):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("您沒有權限開立藥物")
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.prescribed_by = self.request.user
        messages.success(self.request, '藥物已成功開立')
        return super().form_valid(form)
    
    def get_initial(self):
        initial = super().get_initial()
        patient_id = self.request.GET.get('patient_id')
        if patient_id:
            initial['patient'] = patient_id
        return initial
    
    def get_success_url(self):
        return reverse_lazy('clinical:patient_detail', kwargs={'pk': self.object.patient.pk})


class MedicationUpdateView(LoginRequiredMixin, ClinicalPermissionMixin, UpdateView):
    """Update medication"""
    model = Medication
    form_class = MedicationForm
    template_name = 'clinical/medication_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not self.can_manage_medication(request.user):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("您沒有權限修改藥物")
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        messages.success(self.request, '藥物已成功更新')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('clinical:patient_detail', kwargs={'pk': self.object.patient.pk})


# ==================== Nursing Notes ====================

class NursingNoteListView(LoginRequiredMixin, ClinicalPermissionMixin, ListView):
    """List nursing notes"""
    model = NursingNote
    template_name = 'clinical/nursing_note_list.html'
    context_object_name = 'nursing_notes'
    paginate_by = 20
    
    def get_queryset(self):
        self.check_permission(self.request.user, required_roles=[
            'admin', 'nurse', 'doctor'
        ])
        
        queryset = NursingNote.objects.select_related('patient', 'nurse')
        
        # Filter by patient if provided
        patient_id = self.kwargs.get('patient_id')
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        
        return queryset.order_by('-note_datetime')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_create'] = self.can_create_nursing_note(self.request.user)
        
        patient_id = self.kwargs.get('patient_id')
        if patient_id:
            context['patient'] = get_object_or_404(User, pk=patient_id, role='patient')
        
        return context


class NursingNoteCreateView(LoginRequiredMixin, ClinicalPermissionMixin, CreateView):
    """Create nursing note"""
    model = NursingNote
    form_class = NursingNoteForm
    template_name = 'clinical/nursing_note_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not self.can_create_nursing_note(request.user):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("您沒有權限建立護理紀錄")
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.nurse = self.request.user
        messages.success(self.request, '護理紀錄已成功建立')
        return super().form_valid(form)
    
    def get_initial(self):
        initial = super().get_initial()
        patient_id = self.request.GET.get('patient_id')
        if patient_id:
            initial['patient'] = patient_id
        initial['note_datetime'] = timezone.now().strftime('%Y-%m-%dT%H:%M')
        return initial
    
    def get_success_url(self):
        return reverse_lazy('clinical:patient_detail', kwargs={'pk': self.object.patient.pk})


# ==================== Care Plans (Case Manager) ====================

class CarePlanListView(LoginRequiredMixin, ClinicalPermissionMixin, ListView):
    """List care plans"""
    model = CarePlan
    template_name = 'clinical/care_plan_list.html'
    context_object_name = 'care_plans'
    paginate_by = 20
    
    def get_queryset(self):
        self.check_permission(self.request.user, required_roles=[
            'admin', 'case_manager', 'nurse'
        ])
        
        queryset = CarePlan.objects.select_related('patient', 'case_manager').prefetch_related('goals')
        
        # Filter by patient if provided
        patient_id = self.kwargs.get('patient_id')
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        
        # Role-based filtering
        if self.request.user.role == 'case_manager':
            queryset = queryset.filter(case_manager=self.request.user)
        
        return queryset.order_by('-period_start')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_create'] = self.can_manage_care_plan(self.request.user)
        
        patient_id = self.kwargs.get('patient_id')
        if patient_id:
            context['patient'] = get_object_or_404(User, pk=patient_id, role='patient')
        
        return context


class CarePlanCreateView(LoginRequiredMixin, ClinicalPermissionMixin, CreateView):
    """Create care plan"""
    model = CarePlan
    form_class = CarePlanForm
    template_name = 'clinical/care_plan_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not self.can_manage_care_plan(request.user):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("您沒有權限建立照護計畫")
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.case_manager = self.request.user
        messages.success(self.request, '照護計畫已成功建立')
        return super().form_valid(form)
    
    def get_initial(self):
        initial = super().get_initial()
        patient_id = self.request.GET.get('patient_id')
        if patient_id:
            initial['patient'] = patient_id
        return initial
    
    def get_success_url(self):
        return reverse_lazy('clinical:care_plan_detail', kwargs={'pk': self.object.pk})


class CarePlanDetailView(LoginRequiredMixin, ClinicalPermissionMixin, DetailView):
    """View care plan with goals"""
    model = CarePlan
    template_name = 'clinical/care_plan_detail.html'
    context_object_name = 'care_plan'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['goals'] = self.object.goals.all().order_by('priority', 'target_date')
        context['can_edit'] = (self.request.user.role == 'admin' or 
                              self.object.case_manager == self.request.user)
        context['can_add_goal'] = self.can_manage_care_plan(self.request.user)
        return context


class CarePlanUpdateView(LoginRequiredMixin, ClinicalPermissionMixin, UpdateView):
    """Update care plan"""
    model = CarePlan
    form_class = CarePlanForm
    template_name = 'clinical/care_plan_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if request.user.role != 'admin' and obj.case_manager != request.user:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("只有建立者或管理員可以編輯此計畫")
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        messages.success(self.request, '照護計畫已成功更新')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('clinical:care_plan_detail', kwargs={'pk': self.object.pk})


# ==================== Care Plan Goals ====================

class CarePlanGoalCreateView(LoginRequiredMixin, ClinicalPermissionMixin, CreateView):
    """Add goal to care plan"""
    model = CarePlanGoal
    form_class = CarePlanGoalForm
    template_name = 'clinical/care_plan_goal_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.care_plan = get_object_or_404(CarePlan, pk=self.kwargs['plan_id'])
        
        if not self.can_manage_care_plan(request.user):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("您沒有權限新增目標")
        
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.care_plan = self.care_plan
        messages.success(self.request, '目標已成功新增')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['care_plan'] = self.care_plan
        return context
    
    def get_success_url(self):
        return reverse_lazy('clinical:care_plan_detail', kwargs={'pk': self.care_plan.pk})


class CarePlanGoalUpdateView(LoginRequiredMixin, ClinicalPermissionMixin, UpdateView):
    """Update care plan goal"""
    model = CarePlanGoal
    form_class = CarePlanGoalForm
    template_name = 'clinical/care_plan_goal_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not self.can_manage_care_plan(request.user):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("您沒有權限編輯目標")
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        messages.success(self.request, '目標已成功更新')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('clinical:care_plan_detail', kwargs={'pk': self.object.care_plan.pk})


# ==================== Care Records (Caregiver) ====================

class CareRecordListView(LoginRequiredMixin, ClinicalPermissionMixin, ListView):
    """List care records"""
    model = CareRecord
    template_name = 'clinical/care_record_list.html'
    context_object_name = 'care_records'
    paginate_by = 20
    
    def get_queryset(self):
        self.check_permission(self.request.user, required_roles=[
            'admin', 'caregiver', 'case_manager', 'nurse'
        ])
        
        queryset = CareRecord.objects.select_related('patient', 'caregiver')
        
        # Filter by patient if provided
        patient_id = self.kwargs.get('patient_id')
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        
        # Role-based filtering
        if self.request.user.role == 'caregiver':
            queryset = queryset.filter(caregiver=self.request.user)
        
        return queryset.order_by('-record_date', '-record_time')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_create'] = self.can_create_care_record(self.request.user)
        
        patient_id = self.kwargs.get('patient_id')
        if patient_id:
            context['patient'] = get_object_or_404(User, pk=patient_id, role='patient')
        
        return context


class CareRecordCreateView(LoginRequiredMixin, ClinicalPermissionMixin, CreateView):
    """Create care record"""
    model = CareRecord
    form_class = CareRecordForm
    template_name = 'clinical/care_record_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not self.can_create_care_record(request.user):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("您沒有權限建立照護記錄")
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.caregiver = self.request.user
        messages.success(self.request, '照護記錄已成功建立')
        return super().form_valid(form)
    
    def get_initial(self):
        initial = super().get_initial()
        patient_id = self.request.GET.get('patient_id')
        if patient_id:
            initial['patient'] = patient_id
        initial['record_date'] = timezone.now().date()
        initial['record_time'] = timezone.now().time()
        return initial
    
    def get_success_url(self):
        return reverse_lazy('clinical:patient_detail', kwargs={'pk': self.object.patient.pk})


# ==================== Incident Reports ====================

class IncidentReportListView(LoginRequiredMixin, ClinicalPermissionMixin, ListView):
    """List incident reports"""
    model = IncidentReport
    template_name = 'clinical/incident_report_list.html'
    context_object_name = 'incidents'
    paginate_by = 20
    
    def get_queryset(self):
        self.check_permission(self.request.user, required_roles=[
            'admin', 'doctor', 'nurse', 'case_manager', 'caregiver', 'therapist'
        ])
        
        queryset = IncidentReport.objects.select_related('patient', 'reported_by')
        
        # Filter by patient if provided
        patient_id = self.kwargs.get('patient_id')
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        
        # Role-based filtering
        if self.request.user.role == 'caregiver':
            # Caregivers see incidents they reported or for their patients
            queryset = queryset.filter(
                Q(reported_by=self.request.user) |
                Q(patient__patient_record__caregiver=self.request.user)
            )
        elif self.request.user.role == 'case_manager':
            # Case managers see incidents for their patients
            queryset = queryset.filter(patient__patient_record__case_manager=self.request.user)
        
        return queryset.order_by('-incident_datetime')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_create'] = self.can_report_incident(self.request.user)
        
        patient_id = self.kwargs.get('patient_id')
        if patient_id:
            context['patient'] = get_object_or_404(User, pk=patient_id, role='patient')
        
        return context


class IncidentReportCreateView(LoginRequiredMixin, ClinicalPermissionMixin, CreateView):
    """Create incident report"""
    model = IncidentReport
    form_class = IncidentReportForm
    template_name = 'clinical/incident_report_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not self.can_report_incident(request.user):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("您沒有權限通報事件")
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.reported_by = self.request.user
        messages.success(self.request, '異常事件已成功通報')
        return super().form_valid(form)
    
    def get_initial(self):
        initial = super().get_initial()
        patient_id = self.request.GET.get('patient_id')
        if patient_id:
            initial['patient'] = patient_id
        initial['incident_datetime'] = timezone.now().strftime('%Y-%m-%dT%H:%M')
        return initial
    
    def get_success_url(self):
        return reverse_lazy('clinical:incident_report_list')


class IncidentReportDetailView(LoginRequiredMixin, ClinicalPermissionMixin, DetailView):
    """View incident report details"""
    model = IncidentReport
    template_name = 'clinical/incident_report_detail.html'
    context_object_name = 'incident'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_update'] = (self.request.user.role in ['admin', 'nurse', 'case_manager'])
        return context


class IncidentReportUpdateView(LoginRequiredMixin, ClinicalPermissionMixin, UpdateView):
    """Update incident report (follow-up)"""
    model = IncidentReport
    form_class = IncidentReportForm
    template_name = 'clinical/incident_report_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.role not in ['admin', 'nurse', 'case_manager']:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("只有管理員、護理師或個管師可以更新事件報告")
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        messages.success(self.request, '事件報告已成功更新')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('clinical:incident_report_detail', kwargs={'pk': self.object.pk})


# ==================== Equipment Management ====================

class EquipmentListView(LoginRequiredMixin, ClinicalPermissionMixin, ListView):
    """List equipment"""
    model = Equipment
    template_name = 'clinical/equipment_list.html'
    context_object_name = 'equipment_list'
    paginate_by = 20
    
    def get_queryset(self):
        self.check_permission(self.request.user, required_roles=[
            'admin', 'therapist', 'nurse'
        ])
        
        queryset = Equipment.objects.all()
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by type
        equipment_type = self.request.GET.get('type')
        if equipment_type:
            queryset = queryset.filter(equipment_type=equipment_type)
        
        return queryset.order_by('equipment_name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_create'] = self.can_manage_equipment(self.request.user)
        context['status_choices'] = Equipment.STATUS_CHOICES
        context['type_choices'] = Equipment.EQUIPMENT_TYPE_CHOICES
        return context


class EquipmentCreateView(LoginRequiredMixin, ClinicalPermissionMixin, CreateView):
    """Create equipment"""
    model = Equipment
    form_class = EquipmentForm
    template_name = 'clinical/equipment_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not self.can_manage_equipment(request.user):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("您沒有權限管理設備")
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        messages.success(self.request, '設備已成功建立')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('clinical:equipment_list')


class EquipmentUpdateView(LoginRequiredMixin, ClinicalPermissionMixin, UpdateView):
    """Update equipment"""
    model = Equipment
    form_class = EquipmentForm
    template_name = 'clinical/equipment_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not self.can_manage_equipment(request.user):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("您沒有權限管理設備")
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        messages.success(self.request, '設備已成功更新')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('clinical:equipment_list')


class EquipmentDetailView(LoginRequiredMixin, ClinicalPermissionMixin, DetailView):
    """View equipment details and reservations"""
    model = Equipment
    template_name = 'clinical/equipment_detail.html'
    context_object_name = 'equipment'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get upcoming reservations
        context['reservations'] = EquipmentReservation.objects.filter(
            equipment=self.object,
            reservation_date__gte=timezone.now().date(),
            status__in=['pending', 'confirmed', 'in_use']
        ).order_by('reservation_date', 'start_time')
        
        context['can_edit'] = self.can_manage_equipment(self.request.user)
        return context


# ==================== Equipment Reservations ====================

class EquipmentReservationListView(LoginRequiredMixin, ClinicalPermissionMixin, ListView):
    """List equipment reservations"""
    model = EquipmentReservation
    template_name = 'clinical/equipment_reservation_list.html'
    context_object_name = 'reservations'
    paginate_by = 20
    
    def get_queryset(self):
        self.check_permission(self.request.user, required_roles=[
            'admin', 'therapist', 'nurse'
        ])
        
        queryset = EquipmentReservation.objects.select_related(
            'equipment', 'reserved_by', 'patient'
        )
        
        # Filter by equipment if provided
        equipment_id = self.kwargs.get('equipment_id')
        if equipment_id:
            queryset = queryset.filter(equipment_id=equipment_id)
        
        # Role-based filtering
        if self.request.user.role == 'therapist':
            queryset = queryset.filter(reserved_by=self.request.user)
        
        return queryset.order_by('-reservation_date', '-start_time')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_create'] = self.can_manage_equipment(self.request.user)
        
        equipment_id = self.kwargs.get('equipment_id')
        if equipment_id:
            context['equipment'] = get_object_or_404(Equipment, pk=equipment_id)
        
        return context


class EquipmentReservationCreateView(LoginRequiredMixin, ClinicalPermissionMixin, CreateView):
    """Create equipment reservation"""
    model = EquipmentReservation
    form_class = EquipmentReservationForm
    template_name = 'clinical/equipment_reservation_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not self.can_manage_equipment(request.user):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("您沒有權限預約設備")
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.reserved_by = self.request.user
        messages.success(self.request, '設備已成功預約')
        return super().form_valid(form)
    
    def get_initial(self):
        initial = super().get_initial()
        equipment_id = self.request.GET.get('equipment_id')
        if equipment_id:
            initial['equipment'] = equipment_id
        return initial
    
    def get_success_url(self):
        return reverse_lazy('clinical:equipment_reservation_list')


class EquipmentReservationUpdateView(LoginRequiredMixin, ClinicalPermissionMixin, UpdateView):
    """Update equipment reservation"""
    model = EquipmentReservation
    form_class = EquipmentReservationForm
    template_name = 'clinical/equipment_reservation_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if request.user.role != 'admin' and obj.reserved_by != request.user:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("只有預約者或管理員可以編輯預約")
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        messages.success(self.request, '預約已成功更新')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('clinical:equipment_reservation_list')


# ==================== Dashboard Views ====================

@login_required
def clinical_dashboard(request):
    """Clinical management dashboard"""
    context = {
        'title': '臨床管理',
    }
    
    if request.user.role == 'admin':
        # Admin sees all statistics
        context['total_patients'] = User.objects.filter(role='patient', is_active=True).count()
        context['active_rehab_plans'] = RehabPlan.objects.filter(status='active').count()
        context['pending_incidents'] = IncidentReport.objects.filter(status='reported').count()
        context['recent_incidents'] = IncidentReport.objects.select_related('patient', 'reported_by').order_by('-incident_datetime')[:5]
        
    elif request.user.role == 'case_manager':
        # Case manager sees their patients
        patients = User.objects.filter(
            role='patient',
            patient_record__case_manager=request.user
        )
        context['my_patients'] = patients
        context['active_care_plans'] = CarePlan.objects.filter(
            case_manager=request.user,
            status='active'
        ).count()
        
    elif request.user.role == 'caregiver':
        # Caregiver sees their patients
        patients = User.objects.filter(
            role='patient',
            patient_record__caregiver=request.user
        )
        context['my_patients'] = patients
        context['today_care_records'] = CareRecord.objects.filter(
            caregiver=request.user,
            record_date=timezone.now().date()
        ).count()
    
    return render(request, 'clinical/dashboard.html', context)