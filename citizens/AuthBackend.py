# CUSTOMIZED MODEL BACKEND
# - FOR TOKEN LOGIN (Invitation letter => instead of user + pw )
# - FOR JWTTOKEN TOKEN LOGIN
import os
import logging
import jwt as pyjwt

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import Permission
from django.db.models import Exists, OuterRef, Q
from django.http import HttpResponseForbidden
from oauth2_provider.models import get_application_model
from oauth2_provider.settings import oauth2_settings

from citizens.admin import JWTRequestForm


UserModel = get_user_model()

log = logging.getLogger("oauth2_provider")

class AuthBackend(ModelBackend):
    """
    Authenticates against settings.AUTH_USER_MODEL.
    """

    # TODO: NOT USED, RIGHT? => user original_authenticate...
    def authenticate(self, request, username=None, password=None, token=None, **kwargs):

        MODE = os.environ.get('MODE')

        if not MODE or MODE == "OAUTH":

            # THIS SEEMS TO BE A TOKEN
            if token:
                return self._token_authenticate(request=request, username=username, token=token, **kwargs)
            else:
                return self._original_authenticate(request=request, username=username, password=password, **kwargs)

        if not MODE or MODE != "OAUTH":

            # original / traditional authentication
            return self._original_authenticate(request=request, username=username, password=password, **kwargs)

    def _original_authenticate(self, request, username=None, password=None, **kwargs):

        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if username is None or password is None:
            return
        try:
            user = UserModel._default_manager.get_by_natural_key(username)
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            UserModel().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user

    def _token_authenticate(self, request, username, token, **kwargs):

        assert token
        assert username

        try:
            user = UserModel.objects.get(username=username)
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            pass
        else:
            assert user.token == token
            if self.user_can_authenticate(user):
                return user

    def user_can_authenticate(self, user):
        """
        Reject users with is_active=False. Custom user models that don't have
        that attribute are allowed.
        """
        is_active = getattr(user, 'is_active', None)
        return is_active or is_active is None

    def _get_user_permissions(self, user_obj):
        return user_obj.user_permissions.all()

    def _get_group_permissions(self, user_obj):
        user_groups_field = get_user_model()._meta.get_field('groups')
        user_groups_query = 'group__%s' % user_groups_field.related_query_name()
        return Permission.objects.filter(**{user_groups_query: user_obj})

    def _get_permissions(self, user_obj, obj, from_name):
        """
        Return the permissions of `user_obj` from `from_name`. `from_name` can
        be either "group" or "user" to return permissions from
        `_get_group_permissions` or `_get_user_permissions` respectively.
        """
        if not user_obj.is_active or user_obj.is_anonymous or obj is not None:
            return set()

        perm_cache_name = '_%s_perm_cache' % from_name
        if not hasattr(user_obj, perm_cache_name):
            if user_obj.is_superuser:
                perms = Permission.objects.all()
            else:
                perms = getattr(self, '_get_%s_permissions' % from_name)(user_obj)
            perms = perms.values_list('content_type__app_label', 'codename').order_by()
            setattr(user_obj, perm_cache_name, {"%s.%s" % (ct, name) for ct, name in perms})
        return getattr(user_obj, perm_cache_name)

    def get_user_permissions(self, user_obj, obj=None):
        """
        Return a set of permission strings the user `user_obj` has from their
        `user_permissions`.
        """
        return self._get_permissions(user_obj, obj, 'user')

    def get_group_permissions(self, user_obj, obj=None):
        """
        Return a set of permission strings the user `user_obj` has from the
        groups they belong.
        """
        return self._get_permissions(user_obj, obj, 'group')

    def get_all_permissions(self, user_obj, obj=None):
        if not user_obj.is_active or user_obj.is_anonymous or obj is not None:
            return set()
        if not hasattr(user_obj, '_perm_cache'):
            user_obj._perm_cache = super().get_all_permissions(user_obj)
        return user_obj._perm_cache

    def has_perm(self, user_obj, perm, obj=None):
        return user_obj.is_active and super().has_perm(user_obj, perm, obj=obj)

    def has_module_perms(self, user_obj, app_label):
        """
        Return True if user_obj has any permissions in the given app_label.
        """
        return user_obj.is_active and any(
            perm[:perm.index('.')] == app_label
            for perm in self.get_all_permissions(user_obj)
        )

    def with_perm(self, perm, is_active=True, include_superusers=True, obj=None):
        """
        Return users that have permission "perm". By default, filter out
        inactive users and include superusers.
        """
        if isinstance(perm, str):
            try:
                app_label, codename = perm.split('.')
            except ValueError:
                raise ValueError(
                    'Permission name should be in the form '
                    'app_label.permission_codename.'
                )
        elif not isinstance(perm, Permission):
            raise TypeError(
                'The `perm` argument must be a string or a permission instance.'
            )

        UserModel = get_user_model()
        if obj is not None:
            return UserModel._default_manager.none()

        permission_q = Q(group__user=OuterRef('pk')) | Q(user=OuterRef('pk'))
        if isinstance(perm, Permission):
            permission_q &= Q(pk=perm.pk)
        else:
            permission_q &= Q(codename=codename, content_type__app_label=app_label)

        user_q = Exists(Permission.objects.filter(permission_q))
        if include_superusers:
            user_q |= Q(is_superuser=True)
        if is_active is not None:
            user_q &= Q(is_active=is_active)

        return UserModel._default_manager.filter(user_q)

    def get_user(self, user_id):
        try:
            user = UserModel._default_manager.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
        return user if self.user_can_authenticate(user) else None


class AllowAllUsersModelBackend(ModelBackend):
    def user_can_authenticate(self, user):
        return True


class JWTProtectedResourceMixin(forms.Form):

    """Mixin for protecting resources with client authentication as mentioned in rfc:`3.2.1`
    This involves authenticating with any of: HTTP Basic Auth, Client Credentials and
    Access token in that order. Breaks off after first validation.
    """

    server_class = oauth2_settings.OAUTH2_SERVER_CLASS
    validator_class = oauth2_settings.OAUTH2_VALIDATOR_CLASS
    oauthlib_backend_class = oauth2_settings.OAUTH2_BACKEND_CLASS

    def authenticate_jwt_client(self, request):

        # Validate Post data
        # request.POST = json.loads(request.body)
        form = JWTRequestForm(request.user, request.POST)

        if not form.is_valid():
            return False
        request.client_id = form.cleaned_data['client_id']

        # Validate Token data
        jwttoken = request.headers.get('Authorization')
        if not jwttoken:
            return False
        unverifiedtoken = pyjwt.decode(jwttoken[4:], verify=False)
        if not unverifiedtoken:
            return False
        # Load Application (by client_id)
        Application = get_application_model()
        try:
            request.client = Application.objects.get(client_id=request.client_id)
            # Check that the application can be used (defaults to always True)
            if not request.client.is_usable(request):
                log.debug("Failed body authentication: Application %r is disabled" % (request.client_id))
                return False
        except Application.DoesNotExist:
            log.debug("Failed body authentication: Application %r error" % (request.client_id))
            return False

        verifiedtoken = pyjwt.decode(
            jwttoken[4:],
            request.client.client_secret,
            algorithms=['HS512'],
            aud='demokratiefabrik/fabrikAuth',
            )

        if verifiedtoken:
            request.verifiedtoken = verifiedtoken
            return True

        return False

    def dispatch(self, request, *args, **kwargs):
        # let preflight OPTIONS requests pass
        if request.method.upper() == "OPTIONS":
            return super().dispatch(request, *args, **kwargs)

        try:
            valid = self.authenticate_jwt_client(request)
        except pyjwt.ExpiredSignatureError:
            return False
            
        if valid:

            try:
                user_id = request.verifiedtoken.get('sub')
                user = UserModel.objects.get(pk=user_id)
            except UserModel.DoesNotExist:
                return HttpResponseForbidden()
                
            request.user = user
            return True
        else:
            return False
