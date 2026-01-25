from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta

class ServiceType(models.Model):
    """定義預約服務類型 (Maps to FHIR ServiceType)"""
    
    code = models.CharField(
        max_length=50, 
        unique=True,
        verbose_name='服務代碼'
    )
    display_name_zh = models.CharField(
        max_length=100,
        verbose_name='顯示名稱'
    )
    display_name_en = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='英文名稱'
    )
    default_duration = models.IntegerField(
        default=30,
        verbose_name='預設時長(分鐘)',
        help_text='預設預約時長，單位為分鐘'
    )
    requires_robot = models.BooleanField(
        default=False,
        verbose_name='需要機器人設備'
    )
    color = models.CharField(
        max_length=7,
        default='#007bff',
        verbose_name='顏色代碼',
        help_text='用於日曆顯示，格式: #RRGGBB'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='啟用'
    )
    description = models.TextField(
        blank=True,
        verbose_name='描述'
    )
    
    class Meta:
        db_table = 'service_types'
        verbose_name = '服務類型'
        verbose_name_plural = '服務類型'
        ordering = ['code']
    
    def __str__(self):
        return f"{self.display_name_zh} ({self.default_duration}分鐘)"


class Appointment(models.Model):
    """預約記錄 (Maps to FHIR Appointment Resource)"""
    
    STATUS_CHOICES = [
        ('proposed', '提議中'),
        ('pending', '待確認'),
        ('booked', '已預約'),
        ('arrived', '已報到'),
        ('fulfilled', '已完成'),
        ('cancelled', '已取消'),
        ('noshow', '未到'),
    ]
    
    PRIORITY_CHOICES = [
        ('routine', '一般'),
        ('urgent', '緊急'),
        ('asap', '盡快'),
        ('stat', '立即'),
    ]
    
    # FHIR Integration
    fhir_id = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True,
        verbose_name='FHIR資源ID',
        help_text='FHIR Appointment resource identifier'
    )
    
    identifier = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='預約編號',
        help_text='內部預約編號，格式: APT-YYYYMMDDXXXXX'
    )
    
    # Participants
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patient_appointments',
        limit_choices_to={'role': 'patient'},
        verbose_name='病患'
    )
    
    practitioner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='practitioner_appointments',
        limit_choices_to={'role__in': ['doctor', 'therapist', 'nurse']},
        verbose_name='醫師/治療師'
    )
    
    # Service
    service_type = models.ForeignKey(
        ServiceType,
        on_delete=models.PROTECT,
        verbose_name='服務類型'
    )
    
    # Status & Priority
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='booked',
        verbose_name='狀態'
    )
    
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='routine',
        verbose_name='優先度'
    )
    
    # Timing
    appointment_date = models.DateField(
        verbose_name='預約日期'
    )
    
    start_time = models.TimeField(
        verbose_name='開始時間'
    )
    
    end_time = models.TimeField(
        verbose_name='結束時間'
    )
    
    duration_minutes = models.IntegerField(
        verbose_name='時長(分鐘)',
        help_text='自動計算'
    )
    
    # Location
    location = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='地點',
        help_text='例: 診間A, 復健室1'
    )
    
    # Clinical Information
    reason_code = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='就診原因',
        help_text='主訴'
    )
    
    reason_reference = models.TextField(
        blank=True,
        verbose_name='詳細原因',
        help_text='詳細描述'
    )
    
    comment = models.TextField(
        blank=True,
        verbose_name='備註'
    )
    
    # Status Tracking
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='建立時間'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新時間'
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_appointments',
        verbose_name='建立者'
    )
    
    checked_in_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='報到時間'
    )
    
    checked_in_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='checked_in_appointments',
        verbose_name='報到人員'
    )
    
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='完成時間'
    )
    
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='取消時間'
    )
    
    cancellation_reason = models.TextField(
        blank=True,
        verbose_name='取消原因'
    )
    
    # FHIR Sync
    last_synced_to_fhir = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='最後同步至FHIR時間'
    )
    
    sync_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', '待同步'),
            ('synced', '已同步'),
            ('error', '錯誤'),
        ],
        default='pending',
        verbose_name='同步狀態'
    )
    
    sync_error_message = models.TextField(
        blank=True,
        verbose_name='同步錯誤訊息'
    )
    
    class Meta:
        db_table = 'appointments'
        verbose_name = '預約'
        verbose_name_plural = '預約'
        ordering = ['appointment_date', 'start_time']
        indexes = [
            models.Index(fields=['appointment_date', 'practitioner']),
            models.Index(fields=['appointment_date', 'patient']),
            models.Index(fields=['status']),
            models.Index(fields=['practitioner', 'appointment_date', 'start_time']),
        ]
    
    def __str__(self):
        return f"{self.identifier} - {self.patient.get_full_name()} ({self.appointment_date} {self.start_time})"
    
    def save(self, *args, **kwargs):
        # Auto-generate identifier
        if not self.identifier:
            date_str = timezone.now().strftime('%Y%m%d')
            last_appt = Appointment.objects.filter(
                identifier__startswith=f'APT-{date_str}'
            ).order_by('-identifier').first()
            
            if last_appt:
                last_num = int(last_appt.identifier.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1
            
            self.identifier = f'APT-{date_str}{new_num:05d}'
        
        # Calculate duration
        if self.start_time and self.end_time:
            start = datetime.combine(self.appointment_date, self.start_time)
            end = datetime.combine(self.appointment_date, self.end_time)
            self.duration_minutes = int((end - start).total_seconds() / 60)
        
        super().save(*args, **kwargs)
    
    def clean(self):
        """Validation"""
        # Check if end time is after start time
        if self.start_time and self.end_time:
            if self.end_time <= self.start_time:
                raise ValidationError('結束時間必須晚於開始時間')
        
        # Check for conflicts (same practitioner, overlapping time)
        if self.practitioner and self.appointment_date and self.start_time and self.end_time:
            conflicts = Appointment.objects.filter(
                practitioner=self.practitioner,
                appointment_date=self.appointment_date,
                status__in=['booked', 'arrived']
            ).exclude(pk=self.pk)
            
            for appt in conflicts:
                if (self.start_time < appt.end_time and self.end_time > appt.start_time):
                    raise ValidationError(
                        f'時間衝突: {self.practitioner.get_full_name()} '
                        f'在 {appt.start_time}-{appt.end_time} 已有預約'
                    )
    
    @property
    def is_today(self):
        """Check if appointment is today"""
        return self.appointment_date == timezone.now().date()
    
    @property
    def is_past(self):
        """Check if appointment is in the past"""
        now = timezone.now()
        appt_datetime = datetime.combine(self.appointment_date, self.end_time)
        return appt_datetime < now.replace(tzinfo=None)
    
    @property
    def is_upcoming(self):
        """Check if appointment is upcoming (within 30 minutes)"""
        if not self.is_today:
            return False
        
        now = timezone.now()
        appt_datetime = datetime.combine(self.appointment_date, self.start_time)
        diff = (appt_datetime - now.replace(tzinfo=None)).total_seconds() / 60
        
        return 0 <= diff <= 30
    
    @property
    def is_overdue(self):
        """Check if patient hasn't arrived and appointment time has passed"""
        if self.status not in ['booked', 'pending']:
            return False
        
        now = timezone.now()
        appt_datetime = datetime.combine(self.appointment_date, self.start_time)
        return appt_datetime < now.replace(tzinfo=None)
    
    def check_in(self, user):
        """Mark appointment as arrived"""
        if self.status in ['booked', 'pending']:
            self.status = 'arrived'
            self.checked_in_at = timezone.now()
            self.checked_in_by = user
            self.save()
            return True
        return False
    
    def complete(self):
        """Mark appointment as fulfilled"""
        if self.status == 'arrived':
            self.status = 'fulfilled'
            self.completed_at = timezone.now()
            self.save()
            return True
        return False
    
    def cancel(self, reason=''):
        """Cancel appointment"""
        if self.status not in ['fulfilled', 'cancelled', 'noshow']:
            self.status = 'cancelled'
            self.cancelled_at = timezone.now()
            self.cancellation_reason = reason
            self.save()
            return True
        return False
    
    def mark_no_show(self):
        """Mark as no show"""
        if self.status in ['booked', 'pending'] and self.is_past:
            self.status = 'noshow'
            self.save()
            return True
        return False


class AppointmentNote(models.Model):
    """預約備註"""
    
    NOTE_TYPE_CHOICES = [
        ('clinical', '臨床'),
        ('administrative', '行政'),
        ('cancellation', '取消'),
        ('rescheduling', '改期'),
    ]
    
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name='notes',
        verbose_name='預約'
    )
    
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='作者'
    )
    
    note_type = models.CharField(
        max_length=20,
        choices=NOTE_TYPE_CHOICES,
        default='administrative',
        verbose_name='備註類型'
    )
    
    content = models.TextField(
        verbose_name='內容'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='建立時間'
    )
    
    class Meta:
        db_table = 'appointment_notes'
        verbose_name = '預約備註'
        verbose_name_plural = '預約備註'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.appointment.identifier} - {self.get_note_type_display()} - {self.created_at}"