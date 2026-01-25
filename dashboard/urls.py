from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('admin/', views.admin_dashboard, name='admin'),
    path('doctor/', views.doctor_dashboard, name='doctor'),
    path('therapist/', views.therapist_dashboard, name='therapist'),
    path('nurse/', views.nurse_dashboard, name='nurse'),
    path('patient/', views.patient_dashboard, name='patient'),
    path('researcher/', views.researcher_dashboard, name='researcher'),
    
    # Shift management URLs
    path('shifts/', views.shift_management, name='shift_management'),
    path('shifts/create/', views.shift_create, name='shift_create'),
    path('shifts/<int:shift_id>/edit/', views.shift_edit, name='shift_edit'),
    path('shifts/<int:shift_id>/delete/', views.shift_delete, name='shift_delete'),
    path('shifts/bulk-action/', views.shift_bulk_action, name='shift_bulk_action'),
]