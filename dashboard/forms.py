from django import forms
from django.core.exceptions import ValidationError
from .models import Shift
from account.models import User


class ShiftForm(forms.ModelForm):
    """Form for creating and editing shifts"""
    
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True, role__in=['doctor', 'therapist', 'nurse']),
        label='員工',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    date = forms.DateField(
        label='日期',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    start_time = forms.TimeField(
        label='開始時間',
        widget=forms.TimeInput(attrs={
            'type': 'time',
            'class': 'form-control'
        })
    )
    
    end_time = forms.TimeField(
        label='結束時間',
        widget=forms.TimeInput(attrs={
            'type': 'time',
            'class': 'form-control'
        })
    )
    
    class Meta:
        model = Shift
        fields = ['user', 'shift_type', 'date', 'start_time', 'end_time', 'status', 'location', 'notes']
        widgets = {
            'shift_type': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '例如：門診一、復健科'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '備註事項（選填）'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get('user')
        date = cleaned_data.get('date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        # Check if end_time is after start_time
        if start_time and end_time:
            if end_time <= start_time:
                raise ValidationError('結束時間必須晚於開始時間')
        
        # Check for overlapping shifts for the same user on the same date
        if user and date and start_time and end_time:
            overlapping_shifts = Shift.objects.filter(
                user=user,
                date=date,
                status__in=['scheduled', 'confirmed']
            ).exclude(pk=self.instance.pk if self.instance.pk else None)
            
            for shift in overlapping_shifts:
                # Check if time ranges overlap
                if not (end_time <= shift.start_time or start_time >= shift.end_time):
                    raise ValidationError(
                        f'此時段與現有班表衝突：{shift.get_shift_type_display()} '
                        f'({shift.start_time.strftime("%H:%M")} - {shift.end_time.strftime("%H:%M")})'
                    )
        
        return cleaned_data


class ShiftFilterForm(forms.Form):
    """Form for filtering shifts"""
    
    role = forms.ChoiceField(
        choices=[('', '所有角色')] + [
            ('doctor', '醫師'),
            ('therapist', '治療師'),
            ('nurse', '護理師'),
        ],
        required=False,
        label='角色',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    status = forms.ChoiceField(
        choices=[('', '所有狀態')] + Shift.STATUS_CHOICES,
        required=False,
        label='狀態',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True, role__in=['doctor', 'therapist', 'nurse']),
        required=False,
        label='員工',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    date_from = forms.DateField(
        required=False,
        label='開始日期',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        label='結束日期',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )


class BulkShiftActionForm(forms.Form):
    """Form for bulk actions on shifts"""
    
    ACTION_CHOICES = [
        ('confirm', '確認班表'),
        ('cancel', '取消班表'),
        ('delete', '刪除班表'),
    ]
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        label='批次操作',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    shift_ids = forms.CharField(
        widget=forms.HiddenInput()
    )