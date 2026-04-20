import os
import logging
from pathlib import Path
from dotenv import load_dotenv, dotenv_values


"""
        Sistema web desenvolvido para suprir as necessidades de uma enfermaria escolar típica.

        A necessidade do desenvolvimento do sistema surgiu devido à falta de um sistema de gestão para os atendimentos,
        Fazendo que fosse necessário o uso de planilhas e papel para o controle dos atendimentos.

        O sistema foi desenvolvido com o intuito de facilitar o controle dos atendimentos, dos pacientes e do dia a dia das enfermeiras.

        A migração dos dados foi feita através da sincronização dos dados da planilha anterior e precisou de revisão e adequação. 
        Como anteriormente toda inserção de dados era feita manualmente, era passível de falha humana, portanto, 
        como migramos a planilha para o sistema, possíveis erros humanos foram migrados também.
        O desenvolvedor não se responsabiliza por possíveis inconsistências nos dados.


        O sistema possui quatro módulos principais: patients, appointments, controller e reports.

        Patients: Módulo responsável por conter funções, rotas e configurações de cadastro e controle dos dados dos pacientes.

        Appointments: Módulo responsável por conter funções, rotas e configurações de cadastro e controle dos atendimentos.

        Controller: Módulo responsável por conter funções, rotas e configurações de controles gerais do sistema e principalmente,
        as funções de comunicação com o banco de dados.

        Reports: Módulo responsável por conter funções, rotas e configurações de geração de relatórios.



"""



# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

LOGS_DIR = BASE_DIR / 'logs'


# Load environment variables
load_dotenv()

# dotenv_values() re-parseia o .env com strip correto de aspas e tratamento de #,
# necessário porque o Docker env_file interpreta # como comentário dentro de valores.
_dotenv = dotenv_values()
SECRET_KEY = _dotenv.get('DJANGO_SECRET_KEY') or os.getenv('DJANGO_SECRET_KEY', 'django-insecure-key-for-dev-only')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DJANGO_DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')


EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Application definition

INSTALLED_APPS = [
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # REST Framework
    'rest_framework',

    # CORS
    'corsheaders',

    # Swagger
    'drf_spectacular',

    # Project apps
    'authentication.apps.AuthenticationConfig',
    'appointments.apps.AppointmentsConfig',
    'patients.apps.PatientsConfig',
    'reports.apps.ReportsConfig',
    'imports.apps.ImportsConfig',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# CORS — origens permitidas para o frontend React (Fase 4)
CORS_ALLOWED_ORIGINS = os.getenv(
    'CORS_ALLOWED_ORIGINS',
    'http://localhost:3000,http://127.0.0.1:3000',
).split(',')

# Django REST Framework + JWT
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'School Infirmary API',
    'DESCRIPTION': 'API REST para gestão de atendimentos da enfermaria escolar.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=8),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': False,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

ROOT_URLCONF = 'setup.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'setup.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
     'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'ENFERMARIA_DB'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'postgres'),
        'HOST': os.getenv('DB_HOST', '127.0.0.1'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

def create_log_dirs():
    app_dirs = ['patients', 'appointments', 'reports', 'imports', 'authentication']
    for app in app_dirs:
        dir_path = LOGS_DIR / app
        if not dir_path.exists():
            os.makedirs(dir_path)

# Crie os diretórios antes de configurar o logging
create_log_dirs()


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        # Handlers app patients
        'patients_api_views_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': LOGS_DIR / 'patients' / 'api_views.log',
            'formatter': 'verbose',
        },
        'patients_services_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': LOGS_DIR / 'patients' / 'services.log',
            'formatter': 'verbose',
        },
        # Handlers app appointments
        'appointments_api_views_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': LOGS_DIR / 'appointments' / 'api_views.log',
            'formatter': 'verbose',
        },
        'appointments_services_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': LOGS_DIR / 'appointments' / 'services.log',
            'formatter': 'verbose',
        },
        # Handlers app reports
        'reports_api_views_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': LOGS_DIR / 'reports' / 'api_views.log',
            'formatter': 'verbose',
        },
        'reports_services_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': LOGS_DIR / 'reports' / 'services.log',
            'formatter': 'verbose',
        },
        'imports_services_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': LOGS_DIR / 'imports' / 'services.log',
            'formatter': 'verbose',
        },
        'imports_api_views_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': LOGS_DIR / 'imports' / 'api_views.log',
            'formatter': 'verbose',
        },
        # Handlers app authentication
        'authentication_services_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': LOGS_DIR / 'authentication' / 'services.log',
            'formatter': 'verbose',
        },
        'authentication_api_views_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': LOGS_DIR / 'authentication' / 'api_views.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        # Loggers app patients
        'patients.api_views': {
            'handlers': ['patients_api_views_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'patients.services': {
            'handlers': ['patients_services_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        # Loggers app appointments
        'appointments.api_views': {
            'handlers': ['appointments_api_views_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'appointments.services': {
            'handlers': ['appointments_services_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        # Loggers app reports
        'reports.api_views': {
            'handlers': ['reports_api_views_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'reports.services': {
            'handlers': ['reports_services_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'imports.services': {
            'handlers': ['imports_services_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'imports.api_views': {
            'handlers': ['imports_api_views_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        # Loggers app authentication
        'authentication.services': {
            'handlers': ['authentication_services_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'authentication.api_views': {
            'handlers': ['authentication_api_views_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}







AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]


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

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/images/'

STATICFILES_DIRS = []

STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_ROOT = BASE_DIR /'images'


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'



# Auth redirect (Django admin)
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
