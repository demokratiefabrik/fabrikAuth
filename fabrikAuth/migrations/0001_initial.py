from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db import migrations


def add_oauth_apps(apps, schema_editor):

    MODEL = ['oauth2_provider', 'application']
    App = apps.get_model(*MODEL)
    App.objects.create(
        redirect_uris='http://localhost:8080/authorization',
        client_type='public',
        authorization_grant_type='authorization-code',
        name='demokratiefabrik/fabrikApi',
        skip_authorization=True
    )


def add_permissions(apps, schema_editor):

    ContentType = apps.get_model("contenttypes", "ContentType")
    types = ContentType.objects.filter(app_label='oauth2_provider', model='permission')
    content_type_id = types[0].id

    Permission = apps.get_model("auth", "Permission")
    Permission.objects.create(
        name='administrator@GLOBAL',
        codename='administrator@GLOBAL',
        content_type_id=content_type_id
    )

# def add_users(apps, schema_editor):

#     User = apps.get_model(*settings.AUTH_USER_MODEL.split('.'))

#     # Django Root
#     User.objects.create(
#         email='root@demokratie-fabrik.ch',
#         username='root',
#         is_superuser=True,
#         is_staff=True,
#         password=make_password('...')
#     )

#     User.objects.create(
#         email='administrator@demokratie-fabrik.ch',
#         username='administrator',
#         is_staff=True,
#         password=make_password('...')
#     )


class Migration(migrations.Migration):

    dependencies = [
         ('auth', '__first__'),
         ('oauth2_provider', '__first__'),
    ]

    operations = [
        migrations.RunSQL(
            """-- add Django permission: oauth2_provider--
            # INSERT INTO django_content_type (app_label, model, name) 
            # VALUES ('oauth2_provider', 'permission', 'oauth2_provider_permission');
            INSERT INTO django_content_type (app_label, model) 
            VALUES ('oauth2_provider', 'permission');
            -- allow JWT tokens: (remove token and enlarge token fields)--
            ALTER TABLE `fabrikAuth`.`oauth2_provider_accesstoken` DROP INDEX `token`;
            ALTER TABLE oauth2_provider_accesstoken CHANGE COLUMN `token` `token` VARCHAR(2000) NOT NULL;
            """
        ),

        migrations.RunPython(add_oauth_apps),
        # migrations.RunPython(add_users),
        migrations.RunPython(add_permissions),
    ]
