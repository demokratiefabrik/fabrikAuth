# Django setup

django-oauth-toolkit (oAuth2-Provider)\
https://django-oauth-toolkit.readthedocs.io/en/latest/install.html

ADD CUSTOM USER MODEL\
https://www.caktusgroup.com/blog/2019/04/26/how-switch-custom-django-user-model-mid-project/

# Two Modes of Running

The Django App can run in two modes:

- Env 'Mode' => 'OAUTH': Here only oauth server entrypoints are enabled.
- Env 'Mode' => 'DJANGO': Here full Djanog server is exposed.

## FAQ

**Why demokratiefabrik comes with an own oAuth Server?**

1. full control over data demands for an in-house authentication.
2. need for flexible connection to other civic-tech apps demands for an oAuth technics.
3. Privacy: full split between user data and operation data

# SETUP App (PRODUCTION)

## check setup

> python manage.py check --deploy --settings=fabrikAuth.production_settings

## Docker Builds

> cd /var/demokratiefabrik/fabrikAuth
> docker build -f Dockerfile -t demokratiefabrik/fabrikauth .
> docker run --publish 8010:8010 --detach --restart unless-stopped --name fabrikAuth demokratiefabrik/fabrikauth:latest

# SETUP App (DEVELOPPING)

Set ENV Variable:

> export MODE=DJANGO

Add permission for default democracyfabrik user to fabrikAuth table

Then:

> python manage.py migrate citizens
> python manage.py migrate fabrikAuth
> python manage.py migrate

<!-- # SQL  -->
<!-- INSERT INTO django_migrations (app, name, applied) VALUES ('citizens', '0001_initial', CURRENT_TIMESTAMP);
UPDATE django_content_type SET app_label = 'citizens' WHERE app_label = 'auth' and model = 'user'; -->

### admin custom login form

URL: http://localhost:8010/admin/
=> using user/pw: root/demokratiefabrik

Finally: update client_id and secret_id in fabrikAPi and fabrikClient

# Docker secrets

# Error Reporting

https://docs.djangoproject.com/en/3.1/howto/error-reporting/

# Setup also Example Data

> python manage.py example_data\

TODO : really used?

> python manage.py prepare_assembly digikon2022

# CONCEPTION

EXAMPLE ASSEMBLY IDENTIFER:

- initiativXY
- digikon20222

PERMISSIONS:

- manager@<identifier>
- delegate@<identifier>
- expert@<identifier>
- contributor@<identifier>

## PERMISSIONS & GROUPS REQUIRED FOR fabrikApi

- Global Permissions

  - administrator can setup / manage assemblies and all other content

- Assembly-based permissions: (DEFAULT VALUES)
  - manager (can fully manage its assemblies.)
  - delegate can add entries/suggestions and can evaluate others contribution
  - contributor has permissions to read and contribute.
  - public can view the result of the assembly when its in the PUBLIC PHASE

## Translation

Add a new language (and extract all messages to translate)

> django-admin makemessages -l de-ch

Compile the message catalog:

> django-admin compilemessages

# TODO:

- Django 3.1 requires UTF-8 Code files

# DEV MODE

export MODE=OAUTH

# Massmailer

- add urls.php and installed packages in settings.php.
- python3 manage.py migrate
