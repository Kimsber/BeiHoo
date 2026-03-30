"""
Django settings for BeiHoo project - FHIR EHR Platform
"""

from pathlib import Path
import os
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent


def load_dotenv(dotenv_path):
    if not dotenv_path.exists():
        return

    for raw_line in dotenv_path.read_text(encoding='utf-8').splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue

        key, value = line.split('=', 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


load_dotenv(BASE_DIR / '.env')


def get_env(name, default=None, required=False):
    value = os.getenv(name, default)
    if required and (value is None or value == ''):
        raise ImproperlyConfigured(f"Missing required environment variable: {name}")
    return value

SECRET_KEY = get_env('SECRET_KEY', required=True)
DEBUG = get_env('DEBUG', default='False') == 'True'
ALLOWED_HOSTS = [h.strip() for h in get_env('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',') if h.strip()]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party
    'crispy_forms',
    'crispy_bootstrap5',
    
    # Local apps
    'account',
    'dashboard',
    'appointments',
    'clinical',
    'assessments',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'account.middleware.LoadtestSessionGateMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'BeiHoo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'BeiHoo.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': get_env('DB_NAME', required=True),
        'USER': get_env('DB_USER', required=True),
        'PASSWORD': get_env('DB_PASSWORD', required=True),
        'HOST': get_env('DB_HOST', default='localhost'),
        'PORT': get_env('DB_PORT', default='5432'),
    }
}

# Custom User Model
AUTH_USER_MODEL = 'account.User'

# Login/Logout URLs
LOGIN_URL = 'account:login'
LOGIN_REDIRECT_URL = 'dashboard:home'
LOGOUT_REDIRECT_URL = 'account:login'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'zh-hant'
TIME_ZONE = 'Asia/Taipei'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Load-test lockdown activation control
LOADTEST_LOCKDOWN_ENABLED = get_env('LOADTEST_LOCKDOWN_ENABLED', default='False') == 'True'
LOADTEST_USERNAME_PREFIX = get_env('LOADTEST_USERNAME_PREFIX', default='loadtest_').strip()
LOADTEST_ALLOWED_ROLES = [
    role.strip()
    for role in get_env('LOADTEST_ALLOWED_ROLES', default='admin,doctor,case_manager,caregiver').split(',')
    if role.strip()
]

# Role-based Dashboard Configuration
ROLE_DASHBOARD_MAP = {
    'admin': 'dashboard:admin',
    'doctor': 'dashboard:doctor',
    'therapist': 'dashboard:therapist',
    'nurse': 'dashboard:nurse',
    'case_manager': 'dashboard:case_manager',
    'caregiver': 'dashboard:caregiver',
    'patient': 'dashboard:patient',
    'researcher': 'dashboard:researcher',
}