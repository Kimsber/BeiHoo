from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

class UserRegistrationForm(UserCreationForm):
    """使用者註冊表單"""
    
    email = forms.EmailField(
        required=True, 
        label='電子郵件',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    first_name = forms.CharField(
        max_length=30, 
        required=True, 
        label='名字',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True, 
        label='姓氏',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    phone_number = forms.CharField(
        max_length=20, 
        required=False, 
        label='電話',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    date_of_birth = forms.DateField(
        required=False, 
        label='生日',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    role = forms.ChoiceField(
        label='身份',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number', 
                  'date_of_birth', 'role', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 限制註冊時可選的角色
        self.fields['role'].choices = [
            ('patient', '病患'),
            ('doctor', '醫師'),
            ('therapist', '治療師'),
            ('nurse', '護理師'),
        ]
        self.fields['role'].initial = 'patient'
        
        # 添加 Bootstrap 樣式
        for field_name in ['username', 'password1', 'password2']:
            self.fields[field_name].widget.attrs['class'] = 'form-control'


class UserLoginForm(AuthenticationForm):
    """登入表單"""
    
    username = forms.CharField(
        label='使用者名稱',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '請輸入使用者名稱'
        })
    )
    password = forms.CharField(
        label='密碼',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '請輸入密碼'
        })
    )