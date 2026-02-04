from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class AssessmentTemplate(models.Model):
    """
    評估量表範本
    Maps to FHIR Questionnaire Resource
    """
    
    CATEGORY_CHOICES = [
        ('functional', '功能評估'),      # ADL, IADL, Barthel Index
        ('cognitive', '認知評估'),       # MMSE, MoCA
        ('pain', '疼痛評估'),            # VAS, NRS
        ('nutrition', '營養評估'),       # MNA
        ('fall_risk', '跌倒風險'),       # Morse Fall Scale
        ('pressure', '壓瘡風險'),        # Braden Scale
        ('mood', '情緒評估'),            # GDS, PHQ-9
        ('rehab', '復健評估'),           # FIM, Berg Balance
        ('adl', '日常生活功能'),         # Barthel, Katz
        ('custom', '自訂評估'),
    ]
    
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('active', '啟用'),
        ('retired', '停用'),
    ]
    
    name = models.CharField(
        max_length=200,
        verbose_name='評估名稱'
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='評估代碼',
        help_text='唯一識別碼，如 BARTHEL, MMSE'
    )
    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES,
        verbose_name='評估類別'
    )
    description = models.TextField(
        blank=True,
        verbose_name='說明'
    )
    
    # Scoring configuration
    max_score = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='滿分'
    )
    min_score = models.IntegerField(
        default=0,
        verbose_name='最低分'
    )
    score_interpretation = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='分數解釋',
        help_text='JSON格式，如 {"0-20": "完全依賴", "21-60": "嚴重依賴"}'
    )
    higher_is_better = models.BooleanField(
        default=True,
        verbose_name='分數越高越好',
        help_text='勾選表示高分為正向結果'
    )
    
    # Template structure - flexible JSON for questionnaire items
    items = models.JSONField(
        default=list,
        verbose_name='評估項目',
        help_text='JSON格式的評估項目結構'
    )
    
    # Metadata
    version = models.CharField(
        max_length=20,
        default='1.0',
        verbose_name='版本'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='狀態'
    )
    
    # Applicable roles - who can conduct this assessment
    applicable_roles = models.JSONField(
        default=list,
        blank=True,
        verbose_name='適用角色',
        help_text='可執行此評估的角色列表'
    )
    
    # FHIR Integration (for future use)
    fhir_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='FHIR Questionnaire ID'
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_assessment_templates'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'assessment_templates'
        verbose_name = '評估範本'
        verbose_name_plural = '評估範本'
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def get_interpretation(self, score):
        """根據分數返回解釋文字"""
        if not self.score_interpretation:
            return ""
        
        for range_str, interpretation in self.score_interpretation.items():
            if '-' in range_str:
                min_val, max_val = map(int, range_str.split('-'))
                if min_val <= score <= max_val:
                    return interpretation
        return ""


class PatientAssessment(models.Model):
    """
    病患評估記錄
    Maps to FHIR QuestionnaireResponse Resource
    """
    
    STATUS_CHOICES = [
        ('in_progress', '進行中'),
        ('completed', '已完成'),
        ('amended', '已修正'),
        ('cancelled', '已取消'),
    ]
    
    SYNC_STATUS_CHOICES = [
        ('pending', '待同步'),
        ('synced', '已同步'),
        ('error', '同步錯誤'),
    ]
    
    # Core relationships
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'patient'},
        related_name='assessments',
        verbose_name='病患'
    )
    
    template = models.ForeignKey(
        AssessmentTemplate,
        on_delete=models.PROTECT,
        related_name='responses',
        verbose_name='評估範本'
    )
    
    assessed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='conducted_assessments',
        verbose_name='評估者'
    )
    
    # Assessment timing
    assessment_date = models.DateTimeField(
        default=timezone.now,
        verbose_name='評估日期時間'
    )
    
    # Responses and scoring
    responses = models.JSONField(
        default=dict,
        verbose_name='評估回應',
        help_text='JSON格式的評估回應資料'
    )
    
    total_score = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='總分'
    )
    
    interpretation = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='結果判讀'
    )
    
    # Clinical context
    clinical_notes = models.TextField(
        blank=True,
        verbose_name='臨床備註'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='in_progress',
        verbose_name='狀態'
    )
    
    # Related clinical records (optional links for patient-centered care)
    related_care_plan = models.ForeignKey(
        'clinical.CarePlan',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='related_assessments',
        verbose_name='相關照護計畫'
    )
    
    related_rehab_plan = models.ForeignKey(
        'clinical.RehabPlan',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='related_assessments',
        verbose_name='相關復健計畫'
    )
    
    # FHIR Integration
    fhir_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='FHIR QuestionnaireResponse ID'
    )
    
    sync_status = models.CharField(
        max_length=20,
        choices=SYNC_STATUS_CHOICES,
        default='pending',
        verbose_name='同步狀態'
    )
    last_synced_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='最後同步時間'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'patient_assessments'
        verbose_name = '病患評估'
        verbose_name_plural = '病患評估'
        ordering = ['-assessment_date']
        indexes = [
            models.Index(fields=['patient', '-assessment_date']),
            models.Index(fields=['template', '-assessment_date']),
            models.Index(fields=['status']),
            models.Index(fields=['sync_status']),
        ]
    
    def __str__(self):
        return f"{self.patient.get_full_name()} - {self.template.name} ({self.assessment_date.strftime('%Y-%m-%d')})"
    
    def calculate_score(self):
        """計算總分並更新解釋"""
        if not self.responses:
            return
        
        total = 0
        for item_id, response in self.responses.items():
            if isinstance(response, dict) and 'score' in response:
                total += response['score']
            elif isinstance(response, (int, float)):
                total += response
        
        self.total_score = total
        self.interpretation = self.template.get_interpretation(total)
    
    def save(self, *args, **kwargs):
        # Auto-calculate score if responses exist and status is completed
        if self.status == 'completed' and self.responses:
            self.calculate_score()
        super().save(*args, **kwargs)