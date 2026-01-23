from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, AuditLog

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """自訂使用者管理介面"""
    
    list_display = ['username', 'email', 'role', 'get_full_name', 'is_staff', 'is_active', 'created_at']
    list_filter = ['role', 'is_staff', 'is_active', 'created_at']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone_number']
    ordering = ['-created_at']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('個人資訊', {
            'fields': ('role', 'phone_number', 'date_of_birth', 'avatar')
        }),
        ('FHIR 整合', {
            'fields': ('fhir_resource_id',),
            'classes': ('collapse',)
        }),
        ('時間戳記', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('額外資訊', {
            'fields': ('role', 'email', 'first_name', 'last_name', 'phone_number', 'date_of_birth')
        }),
    )


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """稽核紀錄管理介面 - 唯讀"""
    
    list_display = ['timestamp', 'user', 'action', 'resource_type', 'resource_id', 'ip_address']
    list_filter = ['action', 'timestamp', 'resource_type']
    search_fields = ['user__username', 'resource_type', 'resource_id', 'ip_address']
    date_hierarchy = 'timestamp'
    readonly_fields = ['user', 'action', 'resource_type', 'resource_id', 'ip_address', 'timestamp', 'details']
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser