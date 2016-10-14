# -*- coding: utf-8 -*-
# Django settings for a Codespeed project.
import os

import dj_database_url


DEBUG = True
TEMPLATE_DEBUG = DEBUG

BASEDIR = os.path.abspath(os.path.dirname(__file__))
TOPDIR = os.path.split(BASEDIR)[1]

#: The directory which should contain checked out source repositories:
REPOSITORY_BASE_PATH = os.path.join(BASEDIR, "repos")

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS
DATABASES = {
    'default': dj_database_url.config(default="sqlite:///{}".format(os.path.join(os.path.dirname(BASEDIR), 'dev.db')))
}

TIME_ZONE = 'Europe/Berlin'

LANGUAGE_CODE = 'en-us'

SITE_ID = 1

USE_I18N = False

USE_TZ = True

MEDIA_ROOT = os.path.join(BASEDIR, "media")

MEDIA_URL = '/media/'

ADMIN_MEDIA_PREFIX = '/static/admin/'

SECRET_KEY = 'ajsdklfjalksdfjalskdjfalksdf'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

if DEBUG:
    import traceback
    import logging

    # Define a class that logs unhandled errors
    class LogUncatchedErrors:
        def process_exception(self, request, exception):
            logging.error("Unhandled Exception on request for %s\n%s",
                          request.build_absolute_uri(), traceback.format_exc())
    # And add it to the middleware classes
    MIDDLEWARE_CLASSES += ('codespeed_project.settings.LogUncatchedErrors',)

    # set shown level of logging output to debug
    logging.basicConfig(level=logging.DEBUG)

ROOT_URLCONF = '{0}.urls'.format(TOPDIR)

TEMPLATE_DIRS = (
    os.path.join(BASEDIR, 'templates'),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.request',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'django_rq',
    'django_extensions',
    'codespeed',
    'github_integration',
)

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASEDIR, "sitestatic")
STATICFILES_DIRS = (
    os.path.join(BASEDIR, 'static'),
)

RQ_QUEUES = {
    'default': {
        'HOST': os.getenv('REDIS_HOST', 'localhost'),
        'PORT': 6379,
        'DB': 0,
    },
    'jobs': {
        'HOST': os.getenv('REDIS_HOST', 'localhost'),
        'PORT': 6379,
        'DB': 0,
        'DEFAULT_TIMEOUT': 1200,
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'loggers': {
        'root': {
            'level': 'DEBUG',
        },
        'django.db.backends': {
            'level': 'INFO'
        },
        'requests.packages.urllib3': {
            'level': 'WARNING'
        },
        'docker.auth': {
            'level': 'INFO'
        },
    }
}

GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
GITHUB_CLIENT_ID = os.environ.get('GITHUB_CLIENT_ID')
GITHUB_CLIENT_SECRET = os.environ.get('GITHUB_CLIENT_SECRET')
BASE_URL = os.environ.get('BASE_URL', '') + "/{}"

TMP_DIR = os.environ.get('TMP_DIR')

# Codespeed settings that can be overwritten here.
from codespeed.settings import *
try:
    from local_settings import *
except ImportError:
    pass
