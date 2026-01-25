from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """Custom user model with role-based access"""
    
    ROLE_CHOICES = [
        ('admin', '系統管理員'),
        ('doctor', '醫師'),
        ('therapist', '治療師'),
        ('nurse', '護理師'),
        ('patient', '病患'),
        ('researcher', '研究員'),
    ]
    
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='patient',
        verbose_name='角色'
    )
    phone_number = models.CharField(
        max_length=20, 
        blank=True, 
        verbose_name='電話'
    )
    date_of_birth = models.DateField(
        null=True, 
        blank=True, 
        verbose_name='生日'
    )
    avatar = models.ImageField(
        upload_to='avatars/', 
        blank=True, 
        null=True, 
        verbose_name='頭像'
    )
    
    # For FHIR integration later
    fhir_resource_id = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        help_text="FHIR Resource ID"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = '使用者'
        verbose_name_plural = '使用者'
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
    
    @property
    def is_clinician(self):
        """醫療人員判斷"""
        return self.role in ['doctor', 'therapist', 'nurse']
    
    @property
    def is_patient_user(self):
        """病患判斷"""
        return self.role == 'patient'
    
    @property
    def display_name(self):
        """返回顯示名稱（優先使用姓名，否則使用帳號）"""
        full_name = self.get_full_name()
        if full_name:
            return full_name
        return self.username

    @property
    def dashboard_url(self):
        """Get the URL name for user's dashboard"""
        from django.conf import settings
        return settings.ROLE_DASHBOARD_MAP.get(self.role, 'dashboard:patient')


class AuditLog(models.Model):
    """稽核紀錄 - 用於追蹤所有操作"""
    
    ACTION_CHOICES = [
        ('create', '建立'),
        ('read', '讀取'),
        ('update', '更新'),
        ('delete', '刪除'),
        ('login', '登入'),
        ('logout', '登出'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        verbose_name='使用者'
    )
    action = models.CharField(
        max_length=10, 
        choices=ACTION_CHOICES, 
        verbose_name='動作'
    )
    resource_type = models.CharField(
        max_length=50, 
        blank=True, 
        verbose_name='資源類型'
    )
    resource_id = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name='資源ID'
    )
    ip_address = models.GenericIPAddressField(
        null=True, 
        verbose_name='IP位址'
    )
    timestamp = models.DateTimeField(
        auto_now_add=True, 
        verbose_name='時間'
    )
    details = models.TextField(
        blank=True, 
        verbose_name='詳細資訊'
    )
    
    class Meta:
        db_table = 'audit_logs'
        ordering = ['-timestamp']
        verbose_name = '稽核紀錄'
        verbose_name_plural = '稽核紀錄'
    
    def __str__(self):
        return f"{self.user} - {self.get_action_display()} - {self.timestamp}"