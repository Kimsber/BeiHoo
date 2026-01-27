from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    # Schedule views
    path('schedule/', views.appointment_schedule_grid, name='schedule_grid'),
    path('list/', views.appointment_list, name='list'),
    
    # CRUD operations
    path('create/', views.appointment_create, name='create'),
    path('<int:appointment_id>/', views.appointment_detail, name='detail'),
    path('<int:appointment_id>/edit/', views.appointment_edit, name='edit'),
    path('<int:appointment_id>/delete/', views.appointment_delete, name='delete'),
    
    # Status updates
    path('<int:appointment_id>/checkin/', views.check_in_appointment, name='checkin'),
    path('<int:appointment_id>/complete/', views.complete_appointment, name='complete'),
    path('<int:appointment_id>/cancel/', views.cancel_appointment, name='cancel'),
]