"""
Extension for test environment
"""
# TODO: set to true
SECURE_SSL_REDIRECT = False
SECURE_REFERRER_POLICY = 'same-origin'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Allowed host are hostnames and all docker containers:
ALLOWED_HOSTS = ['demokratiefabrik.sowi.unibe.ch'] + ['172.19.0.{}'.format(i) for i in range(20)]
  
TIME_ZONE = 'UTC'
LANGUAGE_CODE = 'de-ch'
USE_I18N = True
USE_L10N = True
USE_TZ = True

CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
