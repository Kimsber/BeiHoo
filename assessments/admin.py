from django.contrib import admin
from .models import AssessmentTemplate, PatientAssessment


@admin.register(AssessmentTemplate)
class AssessmentTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'category', 'status', 'max_score', 'version', 'created_at']
    list_filter = ['category', 'status']
    search_fields = ['name', 'code', 'description']
    ordering = ['category', 'name']
    
    fieldsets = (
        ('基本資訊', {
            'fields': ('name', 'code', 'category', 'description', 'status', 'version')
        }),
        ('評分設定', {
            'fields': ('max_score', 'min_score', 'higher_is_better', 'score_interpretation')
        }),
        ('評估項目', {
            'fields': ('items', 'applicable_roles')
        }),
        ('FHIR 整合', {
            'fields': ('fhir_id',),
            'classes': ('collapse',)
        }),
    )


@admin.register(PatientAssessment)
class PatientAssessmentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'template', 'assessed_by', 'assessment_date', 'total_score', 'status']
    list_filter = ['status', 'template__category', 'sync_status']
    search_fields = ['patient__first_name', 'patient__last_name', 'patient__username']
    date_hierarchy = 'assessment_date'
    ordering = ['-assessment_date']
    
    fieldsets = (
        ('評估資訊', {
            'fields': ('patient', 'template', 'assessed_by', 'assessment_date', 'status')
        }),
        ('評估結果', {
            'fields': ('responses', 'total_score', 'interpretation', 'clinical_notes')
        }),
        ('關聯記錄', {
            'fields': ('related_care_plan', 'related_rehab_plan'),
            'classes': ('collapse',)
        }),
        ('FHIR 同步', {
            'fields': ('fhir_id', 'sync_status', 'last_synced_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['last_synced_at']