"""
Extension for dev environment
"""

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']
# TOKEN_LOGIN_URL = 'http://localhost/l/%s'

# STATIC_URL = 'http://localhost/'

TIME_ZONE = 'UTC'
LANGUAGE_CODE = 'de-ch'
USE_I18N = True
USE_L10N = True
USE_TZ = True

CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
CORS_ORIGIN_ALLOW_ALL = True


EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Celery /massmailer configuration
CELERY_ALWAYS_EAGER = True
CELERY_TIMEZONE = "Europe/Rome"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 3 * 10
CELERY_ACCEPT_CONTENT = ['pickle']
CELERY_TASK_SERIALIZER = 'pickle'
CELERY_RESULT_SERIALIZER = 'pickle'
CELEREY_BROKER_CONNECTION_MAX_RETRIES = 5
CELERY_REDIS_MAX_CONNECTIONS = 5
CELERY_BROKER_TRANSPORT_OPTIONS = {
    'max_retries': 10
}

OAUTH2_PROVIDER = {
    'PKCE_REQUIRED': True,
    'ACCESS_TOKEN_EXPIRE_SECONDS': 300,  # after  seconds a new token is to issue
    'ACCESS_TOKEN_GENERATOR': 'fabrikAuth.generators.generate_access_token',
    'REFRESH_TOKEN_GENERATOR': 'fabrikAuth.generators.generate_refresh_token',
    # 'CLIENT_ID_GENERATOR_CLASS': 'oauth2_provider.generators.ClientIdGenerator',
}
