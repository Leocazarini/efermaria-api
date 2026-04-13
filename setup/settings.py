import os
import logging
from pathlib import Path
from dotenv import load_dotenv


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

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-key-for-dev-only')

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

    # Authentication apps

    'allauth',
    'allauth.account',
    'allauth.socialaccount',

    # Providers
    'allauth.socialaccount.providers.google',

    # Project apps
    'appointments.apps.AppointmentsConfig',
    'controller.apps.ControllerConfig',
    'patients.apps.PatientsConfig',
    'reports.apps.ReportsConfig',
]

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    "allauth.account.middleware.AccountMiddleware",
]

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
    app_dirs = {
        'patients': ['views', 'models'],
        'appointments': ['views', 'models'],
        'controller': ['crud'],
    }
    
    for app, modules in app_dirs.items():
        for module in modules:
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
        'patients_views_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': LOGS_DIR / 'patients' / 'views.log',
            'formatter': 'verbose',
        },
        'patients_models_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': LOGS_DIR / 'patients' / 'models.log',
            'formatter': 'verbose',
        },
        # Handlers app appointments
        'appointments_views_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': LOGS_DIR / 'appointments' / 'views.log',
            'formatter': 'verbose',
        },
        'appointments_models_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': LOGS_DIR / 'appointments' / 'models.log',
            'formatter': 'verbose',
        },
        # Handlers app controller
        'controller_crud_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': LOGS_DIR / 'controller' / 'crud.log',
            'formatter': 'verbose',
        },
        'controller_views_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': LOGS_DIR / 'controller' / 'views.log',
            'formatter': 'verbose',
        },
        'reports_views_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': LOGS_DIR / 'reports' / 'views.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        # Loggers app patients
        'patients.views': {
            'handlers': ['patients_views_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        # Loggers app appointments
        'appointments.views': {
            'handlers': ['appointments_views_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        # Loggers app controller
        'controller.crud': {
            'handlers': ['controller_crud_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'controller.views': {
            'handlers': ['controller_views_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'reports.views': {
            'handlers': ['reports_views_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}







AUTHENTICATION_BACKENDS = [
    
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by email
    'allauth.account.auth_backends.AuthenticationBackend',  
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

STATICFILES_DIRS = [
    BASE_DIR / 'staticfiles',
    ]

STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_ROOT = BASE_DIR /'images'


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'



# Allauth settings

ACCOUNT_EMAIL_VERIFICATION = 'none'
SOCIALACCOUNT_ONLY = True

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'


SOCIALACCOUNT_PROVIDERS = {
    "google": {
        
        "APPS": [
            {
                "client_id": os.getenv('GOOGLE_CLIENT_ID', ''),
                "secret": os.getenv('GOOGLE_SECRET', ''),
                "key": ""
            },
        ],
        # These are provider-specific settings that can only be
        # listed here:
        "SCOPE": [
            "profile",
            "email",
        ],
        "AUTH_PARAMS": {
            "access_type": "online",
        },
    }
}
