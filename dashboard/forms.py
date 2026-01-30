from django import forms
from django.core.exceptions import ValidationError
from .models import Shift
from account.models import User


class ShiftForm(forms.ModelForm):
    """Form for creating and editing shifts"""
    
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True, role__in=['doctor', 'therapist', 'nurse', 'case_manager', 'caregiver']),
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
            ('case_manager', '個管師'),
            ('caregiver', '照服員'),
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
        queryset=User.objects.filter(is_active=True, role__in=['doctor', 'therapist', 'nurse', 'case_manager', 'caregiver']),
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


class UserManagementForm(forms.ModelForm):
    """Form for admin to create/edit users"""
    
    email = forms.EmailField(
        required=False, 
        label='電子郵件',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'user@example.com'
        })
    )
    
    first_name = forms.CharField(
        max_length=30, 
        required=False, 
        label='名字',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '名字'
        })
    )
    
    last_name = forms.CharField(
        max_length=30, 
        required=False, 
        label='姓氏',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '姓氏'
        })
    )
    
    phone_number = forms.CharField(
        max_length=20, 
        required=False, 
        label='電話',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '0912-345-678'
        })
    )
    
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        label='角色',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    is_active = forms.BooleanField(
        required=False,
        initial=True,
        label='啟用',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number', 'role', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '使用者帳號'
            })
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            existing_user = User.objects.filter(email=email).exclude(pk=self.instance.pk).first()
            if existing_user:
                raise ValidationError('此電子郵件已被使用')
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        existing_user = User.objects.filter(username=username).exclude(pk=self.instance.pk).first()
        if existing_user:
            raise ValidationError('此使用者名稱已被使用')
        return username


class UserCreateForm(UserManagementForm):
    """Form for creating new users with password"""
    
    password1 = forms.CharField(
        label='密碼',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '請輸入密碼',
            'autocomplete': 'new-password'
        })
    )
    
    password2 = forms.CharField(
        label='確認密碼',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '請再次輸入密碼',
            'autocomplete': 'new-password'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Disable autocomplete for all fields in create form
        for field_name, field in self.fields.items():
            if field_name == 'username':
                field.widget.attrs['autocomplete'] = 'off'
            elif field_name == 'email':
                field.widget.attrs['autocomplete'] = 'off'
            elif field_name in ['first_name', 'last_name']:
                field.widget.attrs['autocomplete'] = 'off'
            elif field_name == 'phone_number':
                field.widget.attrs['autocomplete'] = 'off'
    
    class Meta(UserManagementForm.Meta):
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number', 'role', 'is_active', 'password1', 'password2']
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError('兩次輸入的密碼不一致')
        return password2
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class UserFilterForm(forms.Form):
    """Form for filtering users"""
    
    role = forms.ChoiceField(
        choices=[('', '所有角色')] + list(User.ROLE_CHOICES),
        required=False,
        label='角色',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    is_active = forms.ChoiceField(
        choices=[('', '全部'), ('1', '啟用'), ('0', '停用')],
        required=False,
        label='狀態',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    search = forms.CharField(
        required=False,
        label='搜尋',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '搜尋使用者名稱或姓名...'
        })
    )


class PasswordResetFormAdmin(forms.Form):
    """Form for admin to reset user password"""
    
    new_password1 = forms.CharField(
        label='新密碼',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '請輸入新密碼'
        })
    )
    
    new_password2 = forms.CharField(
        label='確認新密碼',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '請再次輸入新密碼'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('new_password1')
        password2 = cleaned_data.get('new_password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError('兩次輸入的密碼不一致')
        
        return cleaned_data


class ShiftExcelUploadForm(forms.Form):
    """Form for uploading Excel file with shift schedules"""
    
    excel_file = forms.FileField(
        label='Excel 檔案',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.xlsx,.xls'
        }),
        help_text='請上傳 Excel 檔案 (.xlsx 或 .xls)'
    )
    
    def clean_excel_file(self):
        file = self.cleaned_data.get('excel_file')
        if file:
            # Check file extension
            if not file.name.endswith(('.xlsx', '.xls')):
                raise ValidationError('請上傳 Excel 檔案 (.xlsx 或 .xls)')
            
            # Check file size (max 5MB)
            if file.size > 5 * 1024 * 1024:
                raise ValidationError('檔案大小不得超過 5MB')
        
        return file