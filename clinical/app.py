from django.apps import AppConfig


class ClinicalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'clinical'
    verbose_name = '臨床管理'