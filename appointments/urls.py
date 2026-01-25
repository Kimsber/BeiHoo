from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('schedule/', views.appointment_schedule_grid, name='schedule_grid'),
    path('<int:appointment_id>/', views.appointment_detail, name='detail'),
    path('<int:appointment_id>/checkin/', views.check_in_appointment, name='checkin'),
    path('<int:appointment_id>/complete/', views.complete_appointment, name='complete'),
    path('<int:appointment_id>/cancel/', views.cancel_appointment, name='cancel'),
]