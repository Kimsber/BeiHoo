from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class PatientRecord(models.Model):
    """Patient medical record overview"""
    
    STATUS_CHOICES = [
        ('active', '在院'),
        ('discharged', '已出院'),
        ('transferred', '已轉院'),
    ]
    
    patient = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'patient'},
        related_name='patient_record'
    )
    
    medical_record_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='病歷號'
    )
    
    admission_date = models.DateField(
        default=timezone.now,
        verbose_name='入院日期'
    )
    
    discharge_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='出院日期'
    )
    
    primary_diagnosis = models.CharField(
        max_length=200,
        verbose_name='主要診斷'
    )
    
    secondary_diagnosis = models.TextField(
        blank=True,
        verbose_name='次要診斷'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='狀態'
    )
    
    allergies = models.TextField(
        blank=True,
        verbose_name='過敏史'
    )
    
    medical_history = models.TextField(
        blank=True,
        verbose_name='病史'
    )
    
    emergency_contact_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='緊急聯絡人'
    )
    
    emergency_contact_phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='緊急聯絡電話'
    )
    
    # Case Manager Assignment
    case_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'case_manager'},
        related_name='managed_patients',
        verbose_name='個管師'
    )
    
    # Caregiver Assignment
    caregiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'caregiver'},
        related_name='cared_patients',
        verbose_name='照服員'
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name='備註'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'patient_records'
        verbose_name = '病患記錄'
        verbose_name_plural = '病患記錄'
        ordering = ['-admission_date']
    
    def __str__(self):
        return f"{self.patient.get_full_name()} - {self.medical_record_number}"


class MedicalRecord(models.Model):
    """Medical consultation records (SOAP notes)"""
    
    RECORD_TYPE_CHOICES = [
        ('consultation', '門診'),
        ('followup', '複診'),
        ('emergency', '急診'),
        ('inpatient', '住院'),
    ]
    
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'patient'},
        related_name='medical_records'
    )
    
    practitioner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role__in': ['doctor', 'therapist']},
        related_name='created_medical_records'
    )
    
    record_date = models.DateField(default=timezone.now)
    record_time = models.TimeField(default=timezone.now)
    
    record_type = models.CharField(
        max_length=20,
        choices=RECORD_TYPE_CHOICES,
        default='consultation'
    )
    
    # SOAP Notes
    chief_complaint = models.TextField(verbose_name='主訴 (Subjective)')
    objective_findings = models.TextField(verbose_name='客觀發現 (Objective)', blank=True)
    assessment = models.TextField(verbose_name='評估 (Assessment)')
    plan = models.TextField(verbose_name='計畫 (Plan)')
    
    diagnosis = models.CharField(max_length=200, blank=True, verbose_name='診斷')
    
    # FHIR Integration
    fhir_id = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'medical_records'
        verbose_name = '診療記錄'
        verbose_name_plural = '診療記錄'
        ordering = ['-record_date', '-record_time']
    
    def __str__(self):
        return f"{self.patient.get_full_name()} - {self.record_date} - {self.get_record_type_display()}"


class RehabPlan(models.Model):
    """Rehabilitation plan"""
    
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('active', '執行中'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]
    
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'patient'},
        related_name='rehab_plans'
    )
    
    therapist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'therapist'},
        related_name='created_rehab_plans'
    )
    
    plan_name = models.CharField(max_length=200, verbose_name='計畫名稱')
    description = models.TextField(verbose_name='說明')
    
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)
    
    goals = models.TextField(verbose_name='目標')
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    
    requires_robot = models.BooleanField(default=False, verbose_name='需要機器人')
    
    sessions_per_week = models.IntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(7)],
        verbose_name='每週次數'
    )
    
    duration_weeks = models.IntegerField(
        default=4,
        validators=[MinValueValidator(1)],
        verbose_name='計畫週數'
    )
    
    notes = models.TextField(blank=True, verbose_name='備註')
    
    # FHIR Integration
    fhir_id = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'rehab_plans'
        verbose_name = '復健計畫'
        verbose_name_plural = '復健計畫'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.patient.get_full_name()} - {self.plan_name}"


class RehabSession(models.Model):
    """Individual rehab session record"""
    
    rehab_plan = models.ForeignKey(
        RehabPlan,
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    
    session_date = models.DateField(default=timezone.now)
    session_time = models.TimeField(default=timezone.now)
    
    duration_minutes = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(240)]
    )
    
    robot_used = models.BooleanField(default=False)
    robot_name = models.CharField(max_length=100, blank=True)
    
    activities_performed = models.TextField(verbose_name='執行活動')
    patient_response = models.TextField(verbose_name='病患反應')
    
    progress_score = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name='進度評分 (1-10)'
    )
    
    completed = models.BooleanField(default=True)
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'rehab_sessions'
        verbose_name = '復健療程'
        verbose_name_plural = '復健療程'
        ordering = ['-session_date', '-session_time']
    
    def __str__(self):
        return f"{self.rehab_plan.patient.get_full_name()} - {self.session_date}"


class VitalSigns(models.Model):
    """Vital signs records"""
    
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'patient'},
        related_name='vital_signs'
    )
    
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role__in': ['nurse', 'doctor', 'caregiver']},
        related_name='recorded_vitals'
    )
    
    recorded_at = models.DateTimeField(default=timezone.now)
    
    # Vital signs measurements
    systolic_bp = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(50), MaxValueValidator(250)],
        verbose_name='收縮壓 (mmHg)'
    )
    
    diastolic_bp = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(30), MaxValueValidator(150)],
        verbose_name='舒張壓 (mmHg)'
    )
    
    heart_rate = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(30), MaxValueValidator(200)],
        verbose_name='心率 (bpm)'
    )
    
    respiratory_rate = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(8), MaxValueValidator(40)],
        verbose_name='呼吸率 (breaths/min)'
    )
    
    temperature = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name='體溫 (°C)'
    )
    
    spo2 = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(70), MaxValueValidator(100)],
        verbose_name='血氧飽和度 (%)'
    )
    
    weight = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name='體重 (kg)'
    )
    
    height = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name='身高 (cm)'
    )
    
    notes = models.TextField(blank=True)
    
    # FHIR Integration
    fhir_id = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        db_table = 'vital_signs'
        verbose_name = '生命徵象'
        verbose_name_plural = '生命徵象'
        ordering = ['-recorded_at']
    
    def __str__(self):
        return f"{self.patient.get_full_name()} - {self.recorded_at.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def blood_pressure(self):
        if self.systolic_bp and self.diastolic_bp:
            return f"{self.systolic_bp}/{self.diastolic_bp}"
        return "N/A"


class Medication(models.Model):
    """Medication orders"""
    
    STATUS_CHOICES = [
        ('active', '使用中'),
        ('completed', '已完成'),
        ('discontinued', '已停用'),
        ('on_hold', '暫停'),
    ]
    
    FREQUENCY_CHOICES = [
        ('once', '單次'),
        ('qd', '每日一次'),
        ('bid', '每日兩次'),
        ('tid', '每日三次'),
        ('qid', '每日四次'),
        ('q4h', '每4小時'),
        ('q6h', '每6小時'),
        ('q8h', '每8小時'),
        ('q12h', '每12小時'),
        ('prn', '需要時'),
    ]
    
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'patient'},
        related_name='medications'
    )
    
    prescribed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'doctor'},
        related_name='prescribed_medications'
    )
    
    medication_name = models.CharField(max_length=200, verbose_name='藥名')
    dosage = models.CharField(max_length=100, verbose_name='劑量')
    route = models.CharField(max_length=50, verbose_name='給藥途徑')
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, verbose_name='頻率')
    
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    indication = models.TextField(verbose_name='適應症')
    special_instructions = models.TextField(blank=True, verbose_name='特別指示')
    
    # FHIR Integration
    fhir_id = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'medications'
        verbose_name = '用藥'
        verbose_name_plural = '用藥'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.patient.get_full_name()} - {self.medication_name}"


class MedicationAdministration(models.Model):
    """Medication administration record"""
    
    STATUS_CHOICES = [
        ('scheduled', '已排程'),
        ('administered', '已給藥'),
        ('missed', '漏給'),
        ('refused', '拒絕'),
        ('held', '保留'),
    ]
    
    medication = models.ForeignKey(
        Medication,
        on_delete=models.CASCADE,
        related_name='administrations'
    )
    
    scheduled_time = models.DateTimeField(verbose_name='排程時間')
    administered_time = models.DateTimeField(null=True, blank=True, verbose_name='給藥時間')
    
    administered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        limit_choices_to={'role': 'nurse'},
        related_name='administered_medications'
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'medication_administrations'
        verbose_name = '給藥記錄'
        verbose_name_plural = '給藥記錄'
        ordering = ['-scheduled_time']
    
    def __str__(self):
        return f"{self.medication.medication_name} - {self.scheduled_time.strftime('%Y-%m-%d %H:%M')}"


class NursingNote(models.Model):
    """Nursing notes and assessments"""
    
    NOTE_TYPE_CHOICES = [
        ('admission', '入院評估'),
        ('shift', '交班記錄'),
        ('assessment', '護理評估'),
        ('intervention', '護理措施'),
        ('progress', '進度記錄'),
        ('discharge', '出院評估'),
    ]
    
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'patient'},
        related_name='nursing_notes'
    )
    
    nurse = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'nurse'},
        related_name='written_nursing_notes'
    )
    
    note_datetime = models.DateTimeField(default=timezone.now)
    note_type = models.CharField(max_length=20, choices=NOTE_TYPE_CHOICES)
    
    assessment = models.TextField(verbose_name='評估')
    intervention = models.TextField(verbose_name='措施')
    evaluation = models.TextField(verbose_name='評值', blank=True)
    
    # FHIR Integration
    fhir_id = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'nursing_notes'
        verbose_name = '護理紀錄'
        verbose_name_plural = '護理紀錄'
        ordering = ['-note_datetime']
    
    def __str__(self):
        return f"{self.patient.get_full_name()} - {self.note_datetime.strftime('%Y-%m-%d %H:%M')}"


class CarePlan(models.Model):
    """Care plan for case management"""
    
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('active', '執行中'),
        ('on_hold', '暫停'),
        ('completed', '完成'),
        ('cancelled', '取消'),
    ]
    
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'patient'},
        related_name='care_plans'
    )
    
    case_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'case_manager'},
        related_name='created_care_plans'
    )
    
    title = models.CharField(max_length=200, verbose_name='計畫名稱')
    description = models.TextField(verbose_name='說明')
    
    period_start = models.DateField(default=timezone.now)
    period_end = models.DateField(null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # FHIR Integration
    fhir_id = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'care_plans'
        verbose_name = '照護計畫'
        verbose_name_plural = '照護計畫'
        ordering = ['-period_start']
    
    def __str__(self):
        return f"{self.patient.get_full_name()} - {self.title}"


class CarePlanGoal(models.Model):
    """Goals within care plan"""
    
    ACHIEVEMENT_CHOICES = [
        ('in_progress', '進行中'),
        ('achieved', '已達成'),
        ('not_achieved', '未達成'),
        ('sustaining', '維持中'),
    ]
    
    care_plan = models.ForeignKey(
        CarePlan,
        on_delete=models.CASCADE,
        related_name='goals'
    )
    
    description = models.TextField(verbose_name='目標')
    target_date = models.DateField(null=True, blank=True, verbose_name='目標日期')
    
    achievement_status = models.CharField(
        max_length=20,
        choices=ACHIEVEMENT_CHOICES,
        default='in_progress'
    )
    
    priority = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name='優先度 (1-10)'
    )
    
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'care_plan_goals'
        verbose_name = '照護目標'
        verbose_name_plural = '照護目標'
        ordering = ['priority', 'target_date']
    
    def __str__(self):
        return f"{self.care_plan.title} - {self.description[:50]}"


class CareRecord(models.Model):
    """Daily care activity records by caregivers"""
    
    ACTIVITY_TYPE_CHOICES = [
        ('bathing', '沐浴協助'),
        ('dressing', '更衣協助'),
        ('feeding', '進食協助'),
        ('mobility', '移動協助'),
        ('toileting', '如廁協助'),
        ('exercise', '運動協助'),
        ('medication', '用藥協助'),
        ('hygiene', '個人衛生'),
        ('social', '社交活動'),
        ('other', '其他'),
    ]
    
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'patient'},
        related_name='care_records'
    )
    
    caregiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'caregiver'},
        related_name='created_care_records'
    )
    
    record_date = models.DateField(default=timezone.now)
    record_time = models.TimeField(default=timezone.now)
    
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPE_CHOICES)
    
    duration_minutes = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(480)]
    )
    
    description = models.TextField(verbose_name='活動說明')
    patient_response = models.TextField(verbose_name='病患反應', blank=True)
    
    # FHIR Integration
    fhir_id = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'care_records'
        verbose_name = '照護記錄'
        verbose_name_plural = '照護記錄'
        ordering = ['-record_date', '-record_time']
    
    def __str__(self):
        return f"{self.patient.get_full_name()} - {self.get_activity_type_display()} - {self.record_date}"


class IncidentReport(models.Model):
    """Incident reporting system"""
    
    INCIDENT_TYPE_CHOICES = [
        ('fall', '跌倒'),
        ('injury', '受傷'),
        ('medication_error', '用藥錯誤'),
        ('behavioral', '行為異常'),
        ('vital_abnormal', '生命徵象異常'),
        ('equipment', '設備問題'),
        ('infection', '感染'),
        ('other', '其他'),
    ]
    
    SEVERITY_CHOICES = [
        ('minor', '輕微'),
        ('moderate', '中度'),
        ('severe', '嚴重'),
        ('critical', '危急'),
    ]
    
    STATUS_CHOICES = [
        ('reported', '已通報'),
        ('under_review', '審查中'),
        ('action_taken', '已處理'),
        ('resolved', '已結案'),
    ]
    
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'patient'},
        related_name='incidents'
    )
    
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reported_incidents'
    )
    
    incident_datetime = models.DateTimeField(default=timezone.now)
    
    incident_type = models.CharField(max_length=30, choices=INCIDENT_TYPE_CHOICES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    
    description = models.TextField(verbose_name='事件描述')
    immediate_action = models.TextField(verbose_name='立即處置')
    
    location = models.CharField(max_length=100, verbose_name='發生地點', blank=True)
    
    notified_staff = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='received_incident_notifications',
        blank=True
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='reported')
    
    follow_up_notes = models.TextField(blank=True, verbose_name='後續追蹤')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'incident_reports'
        verbose_name = '異常通報'
        verbose_name_plural = '異常通報'
        ordering = ['-incident_datetime']
    
    def __str__(self):
        return f"{self.patient.get_full_name()} - {self.get_incident_type_display()} - {self.incident_datetime.strftime('%Y-%m-%d')}"


class Equipment(models.Model):
    """Medical and rehab equipment inventory"""
    
    STATUS_CHOICES = [
        ('available', '可用'),
        ('in_use', '使用中'),
        ('maintenance', '維護中'),
        ('broken', '故障'),
        ('retired', '報廢'),
    ]
    
    EQUIPMENT_TYPE_CHOICES = [
        ('robot', '復健機器人'),
        ('wheelchair', '輪椅'),
        ('walker', '助行器'),
        ('medical_device', '醫療設備'),
        ('exercise', '運動器材'),
        ('other', '其他'),
    ]
    
    equipment_name = models.CharField(max_length=200, verbose_name='設備名稱')
    equipment_type = models.CharField(max_length=30, choices=EQUIPMENT_TYPE_CHOICES)
    
    manufacturer = models.CharField(max_length=100, verbose_name='製造商', blank=True)
    model_number = models.CharField(max_length=100, verbose_name='型號', blank=True)
    serial_number = models.CharField(max_length=100, unique=True, verbose_name='序號')
    
    purchase_date = models.DateField(null=True, blank=True, verbose_name='購買日期')
    last_maintenance_date = models.DateField(null=True, blank=True, verbose_name='最後維護日期')
    next_maintenance_date = models.DateField(null=True, blank=True, verbose_name='下次維護日期')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    location = models.CharField(max_length=100, verbose_name='存放位置')
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'equipment'
        verbose_name = '設備'
        verbose_name_plural = '設備'
        ordering = ['equipment_name']
    
    def __str__(self):
        return f"{self.equipment_name} ({self.serial_number})"


class EquipmentReservation(models.Model):
    """Equipment reservation system"""
    
    STATUS_CHOICES = [
        ('pending', '待確認'),
        ('confirmed', '已確認'),
        ('in_use', '使用中'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]
    
    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        related_name='reservations'
    )
    
    reserved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='equipment_reservations'
    )
    
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'patient'},
        related_name='equipment_usage',
        null=True,
        blank=True
    )
    
    reservation_date = models.DateField(default=timezone.now)
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    purpose = models.TextField(verbose_name='使用目的')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'equipment_reservations'
        verbose_name = '設備預約'
        verbose_name_plural = '設備預約'
        ordering = ['reservation_date', 'start_time']
    
    def __str__(self):
        return f"{self.equipment.equipment_name} - {self.reservation_date} {self.start_time}"