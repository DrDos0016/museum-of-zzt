import os
import sys
import mimetypes
mimetypes.add_type("application/wasm", ".wasm", True)

try:
    from .private import DATABASES
except ImportError:
    error = """ERROR: Database settings not found.
Make sure museum/private.py exists and contains a DATABASE variable that
matches Django's configuration format.

See: https://docs.djangoproject.com/en/3.0/ref/settings/#databases"
"""
    print(error)
    sys.exit()

try:
    from .private import SECRET_KEY
except ImportError:
    error = """ERROR: SECRET_KEY not found.
Make sure museum/private.py exists and contains a SECRET_KEY variable that
matches Django's configuration format.

See: https://docs.djangoproject.com/en/3.0/ref/settings/#std:setting-SECRET_KEY
"""
    print(error)
    sys.exit()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True if os.path.isfile(os.path.join(BASE_DIR, "DEV")) else False

ALLOWED_HOSTS = [
    "django.pi",
    "z2.pokyfriends.com",
    "museum.pokyfriends.com",
    "museumofzzt.com",
    "www.museumofzzt.com",
    "openbeta.museumofzzt.com",
    "merbotia.museumofzzt.com",
    "beta.museumofzzt.com",
    "api.museumofzzt.com",
    "192.168.1.66",
    "169.254.242.177",
    "10.42.0.1",
    "127.0.0.1",
    "testserver",
    "10.0.0.101",
]


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "markdown_deux",
    "museum_site",
    "comic",
    "poll",
    "museum_api",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'museum.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ["templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'museum_site.context_processors.museum_global'
            ],
        },
    },
]

WSGI_APPLICATION = 'museum.wsgi.application'


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = "login_user"
