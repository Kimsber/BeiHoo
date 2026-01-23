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
]