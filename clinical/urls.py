from django.urls import path
from . import views

app_name = 'clinical'

urlpatterns = [
    # Dashboard
    path('', views.clinical_dashboard, name='dashboard'),
    
    # ==================== Patient Management ====================
    path('patients/', views.PatientListView.as_view(), name='patient_list'),
    path('patients/<int:pk>/', views.PatientDetailView.as_view(), name='patient_detail'),
    path('patients/record/create/', views.PatientRecordCreateView.as_view(), name='patient_record_create'),
    path('patients/record/<int:pk>/edit/', views.PatientRecordUpdateView.as_view(), name='patient_record_edit'),
    
    # ==================== Medical Records ====================
    path('medical-records/', views.MedicalRecordListView.as_view(), name='medical_record_list'),
    path('medical-records/patient/<int:patient_id>/', views.MedicalRecordListView.as_view(), name='medical_record_list_by_patient'),
    path('medical-records/<int:pk>/', views.MedicalRecordDetailView.as_view(), name='medical_record_detail'),
    path('medical-records/create/', views.MedicalRecordCreateView.as_view(), name='medical_record_create'),
    path('medical-records/<int:pk>/edit/', views.MedicalRecordUpdateView.as_view(), name='medical_record_edit'),
    
    # ==================== Rehab Plans ====================
    path('rehab-plans/', views.RehabPlanListView.as_view(), name='rehab_plan_list'),
    path('rehab-plans/patient/<int:patient_id>/', views.RehabPlanListView.as_view(), name='rehab_plan_list_by_patient'),
    path('rehab-plans/<int:pk>/', views.RehabPlanDetailView.as_view(), name='rehab_plan_detail'),
    path('rehab-plans/create/', views.RehabPlanCreateView.as_view(), name='rehab_plan_create'),
    path('rehab-plans/<int:pk>/edit/', views.RehabPlanUpdateView.as_view(), name='rehab_plan_edit'),
    
    # Rehab Sessions
    path('rehab-plans/<int:plan_id>/sessions/create/', views.RehabSessionCreateView.as_view(), name='rehab_session_create'),
    
    # ==================== Vital Signs ====================
    path('vital-signs/', views.VitalSignsListView.as_view(), name='vital_signs_list'),
    path('vital-signs/patient/<int:patient_id>/', views.VitalSignsListView.as_view(), name='vital_signs_list_by_patient'),
    path('vital-signs/create/', views.VitalSignsCreateView.as_view(), name='vital_signs_create'),
    
    # ==================== Medications ====================
    path('medications/', views.MedicationListView.as_view(), name='medication_list'),
    path('medications/patient/<int:patient_id>/', views.MedicationListView.as_view(), name='medication_list_by_patient'),
    path('medications/create/', views.MedicationCreateView.as_view(), name='medication_create'),
    path('medications/<int:pk>/edit/', views.MedicationUpdateView.as_view(), name='medication_edit'),
    
    # ==================== Nursing Notes ====================
    path('nursing-notes/', views.NursingNoteListView.as_view(), name='nursing_note_list'),
    path('nursing-notes/patient/<int:patient_id>/', views.NursingNoteListView.as_view(), name='nursing_note_list_by_patient'),
    path('nursing-notes/create/', views.NursingNoteCreateView.as_view(), name='nursing_note_create'),
    
    # ==================== Care Plans (Case Manager) ====================
    path('care-plans/', views.CarePlanListView.as_view(), name='care_plan_list'),
    path('care-plans/patient/<int:patient_id>/', views.CarePlanListView.as_view(), name='care_plan_list_by_patient'),
    path('care-plans/<int:pk>/', views.CarePlanDetailView.as_view(), name='care_plan_detail'),
    path('care-plans/create/', views.CarePlanCreateView.as_view(), name='care_plan_create'),
    path('care-plans/<int:pk>/edit/', views.CarePlanUpdateView.as_view(), name='care_plan_edit'),
    
    # Care Plan Goals
    path('care-plans/<int:plan_id>/goals/create/', views.CarePlanGoalCreateView.as_view(), name='care_plan_goal_create'),
    path('care-plan-goals/<int:pk>/edit/', views.CarePlanGoalUpdateView.as_view(), name='care_plan_goal_edit'),
    
    # ==================== Care Records (Caregiver) ====================
    path('care-records/', views.CareRecordListView.as_view(), name='care_record_list'),
    path('care-records/patient/<int:patient_id>/', views.CareRecordListView.as_view(), name='care_record_list_by_patient'),
    path('care-records/create/', views.CareRecordCreateView.as_view(), name='care_record_create'),
    
    # ==================== Incident Reports ====================
    path('incidents/', views.IncidentReportListView.as_view(), name='incident_report_list'),
    path('incidents/patient/<int:patient_id>/', views.IncidentReportListView.as_view(), name='incident_report_list_by_patient'),
    path('incidents/<int:pk>/', views.IncidentReportDetailView.as_view(), name='incident_report_detail'),
    path('incidents/create/', views.IncidentReportCreateView.as_view(), name='incident_report_create'),
    path('incidents/<int:pk>/edit/', views.IncidentReportUpdateView.as_view(), name='incident_report_edit'),
    
    # ==================== Equipment Management ====================
    path('equipment/', views.EquipmentListView.as_view(), name='equipment_list'),
    path('equipment/<int:pk>/', views.EquipmentDetailView.as_view(), name='equipment_detail'),
    path('equipment/create/', views.EquipmentCreateView.as_view(), name='equipment_create'),
    path('equipment/<int:pk>/edit/', views.EquipmentUpdateView.as_view(), name='equipment_edit'),
    
    # Equipment Reservations
    path('equipment-reservations/', views.EquipmentReservationListView.as_view(), name='equipment_reservation_list'),
    path('equipment/<int:equipment_id>/reservations/', views.EquipmentReservationListView.as_view(), name='equipment_reservation_list_by_equipment'),
    path('equipment-reservations/create/', views.EquipmentReservationCreateView.as_view(), name='equipment_reservation_create'),
    path('equipment-reservations/<int:pk>/edit/', views.EquipmentReservationUpdateView.as_view(), name='equipment_reservation_edit'),
]