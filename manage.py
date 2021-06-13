#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
# from django.core import signals


# from django.http.response import HttpResponseBase

# class OverriddenHttpResponseBase:

#     @staticmethod
#     def close(self):
#         for closable in self._closable_objects:
#             try:
#                 closable.close()
#             except Exception:
#                 pass
#         self.closed = True
#         # here you can access your request using self._closable_objects 

#         # you can either send it to request_finished 
#         signals.request_finished.send(sender=<whatever data you want>)
#         # or code your stuff here without using request_finished at all

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fabrikAuth.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
