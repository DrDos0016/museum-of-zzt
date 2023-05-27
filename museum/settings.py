import os
import sys
import mimetypes
mimetypes.add_type("application/wasm", ".wasm", True)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get("MOZ_DB_NAME", "museum_of_zzt"),
        'USER': os.environ.get("MOZ_DB_USER", "root"),
        'PASSWORD': os.environ.get("MOZ_DB_PASS", ""),
        'HOST': os.environ.get("MOZ_DB_HOST", ""),
        'PORT': os.environ.get("MOZ_DB_PORT", ""),
    }
}

SECRET_KEY = os.environ.get("MOZ_SECRET_KEY", "!c;LOCKED FILE")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ENVIRONMENT = os.environ.get("MOZ_ENVIRONMENT", "DEV")  # Valid options: DEV, BETA, PROD

DEBUG = True if (ENVIRONMENT == "DEV") else False

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
    "10.0.0.98",
    "kudzu.museumofzzt.com",
]


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "museum_site",
    "comic",
    "poll",
    "museum_api",
    "zap",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "museum_site.middleware.beta_password_check_middleware.Beta_Password_Check_Middleware",
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
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = False

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = "login_user"

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'moz-cache-1',
        'TIMEOUT': None
    }
}

DATE_FORMAT = "M j, Y"
