from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.urls import reverse


class ReturnURLMixin:
    """
    Mixin to handle return URL logic for forms
    Allows forms to redirect back to the referring page
    """
    
    def get_return_url(self):
        """Get the URL to return to after form submission"""
        # Check for 'next' parameter in POST or GET
        next_url = self.request.POST.get('next') or self.request.GET.get('next')
        
        if next_url:
            return next_url
        
        # Check HTTP_REFERER
        referer = self.request.META.get('HTTP_REFERER')
        if referer:
            # Only use referer if it's from the same domain
            request_host = self.request.get_host()
            if request_host in referer:
                return referer
        
        # Default fallback
        return self.get_default_return_url()
    
    def get_default_return_url(self):
        """Override this to provide a default return URL"""
        return reverse('clinical:patient_list')
    
    def get_success_url(self):
        """Override get_success_url to use return URL logic"""
        return self.get_return_url()
    
    def get_context_data(self, **kwargs):
        """Add return URL to context for use in templates"""
        context = super().get_context_data(**kwargs)
        
        # Get return URL from GET parameter or referer
        next_url = self.request.GET.get('next')
        if not next_url:
            referer = self.request.META.get('HTTP_REFERER')
            if referer and self.request.get_host() in referer:
                next_url = referer
        
        # If we have patient_id in GET, build patient detail URL as fallback
        if not next_url:
            patient_id = self.request.GET.get('patient_id')
            if patient_id:
                try:
                    next_url = reverse('clinical:patient_detail', kwargs={'pk': patient_id})
                except:
                    pass
        
        context['return_url'] = next_url or self.get_default_return_url()
        return context


class ClinicalPermissionMixin:
    """Mixin for role-based permissions in clinical views"""
    
    def check_permission(self, user, required_roles=None):
        """Check if user has required role"""
        if not user.is_authenticated:
            raise PermissionDenied("請先登入")
        
        if required_roles and user.role not in required_roles:
            raise PermissionDenied("您沒有權限訪問此頁面")
        
        return True
    
    def filter_patients_by_role(self, queryset, user):
        """
        Filter patient queryset based on user role
        Admin: See all patients
        Doctor/Therapist/Nurse: See patients with appointments or assigned
        CaseManager: See assigned cases
        Caregiver: See assigned patients
        """
        if user.role == 'admin':
            return queryset
        
        elif user.role in ['doctor', 'therapist']:
            # See patients they have appointments with
            return queryset.filter(
                Q(patient_appointments__practitioner=user) |
                Q(patient_record__case_manager=user)
            ).distinct()
        
        elif user.role == 'nurse':
            # Nurses can see all active patients
            return queryset.filter(is_active=True, role='patient')
        
        elif user.role == 'case_manager':
            # See assigned cases
            return queryset.filter(
                patient_record__case_manager=user,
                patient_record__status='active'
            ).distinct()
        
        elif user.role == 'caregiver':
            # See assigned patients
            return queryset.filter(
                patient_record__caregiver=user,
                patient_record__status='active'
            ).distinct()
        
        else:
            return queryset.none()
    
    def can_view_patient(self, user, patient):
        """Check if user can view specific patient"""
        if user.role == 'admin':
            return True
        
        if user.role in ['doctor', 'therapist']:
            # Check if they have appointments with this patient
            from appointments.models import Appointment
            has_appointment = Appointment.objects.filter(
                practitioner=user,
                patient=patient
            ).exists()
            
            # Check if assigned as case manager
            has_assignment = hasattr(patient, 'patient_record') and \
                           patient.patient_record.case_manager == user
            
            return has_appointment or has_assignment
        
        if user.role == 'nurse':
            return patient.role == 'patient' and patient.is_active
        
        if user.role == 'case_manager':
            return hasattr(patient, 'patient_record') and \
                   patient.patient_record.case_manager == user
        
        if user.role == 'caregiver':
            return hasattr(patient, 'patient_record') and \
                   patient.patient_record.caregiver == user
        
        return False
    
    def can_edit_patient_record(self, user, patient):
        """Check if user can edit patient record"""
        if user.role == 'admin':
            return True
        
        # Only admin can edit patient records
        return False
    
    def can_create_medical_record(self, user):
        """Check if user can create medical records"""
        return user.role in ['admin', 'doctor', 'therapist']
    
    def can_create_rehab_plan(self, user):
        """Check if user can create rehab plans"""
        return user.role in ['admin', 'therapist']
    
    def can_record_vitals(self, user):
        """Check if user can record vital signs"""
        return user.role in ['admin', 'nurse', 'caregiver']
    
    def can_manage_medication(self, user):
        """Check if user can manage medications"""
        return user.role in ['admin', 'doctor', 'nurse']
    
    def can_create_nursing_note(self, user):
        """Check if user can create nursing notes"""
        return user.role in ['admin', 'nurse']
    
    def can_manage_care_plan(self, user):
        """Check if user can manage care plans"""
        return user.role in ['admin', 'case_manager']
    
    def can_create_care_record(self, user):
        """Check if user can create care records"""
        return user.role in ['admin', 'caregiver']
    
    def can_report_incident(self, user):
        """Check if user can report incidents"""
        # All staff can report incidents
        return user.role in ['admin', 'doctor', 'therapist', 'nurse', 'case_manager', 'caregiver']
    
    def can_manage_equipment(self, user):
        """Check if user can manage equipment"""
        return user.role in ['admin', 'therapist']