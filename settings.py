# Django settings for every_resources project.
from django.conf import global_settings

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

import os

BASE_DIR = os.path.dirname(__file__)


DATABASE_ENGINE = 'mysql'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'tsuyukimakoto'             # Or path to database file if using sqlite3.
DATABASE_ENGINE = 'sqlite3'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'test.data'             # Or path to database file if using sqlite3.
DATABASE_USER = 'tsuyukimakoto'             # Not used with sqlite3.
DATABASE_PASSWORD = 'tsuyukimakoto'         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Japan'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'ja'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(BASE_DIR, 'everes_theme_default/templates/static/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/static/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '7(akr)kbm!7(+994q+kv2gh+9&5q%c5m%*0&#6!lhct*1n_(!w'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    #'everes_core.utils.DBDebugMiddleware',
)

ROOT_URLCONF = 'django-every_resources.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.markup',
    'django.contrib.flatpages',
    'django.contrib.admindocs',
    'everes_core',
    'everes_functional_workflow',
    'everes_functional_feed',
    'everes_blog',
    'everes_event',
    'everes_diigo',
    'everes_magnolia',
    'everes_photo',
    'everes_project',
    'everes_note',
    'everes_release',
    'everes_theme_sea',
    'everes_theme_default',
)

AUTH_PROFILE_MODULE = 'everes_core.cmsUserprofile'

TEMPLATE_CONTEXT_PROCESSORS = global_settings.TEMPLATE_CONTEXT_PROCESSORS + (
    'everes_core.context_processors.site',
    'everes_core.context_processors.api_keys',
    'everes_core.context_processors.everes_apps',
    'everes_core.context_processors.everes_tags',
    'everes_core.context_processors.everes_days',
    'everes_core.context_processors.everes_root_template',
)

GOOGLE_API_KEY = 'ABQIAAAAqqFWuvyrfIOifreBS0pD6BQCULP4XOMyhPd8d_NrQQEO8sT8XBTc4moQjlQsvb09T-mbSfECKD_dzQ'
GOOGLE_ANALYTICS = None
GOOGLE_SEARCH    = None
GOOGLE_ADSENSE   = None
GOOGLE_AD_SLOT   = None

RESTRUCTUREDTEXT_FILTER_SETTINGS = {
    'doctitle_xform': False,
}

PAGENT_BY = 10

USE_WORKFLOW = 'everes_functional_workflow' in INSTALLED_APPS or False
# minutes that limit user feedback.
FEEDBACK_UUID_TIMEOUT = 5

#### photo settings ####
ADDITIONAL_IMAGES = (('thumb', (128,128)), ('listing', (320, 80)), )

