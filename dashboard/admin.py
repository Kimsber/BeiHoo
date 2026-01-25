from django.contrib import admin
from .models import Shift

@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    """Admin interface for shift management"""
    
    list_display = ['user', 'date', 'shift_type', 'start_time', 'end_time', 'status', 'location']
    list_filter = ['shift_type', 'status', 'date', 'user__role']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'location', 'notes']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('基本資訊', {
            'fields': ('user', 'date', 'shift_type')
        }),
        ('時間設定', {
            'fields': ('start_time', 'end_time')
        }),
        ('狀態與地點', {
            'fields': ('status', 'location', 'notes')
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user')