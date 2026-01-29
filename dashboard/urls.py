from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('admin/', views.admin_dashboard, name='admin'),
    path('doctor/', views.doctor_dashboard, name='doctor'),
    path('therapist/', views.therapist_dashboard, name='therapist'),
    path('nurse/', views.nurse_dashboard, name='nurse'),
    path('case-manager/', views.case_manager_dashboard, name='case_manager'),
    path('caregiver/', views.caregiver_dashboard, name='caregiver'),
    path('patient/', views.patient_dashboard, name='patient'),
    path('researcher/', views.researcher_dashboard, name='researcher'),
    
    # Shift management URLs
    path('shifts/', views.shift_management, name='shift_management'),
    path('shifts/create/', views.shift_create, name='shift_create'),
    path('shifts/<int:shift_id>/edit/', views.shift_edit, name='shift_edit'),
    path('shifts/<int:shift_id>/delete/', views.shift_delete, name='shift_delete'),
    path('shifts/bulk-action/', views.shift_bulk_action, name='shift_bulk_action'),
    path('shifts/upload-excel/', views.shift_upload_excel, name='shift_upload_excel'),
    path('shifts/download-template/', views.shift_download_template, name='shift_download_template'),

    # User management URLs
    path('users/', views.user_management, name='user_management'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:user_id>/delete/', views.user_delete, name='user_delete'),
    path('users/<int:user_id>/toggle-active/', views.user_toggle_active, name='user_toggle_active'),
    path('users/<int:user_id>/reset-password/', views.user_reset_password, name='user_reset_password'),
]