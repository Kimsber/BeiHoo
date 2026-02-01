from django.contrib import admin
from .models import (
    PatientRecord, MedicalRecord, RehabPlan, RehabSession,
    VitalSigns, Medication, MedicationAdministration,
    NursingNote, CarePlan, CarePlanGoal, CareRecord,
    IncidentReport, Equipment, EquipmentReservation
)


@admin.register(PatientRecord)
class PatientRecordAdmin(admin.ModelAdmin):
    list_display = ['patient', 'medical_record_number', 'primary_diagnosis', 'admission_date', 'status']
    list_filter = ['status', 'admission_date']
    search_fields = ['patient__username', 'medical_record_number', 'primary_diagnosis']
    date_hierarchy = 'admission_date'


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ['patient', 'record_date', 'record_type', 'practitioner']
    list_filter = ['record_type', 'record_date']
    search_fields = ['patient__username', 'chief_complaint', 'diagnosis']
    date_hierarchy = 'record_date'


@admin.register(RehabPlan)
class RehabPlanAdmin(admin.ModelAdmin):
    list_display = ['patient', 'therapist', 'plan_name', 'start_date', 'status']
    list_filter = ['status', 'start_date']
    search_fields = ['patient__username', 'plan_name']


@admin.register(RehabSession)
class RehabSessionAdmin(admin.ModelAdmin):
    list_display = ['rehab_plan', 'session_date', 'duration_minutes', 'robot_used', 'completed']
    list_filter = ['completed', 'robot_used', 'session_date']


@admin.register(VitalSigns)
class VitalSignsAdmin(admin.ModelAdmin):
    list_display = ['patient', 'recorded_at', 'blood_pressure', 'heart_rate', 'temperature', 'recorded_by']
    list_filter = ['recorded_at']
    search_fields = ['patient__username']
    date_hierarchy = 'recorded_at'


@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = ['patient', 'medication_name', 'dosage', 'frequency', 'start_date', 'status']
    list_filter = ['status', 'frequency']
    search_fields = ['patient__username', 'medication_name']


@admin.register(MedicationAdministration)
class MedicationAdministrationAdmin(admin.ModelAdmin):
    list_display = ['medication', 'scheduled_time', 'administered_time', 'administered_by', 'status']
    list_filter = ['status', 'scheduled_time']


@admin.register(NursingNote)
class NursingNoteAdmin(admin.ModelAdmin):
    list_display = ['patient', 'note_datetime', 'nurse', 'note_type']
    list_filter = ['note_type', 'note_datetime']
    search_fields = ['patient__username', 'assessment']
    date_hierarchy = 'note_datetime'


@admin.register(CarePlan)
class CarePlanAdmin(admin.ModelAdmin):
    list_display = ['patient', 'case_manager', 'title', 'period_start', 'status']
    list_filter = ['status', 'period_start']
    search_fields = ['patient__username', 'title']


@admin.register(CarePlanGoal)
class CarePlanGoalAdmin(admin.ModelAdmin):
    list_display = ['care_plan', 'description', 'target_date', 'achievement_status']
    list_filter = ['achievement_status', 'target_date']


@admin.register(CareRecord)
class CareRecordAdmin(admin.ModelAdmin):
    list_display = ['patient', 'caregiver', 'record_date', 'activity_type']
    list_filter = ['activity_type', 'record_date']
    search_fields = ['patient__username']
    date_hierarchy = 'record_date'


@admin.register(IncidentReport)
class IncidentReportAdmin(admin.ModelAdmin):
    list_display = ['patient', 'incident_datetime', 'incident_type', 'severity', 'status']
    list_filter = ['incident_type', 'severity', 'status', 'incident_datetime']
    search_fields = ['patient__username', 'description']
    date_hierarchy = 'incident_datetime'


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['equipment_name', 'equipment_type', 'serial_number', 'status', 'location']
    list_filter = ['equipment_type', 'status']
    search_fields = ['equipment_name', 'serial_number']


@admin.register(EquipmentReservation)
class EquipmentReservationAdmin(admin.ModelAdmin):
    list_display = ['equipment', 'reserved_by', 'patient', 'reservation_date', 'start_time', 'status']
    list_filter = ['status', 'reservation_date']
    search_fields = ['equipment__equipment_name', 'patient__username']
    date_hierarchy = 'reservation_date'