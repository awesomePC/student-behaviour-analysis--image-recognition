"""
Django settings for image_recognition_project project.

Generated by 'django-admin startproject' using Django 2.2.0

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '43)%4yx)aa@a=+_c(fn&kf3g29xax+=+a&key9i=!98zyim=8j'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', '*']


# Application definition

CORE_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
)

THIRD_PARTY_APPS = (
    'allauth',
    'allauth.account',
    'lazysignup',
    'crispy_forms',
    'widget_tweaks',
    'notifications',
    'django_extensions',
    'debug_toolbar',
    'django_cleanup', # should go after your apps
    'django_celery_beat',
)

OUR_APPS = (
    'users',
    'misc',
    'exam',
    'candidate',
    'recognize',
    'superadmin',
    'proctor',
)

INSTALLED_APPS = CORE_APPS + THIRD_PARTY_APPS + OUR_APPS


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'image_recognition_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
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

WSGI_APPLICATION = 'image_recognition_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }

DATABASES = {
    'default':{
        'ENGINE':'django.db.backends.postgresql_psycopg2',
        'NAME':'image_recognition',
        'USER':'postgres',
        'PASSWORD':'postgres',
        'HOST':'localhost',
        'POST':'5432',
        'ATOMATIC_REQUESTS':True,
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 6,
        }
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static")
]

# Media files( Uploaded images )

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = '/media/'


SITE_ID = 1

AUTH_USER_MODEL = 'users.CustomUser'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

LOGIN_REDIRECT_URL = '/' # /users/handle_login/
ACCOUNT_LOGOUT_REDIRECT_URL = '/accounts/login/'

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
    'lazysignup.backends.LazySignupBackend',
)

# CRISPY forms
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Enabled for django-debug-toolbar to work
INTERNAL_IPS = ['127.0.0.1']


# Django-Allauth Config
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True

## extend sign-up form
# ACCOUNT_FORMS = {
#     'signup': 'users.forms.CustomUserCreationForm',
# }


#logging config

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        "brief": {
            "class": "logging.Formatter",
            "datefmt": "%I:%M:%S",
            "format": "%(levelname)-8s; %(name)-15s; %(message)s"
        },
        "single-line": {
            "class": "logging.Formatter",
            "datefmt": "%I:%M:%S",
            "format": "%(asctime)s - %(levelname)s - %(name)s - %(funcName)s:%(lineno)d - %(message)s",
            "_comment": "%(asctime)s — %(name)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)-- "
        },
        "multi-process": {
            "class": "logging.Formatter",
            "datefmt": "%I:%M:%S",
            "format": "%(levelname)-8s; [%(process)d]; %(name)-15s; %(module)s:%(funcName)s;%(lineno)d: %(message)s"
        },
        "multi-thread": {
            "class": "logging.Formatter",
            "datefmt": "%I:%M:%S",
            "format": "%(levelname)-8s; %(threadName)s; %(name)-15s; %(module)s:%(funcName)s;%(lineno)d: %(message)s"
        },
        "verbose": {
            "class": "logging.Formatter",
            "datefmt": "%I:%M:%S",
            "format": "%(levelname)-8s; [%(process)d]; %(threadName)s; %(name)-15s; %(module)s:%(funcName)s;%(lineno)d: %(message)s"
        },
        "multiline": {
            "class": "logging.Formatter",
            "_comment": "Level: %(levelname)s\nTime: %(asctime)s\nProcess: %(process)d\nThread: %(threadName)s\nLogger: %(name)s\nPath: %(module)s:%(lineno)d\nFunction :%(funcName)s\nMessage: %(message)s\n",
            "format": "Level: %(levelname)s\nTime: %(asctime)s\nLogger: %(name)s\nPath: %(module)s:%(lineno)d\nFunction :%(funcName)s\nMessage: %(message)s\n"
        },
        'verbose_min': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        "file_handler": {
            "level": "DEBUG",
            "class": "logging.handlers.WatchedFileHandler",
            "formatter": "verbose",
            "filename": "logs/logger.txt",
            "mode": "w",
            "encoding": "utf-8"
        },
        "rotating_file_handler": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "multiline",
            "filename": "logs/rotating_logger.html",
            "mode": "a",
            "maxBytes": 5000000,
            "backupCount": 100,
            "encoding": "utf-8"
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        }
    },
    'loggers': {
        '': {
            'level': 'DEBUG',
            'handlers': ['console']
        },
        # 'django': {
        #     'handlers': ['console'],
        #     'propagate': False,
        # },
        # 'django.request': {
        #     'handlers': ['mail_admins'],
        #     'level': 'ERROR',
        #     # required to avoid double logging with root logger
        #     'propagate': False,
        # },
        # 'appname': {
        #     'handlers': ['console', 'mail_admins'],
        #     'level': 'INFO',
        #     'filters': ['special']
        # },
    }
}

##
# Django Notifications
##
DJANGO_NOTIFICATIONS_CONFIG = { 'SOFT_DELETE': True}

#You can attach arbitrary data to your notifications by doing the following:
DJANGO_NOTIFICATIONS_CONFIG = { 'USE_JSONFIELD': True}


# face recognition and emotion detection API base url
FACE_RECOGNITION_BASE_API_URL = "http://localhost:5001/"
EMOTION_DETECTION_BASE_API_URL = "http://localhost:5002/"


# celery
CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'

# The following lines may contains pseudo-code
from celery.schedules import crontab, timedelta

CELERY_BEAT_SCHEDULE = {
    'emotion_recognition': {
        'task': 'recognize.tasks.do_emotion_recognition',
        'schedule': timedelta(seconds=1150), # Periodic Tasks

        # If you want more control over when the task is executed, for example, a particular time of day or day of the week, you can use the crontab schedule type:
        # 'schedule': crontab(hour=1, minute=57), # Crontab schedules
    },
    'object_detection': {
        'task': 'recognize.tasks.do_object_detection',
        'schedule': timedelta(seconds=50), # Periodic Tasks

        # If you want more control over when the task is executed, for example, a particular time of day or day of the week, you can use the crontab schedule type:
        # 'schedule': crontab(hour=1, minute=57), # Crontab schedules
    },
}

# Many of these will be overridden by local settings.
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# CELERY_RESULT_EXPIRES = 60 * 60 * 24  # store results for 1 day
# CELERY_TASK_ALWAYS_EAGER = True
# CELERY_TASK_EAGER_PROPAGATES = True
# CELERY_WORKER_HIJACK_ROOT_LOGGER = False
# CELERY_TASK_ACKS_LATE = True  # Retry if task fails
# CELERY_TASK_TIME_LIMIT = 60 * 25  # in seconds, so 25 minutes
# CELERY_SEND_TASK_ERROR_EMAILS = True
# CELERY_WORKER_MAX_TASKS_PER_CHILD = 300


import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="https://e2932749492e4c00af282eb8f12b4282@sentry.io/1871868",
    integrations=[DjangoIntegration()],

    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True
)
