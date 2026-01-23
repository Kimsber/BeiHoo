from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, UserLoginForm
from .models import AuditLog

def get_client_ip(request):
    """取得客戶端 IP"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def register_view(request):
    """使用者註冊"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # 記錄註冊
            AuditLog.objects.create(
                user=user,
                action='create',
                resource_type='User',
                resource_id=str(user.id),
                ip_address=get_client_ip(request),
                details=f'新使用者註冊: {user.username}'
            )
            
            # 自動登入
            login(request, user)
            messages.success(request, f'歡迎 {user.get_full_name()}！註冊成功。')
            return redirect('home')
        else:
            messages.error(request, '註冊失敗，請檢查輸入的資料。')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'account/register.html', {'form': form})


def login_view(request):
    """使用者登入"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # 記錄登入
            AuditLog.objects.create(
                user=user,
                action='login',
                ip_address=get_client_ip(request),
                details=f'使用者登入: {user.username}'
            )
            
            messages.success(request, f'歡迎回來，{user.get_full_name()}！')
            
            # 檢查是否有 next 參數
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('home')
        else:
            messages.error(request, '登入失敗，請檢查使用者名稱和密碼。')
    else:
        form = UserLoginForm()
    
    return render(request, 'account/login.html', {'form': form})


@login_required
def logout_view(request):
    """使用者登出"""
    # 記錄登出
    AuditLog.objects.create(
        user=request.user,
        action='logout',
        ip_address=get_client_ip(request),
        details=f'使用者登出: {request.user.username}'
    )
    
    logout(request)
    messages.info(request, '您已成功登出。')
    return redirect('login')


@login_required
def profile_view(request):
    """個人資料頁面"""
    return render(request, 'account/profile.html', {'user': request.user})


@login_required
def home_view(request):
    """首頁 - 根據角色顯示不同內容"""
    return render(request, 'home.html', {'user': request.user})