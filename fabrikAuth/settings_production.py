"""
Settings Extension for PROD environment
"""

from get_docker_secret import get_docker_secret


SECURE_SSL_REDIRECT = False  # Produces redirection infinit loop! Why?
SECURE_REFERRER_POLICY = 'same-origin'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

STATIC_URL = 'https://www.demokratiefabrik.ch/fabrikauth/'
TOKEN_LOGIN_URL = 'https://www.demokratiefabrik.ch/l/%s'

TIME_ZONE = 'UTC'
LANGUAGE_CODE = 'de-ch'

USE_I18N = True
USE_L10N = True
USE_TZ = True

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

ADMINS = [('Dominik Wyss', 'demokratiefabrik.ipw@unibe.ch')]

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# added to redirect logs via gunicorn to docker. (and to admin emails...)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler'
        },
        'mail_admins': {
          'level': 'ERROR',
          'class': 'django.utils.log.AdminEmailHandler',
          'include_html': True,
        }
    },
    'loggers': {
        '': {  # 'catch all' loggers by referencing it with the empty string
            'handlers': ['console', 'mail_admins'],
            'level': 'ERROR',
        },
    },
}



# Celery Configuration Options: massmailer tasks
################################################
# 1) Configuration 
# eg: 'redis://localhost:6379/0'
# redis://:password@hostname:port/db_number
# redis://default:YBu...3o2@172.17.0.1:6379/0 
# 'redis://default:YBu...3o2@172.17.0.1:6379/0'
# NOTE: ENVIRONMENT VARIABLES ARE NOT VALID HERE: USED in backend processes! (yet, i dont know why, exactly:(
BROKER_URL = "redis://%s@%s" % (get_docker_secret('fabrikauth_redis_password', ''), get_docker_secret('fabrikauth_redis_url', ''))
CELERY_TIMEZONE = "Europe/Rome"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 3 * 10
CELERY_ACCEPT_CONTENT = ['pickle']
CELERY_TASK_SERIALIZER = 'pickle'
CELERY_RESULT_SERIALIZER = 'pickle'
CELEREY_BROKER_CONNECTION_MAX_RETRIES = 5
CELERY_REDIS_MAX_CONNECTIONS = 5
CELERY_RESULT_BACKEND = BROKER_URL
CELERY_BROKER_TRANSPORT_OPTIONS = {
    'max_retries': 10
}


OAUTH2_PROVIDER = {
    'PKCE_REQUIRED': True,
    'ACCESS_TOKEN_EXPIRE_SECONDS': 60*25,  # after  seconds a new token is to issue
    'ACCESS_TOKEN_GENERATOR': 'fabrikAuth.generators.generate_access_token',
    'REFRESH_TOKEN_GENERATOR': 'fabrikAuth.generators.generate_refresh_token',
    # 'CLIENT_ID_GENERATOR_CLASS': 'oauth2_provider.generators.ClientIdGenerator',
}