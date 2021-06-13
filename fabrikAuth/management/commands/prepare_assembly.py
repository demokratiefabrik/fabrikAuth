from django.db import connection
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Setups permissions for using this assembly'

    def add_permissions_to_db(self, identifier):
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO auth_permission (name, content_type_id, codename) VALUES ('manager@{0}', (SELECT id FROM django_content_type WHERE app_label LIKE 'oauth2_provider' AND model LIKE 'permission'), 'manager@{0}');".format(identifier))
            cursor.execute("INSERT INTO auth_permission (name, content_type_id, codename) VALUES ('delegate@{0}', (SELECT id FROM django_content_type WHERE app_label LIKE 'oauth2_provider' AND model LIKE 'permission'), 'delegate@{0}');".format(identifier))
            cursor.execute("INSERT INTO auth_permission (name, content_type_id, codename) VALUES ('contributor@{0}', (SELECT id FROM django_content_type WHERE app_label LIKE 'oauth2_provider' AND model LIKE 'permission'), 'contributor@{0}');".format(identifier))
            cursor.execute("INSERT INTO auth_permission (name, content_type_id, codename) VALUES ('expert@{0}', (SELECT id FROM django_content_type WHERE app_label LIKE 'oauth2_provider' AND model LIKE 'permission'), 'expert@{0}');".format(identifier))
            # row = cursor.fetchone()


    def add_arguments(self, parser):
        parser.add_argument('identifier', nargs='+', type=str)

    def handle(self, *args, **options):
        for identifier in options['identifier']:

            # TODO: better validate input Min length.
            if not identifier:
                raise CommandError('Poll "%s" does not exist or is invalid' % identifier)

            # TODO Duplication check?
            # if not identifier:
            #     raise CommandError('Poll "%s" is already registered' % identifier)

            # inser new permissions
            self.add_permissions_to_db(identifier)

            self.stdout.write(self.style.SUCCESS('Successfully registered assembly "%s"' % identifier))
