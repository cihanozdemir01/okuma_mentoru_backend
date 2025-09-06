# settings.py dosyasının en üstlerinde olmalı
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# BU ÇOK ÖNEMLİ! Django'nun senin için oluşturduğu gizli anahtarı sakın silme.
# Değeri uzun ve karmaşık bir şey olmalı.
SECRET_KEY = 'django-insecure-....senin-buradaki-değerin-farklı-olmalı....'

# Geliştirme aşamasında bu True olmalı.
DEBUG = True

# Geliştirme aşamasında boş bir liste olabilir.
ALLOWED_HOSTS = ['10.0.2.2', '127.0.0.1']

# --- PAYLAŞTIĞIN VE DOĞRU OLAN BÖLÜMLER ---

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'reading',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# -----------------------------------------------


# Bu satır, projenin ana URL dosyasının nerede olduğunu belirtir.
ROOT_URLCONF = 'config.urls'


# --- YİNE PAYLAŞTIĞIN VE DOĞRU OLAN BÖLÜMLER ---

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
# -----------------------------------------------

# Bu satır, web sunucusu entegrasyonu için gereklidir.
WSGI_APPLICATION = 'config.wsgi.application'


# --- Diğer Standart Ayarlar (Genellikle dosyanın en altında yer alır) ---

# Dil ve zaman ayarları
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Statik dosyaların (CSS, JavaScript, Resimler) URL'si
STATIC_URL = 'static/'

# Varsayılan primary key alanı türü
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'reading:login'