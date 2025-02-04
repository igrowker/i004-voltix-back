"""
Django settings for site_app project.

Generated by 'django-admin startproject' using Django 5.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os 
from dotenv import load_dotenv

load_dotenv()


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['SECRET_KEY']

# Configuración de Celery y Redis
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_BROKER_URL =  os.environ['CELERY_BROKER_URL']  # Broker para gestionar las tareas
CELERY_RESULT_BACKEND =  os.environ['CELERY_RESULT_BACKEND']  # Backend para resultados de las tareas
CELERY_ACCEPT_CONTENT = ['json']  # Formato aceptado para mensajes
CELERY_TASK_SERIALIZER = 'json'  # Serializador para tareas
CELERY_TIMEZONE = 'UTC'  # Zona horaria
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True


# for production we will need to change it
#CORS_ALLOW_ALL_ORIGINS = os.getenv('CORS_ALLOW_ALL_ORIGINS', 'False') == 'True'
# CORS_ALLOW_ALL_ORIGINS = os.getenv('CORS_ALLOW_ALL_ORIGINS')
CORS_ALLOW_ALL_ORIGINS = os.getenv("CORS_ALLOW_ALL_ORIGINS", "False").lower() in ("true", "1", "t", "yes")

CORS_ALLOW_METHODS = [
    "GET",
    "POST",
    "PUT",
    "DELETE",
    "OPTIONS",
    "PATCH",
]

CORS_ALLOW_HEADERS = [
    "Content-Type",
    "Authorization",
    "X-Requested-With",
]


# CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",")



# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ['DEBUG']

ALLOWED_HOSTS = ['*']

AUTH_USER_MODEL = 'voltix.User'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tesseract',
    'corsheaders',

    #apps nuestras
    'voltix',
    'authentication',
    'invoices',
    'measurements',
    'notifications',
    'userprofile',
    'users',
    'pdf_measurement',
    'notify_service',

   #apps externas 
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'drf_yasg',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

ROOT_URLCONF = 'site_app.urls'

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

WSGI_APPLICATION = 'site_app.wsgi.application'



from pathlib import Path

schema = os.environ.get('DB_SCHEMA', "public") # si no encuentra el schema enviado por el .env, es publico por defecto

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'OPTIONS': {
             'options': f'-c search_path={schema}'  # Usar un schema diferente
         },
        'NAME': os.environ['DB_NAME'],  # Base de datos de desarrollo
        'USER': os.environ['DB_USER'],
        'PASSWORD': os.environ['DATABASE_PASSWORD'],
        'HOST': os.environ['DB_HOST'],
        'PORT': int(os.environ['DB_PORT']),
        'CONN_MAX_AGE': 0,  # Deshabilita conexiones persistentes
        
    }
}



AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'static') # agregamos static para el admin en docker:
STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

from .drf_settings import REST_FRAMEWORK, SIMPLE_JWT



################################################################################################################################
########################################### CONFIG PARA EL EMAIL DE BACKEND ####################################################
################################################################################################################################

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'voltix899@gmail.com'  # Tu dirección de correo de Gmail
EMAIL_HOST_PASSWORD = 'jyja gtns fxpu ntfl'  # La password de la APP de Voltix en Gmail

################################################################################################################################

# TEMP_FOLDER = os.path.join(BASE_DIR, 'temp_uploads')


#Base directory for the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Media root (default to 'media/' in BASE_DIR if not set in .env)
MEDIA_ROOT = os.getenv('MEDIA_ROOT', os.path.join(BASE_DIR, 'media'))

# Temporary file upload directory (default to 'temp/' in MEDIA_ROOT if not set in .env)
FILE_UPLOAD_TEMP_DIR = os.getenv('FILE_UPLOAD_TEMP_DIR', os.path.join(MEDIA_ROOT, 'temp'))

# Ensure directories exist (automatic creation if missing)
os.makedirs(MEDIA_ROOT, exist_ok=True)
os.makedirs(FILE_UPLOAD_TEMP_DIR, exist_ok=True)

# URL for serving media files in development
MEDIA_URL = '/media/'

# Configuración de Cloudinary (site_app setting)
CLOUDINARY = {
    'cloud_name': os.getenv('CLOUDINARY_CLOUD_NAME'),
    'api_key': os.getenv('CLOUDINARY_API_KEY'),
    'api_secret': os.getenv('CLOUDINARY_API_SECRET'),
}




