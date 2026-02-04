from django.urls import path
from . import views

app_name = 'assessments'

urlpatterns = [
    # ==================== Assessment Templates ====================
    path('templates/', views.AssessmentTemplateListView.as_view(), name='template_list'),
    path('templates/<int:pk>/', views.AssessmentTemplateDetailView.as_view(), name='template_detail'),
    path('templates/create/', views.AssessmentTemplateCreateView.as_view(), name='template_create'),
    path('templates/<int:pk>/edit/', views.AssessmentTemplateUpdateView.as_view(), name='template_edit'),
    
    # ==================== Patient Assessments ====================
    path('', views.PatientAssessmentListView.as_view(), name='assessment_list'),
    path('patient/<int:patient_id>/', views.PatientAssessmentListView.as_view(), name='assessment_list_by_patient'),
    path('detail/<int:pk>/', views.PatientAssessmentDetailView.as_view(), name='assessment_detail'),
    path('create/', views.PatientAssessmentCreateView.as_view(), name='assessment_create'),
    path('<int:pk>/edit/', views.PatientAssessmentUpdateView.as_view(), name='assessment_edit'),
    
    # ==================== API Endpoints ====================
    path('api/templates/<int:pk>/items/', views.get_template_items, name='api_template_items'),
    path('api/patient/<int:patient_id>/history/', views.patient_assessment_history, name='api_patient_history'),
]