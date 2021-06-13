from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import connection

UserModel = get_user_model()

class Command(BaseCommand):
    help = 'Setups permissions for using this assembly'

    def add_permissions_to_db(self, identifier):
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO auth_permission (name, content_type_id, codename) VALUES ('manager@{0}', (SELECT id FROM django_content_type WHERE app_label LIKE 'oauth2_provider' AND model LIKE 'permission'), 'manager@{0}');".format(identifier))
            cursor.execute("INSERT INTO auth_permission (name, content_type_id, codename) VALUES ('delegate@{0}', (SELECT id FROM django_content_type WHERE app_label LIKE 'oauth2_provider' AND model LIKE 'permission'), 'delegate@{0}');".format(identifier))
            cursor.execute("INSERT INTO auth_permission (name, content_type_id, codename) VALUES ('contributor@{0}', (SELECT id FROM django_content_type WHERE app_label LIKE 'oauth2_provider' AND model LIKE 'permission'), 'contributor@{0}');".format(identifier))
            cursor.execute("INSERT INTO auth_permission (name, content_type_id, codename) VALUES ('expert@{0}', (SELECT id FROM django_content_type WHERE app_label LIKE 'oauth2_provider' AND model LIKE 'permission'), 'expert@{0}');".format(identifier))
            # row = cursor.fetchone()

    def add_users_to_db(self, identifier):
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO auth_permission (name, content_type_id, codename) VALUES ('manager@{0}', (SELECT id FROM django_content_type WHERE app_label LIKE 'oauth2_provider' AND model LIKE 'permission'), 'manager@{0}');".format(identifier))
            cursor.execute("INSERT INTO auth_permission (name, content_type_id, codename) VALUES ('delegate@{0}', (SELECT id FROM django_content_type WHERE app_label LIKE 'oauth2_provider' AND model LIKE 'permission'), 'delegate@{0}');".format(identifier))
            cursor.execute("INSERT INTO auth_permission (name, content_type_id, codename) VALUES ('contributor@{0}', (SELECT id FROM django_content_type WHERE app_label LIKE 'oauth2_provider' AND model LIKE 'permission'), 'contributor@{0}');".format(identifier))
            cursor.execute("INSERT INTO auth_permission (name, content_type_id, codename) VALUES ('expert@{0}', (SELECT id FROM django_content_type WHERE app_label LIKE 'oauth2_provider' AND model LIKE 'permission'), 'expert@{0}');".format(identifier))
            # row = cursor.fetchone()

    def add_users(self):

        User = UserModel._default_manager

        # CLIENT USERS
        User.create(
            email='observer@demokratie-fabrik.ch',
            username='observer',
            token='observer',
            password=make_password('demokratiefabrik')
        )

        User.create(
            email='manager@demokratie-fabrik.ch',
            username='manager',
            token='manager',
            is_staff=True,
            password=make_password('demokratiefabrik')
        )

        User.create(
            email='expert@demokratie-fabrik.ch',
            username='expert',
            token='expert',
            password=make_password('demokratiefabrik')
        )

        User.create(
            email='contributor@demokratie-fabrik.ch',
            token='contributor',
            username='contributor',
            password=make_password('demokratiefabrik')
        )

        User.create(
            email='delegate@demokratie-fabrik.ch',
            username='delegate',
            token='delegate',
            password=make_password('demokratiefabrik')
        )


    def link_a_permission_to_a_user(self, identifier, username, permission_name):
        with connection.cursor() as cursor:
            permission_label = '%s@%s' % (permission_name, identifier)
            sql = """
                INSERT INTO auth_user_user_permissions (user_id, permission_id) 
                VALUES (
                        (SELECT id FROM auth_user WHERE username LIKE '%s' LIMIT 1),
                        (SELECT id FROM auth_permission WHERE name LIKE '%s' LIMIT 1)
                );""" % (username, permission_label)
            print(sql)
            cursor.execute(sql)

    def handle(self, *args, **options):

        # inser new permissions
        self.add_users()

        self.add_permissions_to_db('digikon2022')
        self.link_a_permission_to_a_user('digikon2022', 'delegate', 'delegate')
        self.link_a_permission_to_a_user('digikon2022', 'contributor', 'contributor')
        self.link_a_permission_to_a_user('digikon2022', 'manager', 'manager')
        self.link_a_permission_to_a_user('digikon2022', 'expert', 'expert')

        self.add_permissions_to_db('initiativeXY')
        self.link_a_permission_to_a_user('initiativeXY', 'delegate', 'delegate')
        self.link_a_permission_to_a_user('initiativeXY', 'contributor', 'contributor')
        self.link_a_permission_to_a_user('initiativeXY', 'manager', 'manager')
        self.link_a_permission_to_a_user('initiativeXY', 'expert', 'expert')

        self.stdout.write(self.style.SUCCESS('Successfully inserted example data'))
