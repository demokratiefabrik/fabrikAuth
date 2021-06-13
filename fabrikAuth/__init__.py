# import os
# MODE = os.environ.get('MODE')
# if not MODE or MODE != "OAUTH":
from fabrikAuth.celery import app as celery_app
__all__ = ('celery_app',)