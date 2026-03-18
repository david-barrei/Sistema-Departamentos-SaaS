
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/



# SECURITY WARNING: keep the secret key used in production secret!
#SECRET_KEY = os.environ.get('SECRET_KEY')

SECRET_KEY ='django-insecure-nxoar!crwosl_pcu&k=4!+@z7040me-@q*t+1aj&-!+1vtevsd'
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition



TENANT_APPS =(
    'django.contrib.auth', #Gestiona usuarios unicos por cada tenant
    'django.contrib.contenttypes',
    'users',
    'bases',

    "properties",

    "leases.apps.LeasesConfig",
    "billing.apps.BillingConfig",
)

SHARED_APPS= (
    'django_tenants',
    'tenant',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users',
    'crispy_forms',
    'crispy_bootstrap5',
    'rest_framework',
    'django_filters',

)

INSTALLED_APPS = SHARED_APPS + tuple(app for app in TENANT_APPS if app not in SHARED_APPS)



MIDDLEWARE = [
    'django_tenants.middleware.main.TenantMainMiddleware',  # detecta el tenant activo según el dominio, antes de cada request.
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
   
    'users.middleware.FailedLoginMiddleware',
]

ROOT_URLCONF = 'app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
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

WSGI_APPLICATION = 'app.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

import os

DATABASES = {
    'default': {
        #'ENGINE': 'django.db.backends.postgresql',
        'ENGINE': 'django_tenants.postgresql_backend', #trabajar con diferentes esquemas, Sin esto, Django NO sabría cambiar de schema por tenant.
        'NAME': os.environ.get("POSTGRES_DB"),
         "USER":os.environ.get("POSTGRES_USER"),
         "PASSWORD":os.environ.get("POSTGRES_PASSWORD"),
         "HOST": "db",
         "PORT": "5432",
    }
}

print(os.environ.get("POSTGRES_DB"),"******")
# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'es-EC'
TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Subida de images
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / "static"
]

STATIC_ROOT = "/code/static_root"

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Indica a Django qué migraciones aplicar en cada lugar:
DATABASE_ROUTERS = (
    'django_tenants.routers.TenantSyncRouter', 
)

TENANT_MODEL = "tenant.Client"
TENANT_DOMAIN_MODEL = "tenant.Domain"

AUTH_USER_MODEL = 'users.CustomUser'

#CSRF_TRUSTED_ORIGINS = ['']

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/users/login/'
LOGIN_URL = '/users/login/'


# Definicion de paquetes de pantilla para crispy froms
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'


REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
}


