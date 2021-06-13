from django.conf import settings
from citizens.lib.chacha20 import decryptToken, set_new_token, validtoken
from django.db import models

# Create your models here.
# https://docs.djangoproject.com/en/3.0/topics/auth/customizing/#authentication-backends
from django.contrib.auth.models import AbstractUser

# TODO https://schinckel.net/2019/09/18/postgres-enum-types-in-django/
# => for massmailer permissions query => register_enum


class User(AbstractUser):
    class Meta:
        db_table = 'auth_user'

    token = models.CharField(
        # db_column='token',
        max_length=300,
        unique=True,
        null=True,
        blank=True)

    import_bulk = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True)

    extra = models.CharField(
        max_length=300,
        null=True,
        blank=True)

    @property
    def deccryptedtoken(self):

        try:
            token = decryptToken(self.token, '0000', settings, returnAsUTF8=True)
        except Exception:
            token = None
        
        # is the token still valid? (If not, then, create a new one...)
        # create new token:
        if not validtoken(token, settings):
            token = set_new_token(self.username)
            assert validtoken(token, settings)
        
            self.token = decryptToken(token, '0000', settings, inputAsUTF8=True)
            assert decryptToken(self.token, '0000', settings, returnAsUTF8=True) == token
            self.save()
            
        assert token
        return token

    @property
    def tokenurl(self):

        return settings.TOKEN_LOGIN_URL % self.deccryptedtoken

    USERNAME_FIELD = 'username'
    # REQUIRED_FIELDS = ['email']
