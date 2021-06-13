"""
This subdirectory helps to avoid the cirular import of celery app and module...
"""
from __future__ import absolute_import
import os
from django.conf import settings
app = None
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fabrikAuth.settings')

MODE = os.environ.get('MODE')
if not MODE or MODE != "OAUTH":

    # prevent circular import: => ensure that sitepackage-celery is found first
    import sys
    import sysconfig
    pp = sysconfig.get_paths()['purelib']
    sys.path.insert(0, pp)
    # end circular life hack

    from celery import Celery
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fabrikAuth.settings')
    app = Celery('fabrikAuth')
    app.config_from_object(settings)
    app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
