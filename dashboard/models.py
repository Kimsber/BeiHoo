from django.db import models
from django.conf import settings
from django.utils import timezone

class Shift(models.Model):
    """Work shift schedule for healthcare staff"""
    
    SHIFT_TYPE_CHOICES = [
        ('morning', '早班 (08:00-16:00)'),
        ('afternoon', '中班 (16:00-00:00)'),
        ('night', '夜班 (00:00-08:00)'),
        ('full_day', '全日 (08:00-17:00)'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', '已排班'),
        ('confirmed', '已確認'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='shifts',
        verbose_name='員工'
    )
    shift_type = models.CharField(
        max_length=20,
        choices=SHIFT_TYPE_CHOICES,
        verbose_name='班別'
    )
    date = models.DateField(verbose_name='日期')
    start_time = models.TimeField(verbose_name='開始時間')
    end_time = models.TimeField(verbose_name='結束時間')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled',
        verbose_name='狀態'
    )
    location = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='地點/部門'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='備註'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'shifts'
        ordering = ['date', 'start_time']
        verbose_name = '班表'
        verbose_name_plural = '班表'
        unique_together = ['user', 'date', 'start_time']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_shift_type_display()} - {self.date}"
    
    @property
    def is_today(self):
        """Check if shift is today"""
        return self.date == timezone.now().date()
    
    @property
    def is_current(self):
        """Check if shift is currently active"""
        now = timezone.now()
        if self.date == now.date():
            current_time = now.time()
            return self.start_time <= current_time <= self.end_time
        return False
    
    def get_duration(self):
        """Calculate shift duration in hours"""
        from datetime import datetime, timedelta
        start = datetime.combine(self.date, self.start_time)
        end = datetime.combine(self.date, self.end_time)
        
        # Handle shifts that cross midnight
        if end < start:
            end += timedelta(days=1)
        
        duration = (end - start).total_seconds() / 3600
        return round(duration, 1)