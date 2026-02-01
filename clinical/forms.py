from django import forms
from django.core.exceptions import ValidationError
from .models import (
    PatientRecord, MedicalRecord, RehabPlan, RehabSession,
    VitalSigns, Medication, MedicationAdministration,
    NursingNote, CarePlan, CarePlanGoal, CareRecord,
    IncidentReport, Equipment, EquipmentReservation
)
from account.models import User


class PatientRecordForm(forms.ModelForm):
    """Form for creating and editing patient records"""
    
    patient = forms.ModelChoiceField(
        queryset=User.objects.filter(role='patient', is_active=True),
        label='病患',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    admission_date = forms.DateField(
        label='入院日期',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    discharge_date = forms.DateField(
        required=False,
        label='出院日期',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    case_manager = forms.ModelChoiceField(
        queryset=User.objects.filter(role='case_manager', is_active=True),
        required=False,
        label='個管師',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    caregiver = forms.ModelChoiceField(
        queryset=User.objects.filter(role='caregiver', is_active=True),
        required=False,
        label='照服員',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = PatientRecord
        fields = [
            'patient', 'medical_record_number', 'admission_date', 'discharge_date',
            'primary_diagnosis', 'secondary_diagnosis', 'status', 'allergies',
            'medical_history', 'emergency_contact_name', 'emergency_contact_phone',
            'case_manager', 'caregiver', 'notes'
        ]
        widgets = {
            'medical_record_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '例如：MR-2026-0001'}),
            'primary_diagnosis': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '主要診斷'}),
            'secondary_diagnosis': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'allergies': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': '藥物過敏、食物過敏等'}),
            'medical_history': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0912-345-678'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class MedicalRecordForm(forms.ModelForm):
    """Form for SOAP notes"""
    
    patient = forms.ModelChoiceField(
        queryset=User.objects.filter(role='patient', is_active=True),
        label='病患',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    record_date = forms.DateField(
        label='記錄日期',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    record_time = forms.TimeField(
        label='記錄時間',
        widget=forms.TimeInput(attrs={
            'type': 'time',
            'class': 'form-control'
        })
    )
    
    class Meta:
        model = MedicalRecord
        fields = [
            'patient', 'record_date', 'record_time', 'record_type',
            'chief_complaint', 'objective_findings', 'assessment', 'plan', 'diagnosis'
        ]
        widgets = {
            'record_type': forms.Select(attrs={'class': 'form-select'}),
            'chief_complaint': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '主訴 (Subjective)：病患的主觀症狀描述'
            }),
            'objective_findings': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '客觀發現 (Objective)：檢查結果、生命徵象等'
            }),
            'assessment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '評估 (Assessment)：診斷分析'
            }),
            'plan': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '計畫 (Plan)：治療計畫、處置方式'
            }),
            'diagnosis': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '診斷'}),
        }


class RehabPlanForm(forms.ModelForm):
    """Form for rehab plans"""
    
    patient = forms.ModelChoiceField(
        queryset=User.objects.filter(role='patient', is_active=True),
        label='病患',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    start_date = forms.DateField(
        label='開始日期',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    end_date = forms.DateField(
        required=False,
        label='結束日期',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    class Meta:
        model = RehabPlan
        fields = [
            'patient', 'plan_name', 'description', 'start_date', 'end_date',
            'goals', 'status', 'requires_robot', 'sessions_per_week',
            'duration_weeks', 'notes'
        ]
        widgets = {
            'plan_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '例如：下肢復健訓練計畫'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'goals': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '列出復健目標'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'requires_robot': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sessions_per_week': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '7'}),
            'duration_weeks': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class RehabSessionForm(forms.ModelForm):
    """Form for recording rehab sessions"""
    
    session_date = forms.DateField(
        label='療程日期',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    session_time = forms.TimeField(
        label='療程時間',
        widget=forms.TimeInput(attrs={
            'type': 'time',
            'class': 'form-control'
        })
    )
    
    class Meta:
        model = RehabSession
        fields = [
            'session_date', 'session_time', 'duration_minutes',
            'robot_used', 'robot_name', 'activities_performed',
            'patient_response', 'progress_score', 'completed', 'notes'
        ]
        widgets = {
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '240'}),
            'robot_used': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'robot_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '使用的機器人名稱'}),
            'activities_performed': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '執行的復健活動'}),
            'patient_response': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '病患反應與配合度'}),
            'progress_score': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '10'}),
            'completed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class VitalSignsForm(forms.ModelForm):
    """Form for recording vital signs"""
    
    patient = forms.ModelChoiceField(
        queryset=User.objects.filter(role='patient', is_active=True),
        label='病患',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    recorded_at = forms.DateTimeField(
        label='記錄時間',
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control'
        })
    )
    
    class Meta:
        model = VitalSigns
        fields = [
            'patient', 'recorded_at', 'systolic_bp', 'diastolic_bp',
            'heart_rate', 'respiratory_rate', 'temperature', 'spo2',
            'weight', 'height', 'notes'
        ]
        widgets = {
            'systolic_bp': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'mmHg', 'min': '50', 'max': '250'}),
            'diastolic_bp': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'mmHg', 'min': '30', 'max': '150'}),
            'heart_rate': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'bpm', 'min': '30', 'max': '200'}),
            'respiratory_rate': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'breaths/min', 'min': '8', 'max': '40'}),
            'temperature': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°C', 'step': '0.1', 'min': '35', 'max': '42'}),
            'spo2': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '%', 'min': '70', 'max': '100'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'kg', 'step': '0.1'}),
            'height': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'cm', 'step': '0.1'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class MedicationForm(forms.ModelForm):
    """Form for medication orders"""
    
    patient = forms.ModelChoiceField(
        queryset=User.objects.filter(role='patient', is_active=True),
        label='病患',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    start_date = forms.DateField(
        label='開始日期',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    end_date = forms.DateField(
        required=False,
        label='結束日期',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    class Meta:
        model = Medication
        fields = [
            'patient', 'medication_name', 'dosage', 'route', 'frequency',
            'start_date', 'end_date', 'status', 'indication', 'special_instructions'
        ]
        widgets = {
            'medication_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '藥品名稱'}),
            'dosage': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '例如：500mg'}),
            'route': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '例如：口服、靜脈注射'}),
            'frequency': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'indication': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': '用藥原因'}),
            'special_instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': '特殊注意事項'}),
        }


class NursingNoteForm(forms.ModelForm):
    """Form for nursing notes"""
    
    patient = forms.ModelChoiceField(
        queryset=User.objects.filter(role='patient', is_active=True),
        label='病患',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    note_datetime = forms.DateTimeField(
        label='記錄時間',
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control'
        })
    )
    
    class Meta:
        model = NursingNote
        fields = [
            'patient', 'note_datetime', 'note_type',
            'assessment', 'intervention', 'evaluation'
        ]
        widgets = {
            'note_type': forms.Select(attrs={'class': 'form-select'}),
            'assessment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '評估'}),
            'intervention': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '護理措施'}),
            'evaluation': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '評值'}),
        }


class CarePlanForm(forms.ModelForm):
    """Form for care plans"""
    
    patient = forms.ModelChoiceField(
        queryset=User.objects.filter(role='patient', is_active=True),
        label='病患',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    period_start = forms.DateField(
        label='開始日期',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    period_end = forms.DateField(
        required=False,
        label='結束日期',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    class Meta:
        model = CarePlan
        fields = [
            'patient', 'title', 'description', 'period_start',
            'period_end', 'status'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '照護計畫名稱'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': '照護計畫說明'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class CarePlanGoalForm(forms.ModelForm):
    """Form for care plan goals"""
    
    target_date = forms.DateField(
        required=False,
        label='目標日期',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    class Meta:
        model = CarePlanGoal
        fields = ['description', 'target_date', 'achievement_status', 'priority', 'notes']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '目標描述'}),
            'achievement_status': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '10'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class CareRecordForm(forms.ModelForm):
    """Form for care records"""
    
    patient = forms.ModelChoiceField(
        queryset=User.objects.filter(role='patient', is_active=True),
        label='病患',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    record_date = forms.DateField(
        label='記錄日期',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    record_time = forms.TimeField(
        label='記錄時間',
        widget=forms.TimeInput(attrs={
            'type': 'time',
            'class': 'form-control'
        })
    )
    
    class Meta:
        model = CareRecord
        fields = [
            'patient', 'record_date', 'record_time', 'activity_type',
            'duration_minutes', 'description', 'patient_response'
        ]
        widgets = {
            'activity_type': forms.Select(attrs={'class': 'form-select'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '480', 'placeholder': '分鐘'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '活動說明'}),
            'patient_response': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '病患反應'}),
        }


class IncidentReportForm(forms.ModelForm):
    """Form for incident reports"""
    
    patient = forms.ModelChoiceField(
        queryset=User.objects.filter(role='patient', is_active=True),
        label='病患',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    incident_datetime = forms.DateTimeField(
        label='事件發生時間',
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control'
        })
    )
    
    notified_staff = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(
            is_active=True,
            role__in=['admin', 'doctor', 'nurse', 'case_manager']
        ),
        required=False,
        label='通知人員',
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': '5'})
    )
    
    class Meta:
        model = IncidentReport
        fields = [
            'patient', 'incident_datetime', 'incident_type', 'severity',
            'description', 'immediate_action', 'location', 'notified_staff', 'status'
        ]
        widgets = {
            'incident_type': forms.Select(attrs={'class': 'form-select'}),
            'severity': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': '詳細描述事件經過'}),
            'immediate_action': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '已採取的立即處置'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '發生地點'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class EquipmentForm(forms.ModelForm):
    """Form for equipment"""
    
    purchase_date = forms.DateField(
        required=False,
        label='購買日期',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    last_maintenance_date = forms.DateField(
        required=False,
        label='最後維護日期',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    next_maintenance_date = forms.DateField(
        required=False,
        label='下次維護日期',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    class Meta:
        model = Equipment
        fields = [
            'equipment_name', 'equipment_type', 'manufacturer', 'model_number',
            'serial_number', 'purchase_date', 'last_maintenance_date',
            'next_maintenance_date', 'status', 'location', 'notes'
        ]
        widgets = {
            'equipment_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '設備名稱'}),
            'equipment_type': forms.Select(attrs={'class': 'form-select'}),
            'manufacturer': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '製造商'}),
            'model_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '型號'}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '序號'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '存放位置'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class EquipmentReservationForm(forms.ModelForm):
    """Form for equipment reservations"""
    
    equipment = forms.ModelChoiceField(
        queryset=Equipment.objects.filter(status='available'),
        label='設備',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    patient = forms.ModelChoiceField(
        queryset=User.objects.filter(role='patient', is_active=True),
        required=False,
        label='病患',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    reservation_date = forms.DateField(
        label='預約日期',
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
        model = EquipmentReservation
        fields = [
            'equipment', 'patient', 'reservation_date', 'start_time',
            'end_time', 'purpose', 'status', 'notes'
        ]
        widgets = {
            'purpose': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '使用目的'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if start_time and end_time and end_time <= start_time:
            raise ValidationError('結束時間必須晚於開始時間')
        
        return cleaned_data


# Filter Forms

class PatientFilterForm(forms.Form):
    """Form for filtering patients"""
    
    status = forms.ChoiceField(
        required=False,
        choices=[('', '全部')] + PatientRecord.STATUS_CHOICES,
        label='狀態',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    case_manager = forms.ModelChoiceField(
        queryset=User.objects.filter(role='case_manager', is_active=True),
        required=False,
        label='個管師',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    caregiver = forms.ModelChoiceField(
        queryset=User.objects.filter(role='caregiver', is_active=True),
        required=False,
        label='照服員',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    search = forms.CharField(
        required=False,
        label='搜尋',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '姓名、病歷號'
        })
    )