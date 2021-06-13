# e.g https://stackoverflow.com/questions/50896287/django-custom-login-form-show-extra-field
from django.core.exceptions import ValidationError
from citizens.lib.chacha20 import decryptToken, validtoken

from django.conf import settings
from django import forms
from django.contrib import admin
from django.contrib.admin.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _

from .models import User


# class CustomAuthenticationForm(AuthenticationForm):
#     class Meta(AuthenticationForm.Meta):
#         model = User
#         fields = AuthenticationForm.Meta.fields + ('token',)
class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('import_bulk', 'extra')


class CustomUserChangeForm(UserChangeForm):

    class Meta(UserChangeForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'import_bulk', 'extra',
                'email', 'is_staff', 'is_superuser', 'is_active', 'date_joined', 'last_login')

        # fields = UserChangeForm.Meta.fields + ('token',)


class JWTRequestForm(forms.Form):
    """
    A form to transmit the client_<application>_id. This allows to .
    """

    client_id = forms.CharField(
        widget=forms.TextInput,
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(JWTRequestForm, self).__init__(*args, **kwargs)

    def clean_client_id(self):
        return self.cleaned_data.get('client_id')


class JWTEmailUpdateForm(forms.Form):
    """
    A form that lets a user change set their email while checking for a change in the
    e-mail.
    """

    email = forms.EmailField(
        widget=forms.EmailInput,
    )

    client_id = forms.CharField(
        widget=forms.TextInput,
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(JWTEmailUpdateForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        return self.cleaned_data.get('email')

    def save(self, commit=True):
        email = self.cleaned_data["email"]
        self.user.email = email
        if commit:
            self.user.save()
        return self.user


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(required=True)
    token = forms.CharField(required=False)   # token for longtime usage (no additonal sensitive data in the backend)
    ltoken = forms.CharField(required=False)  # token for shortime usage (additonal senistive data in the backend)
    password = forms.CharField(widget=forms.PasswordInput)

    def preValidateTemporaryLimitedToken(self, token):
        # ChaCha20 Decode
        assert token
        if not validtoken(token, settings):
            return False

        chacha = token.split(':')
        username = chacha[0]
        return username and chacha

    def encryptTemporaryLimitedToken(self, ltoken):
        assert ltoken
        assert validtoken(ltoken, settings)
        chacha = ltoken.split(':')
        username = chacha[0]
        assert username, chacha

        # get encryptedtoken
        encryptedtoken = decryptToken(ltoken, '0000', settings, inputAsUTF8=True)
        assert decryptToken(encryptedtoken, '0000', settings, returnAsUTF8=True) == ltoken 
        return username, encryptedtoken

    def extractCredentialsFromToken(self, token):
        # ChaCha20 Decode
        assert token
        chacha = token.split(':')
        assert chacha and len(chacha) == 2
        access = decryptToken(chacha[0], chacha[1], settings, returnAsUTF8=True)
        pos = access.find('_')
        assert pos > -1
        username = access[0:pos]
        password = access[(pos+1):len(access)]
        assert username and password
        assert len(username) < 45
        assert token
        return username, password

    class Meta:
        model = User
        fields = ('email', 'password')

    # def clean_token(self):
    #     data = self.cleaned_data['token']
    #     return data.lower()

    def get_invalid_token_error(self):
        return ValidationError(
            self.error_messages['invalid_token'],
            code='invalid_token',
            params={})

    error_messages = {
        'invalid_token':
            "Der Token ist nicht mehr gültig. Bitte melden Sie sich mit den Zugangsdaten an, die wir Ihnen im Einladungsbrief zugesendet haben.",
        'invalid_login': _(
            "Please enter a correct %(username)s and password. Note that both "
            "fields may be case-sensitive."
        ),
        'inactive': _("This account is inactive."),
    }

    def __init__(self, request=None, *args, **kwargs):
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

        # Set the max length and label for the "username" field.
        self.username_field = User._meta.get_field(User.USERNAME_FIELD)
        username_max_length = self.username_field.max_length or 254
        self.fields['username'].max_length = username_max_length
        self.fields['username'].widget.attrs['maxlength'] = username_max_length
        if self.fields['username'].label is None:
            self.fields['username'].label = capfirst(self.username_field.verbose_name)

        # ASSERT CORRECT TOKEN LINK DATA...
        import urllib.parse as urlparse
        redirect_url = request.GET.get('next')
        query = urlparse.parse_qs(redirect_url) if redirect_url else None
        if query and query.get('token'):
            token = query.get('token')[0]
            try:
                username, password = self.extractCredentialsFromToken(token)
                assert username and password
                self.fields['token'].initial = token
            except Exception:
                pass
        if query and query.get('ltoken'):
            ltoken = query.get('ltoken')[0]
            ltoken = ltoken.strip()
            self.fields['ltoken'].initial = ltoken

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        token = self.cleaned_data.get('token')
        ltoken = self.cleaned_data.get('ltoken')

        # ENABLE TOKEN LOGIN: without saving any more sensitive data on the server....
        # QR-LOGIN!!!
        if token:
            username, password = self.extractCredentialsFromToken(token)
            self.cleaned_data['username'] = username
            # self.cleaned_data['password'] = 'NOTEMPTY'
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        # TEMPORARY TOKEN:
        # FORGOTTEN_PASSWORD (token with one or two day limit)
        elif ltoken:
            
            ltoken = ltoken.strip()
            if not self.preValidateTemporaryLimitedToken(ltoken):
                raise self.get_invalid_token_error()                    
            username, token = self.encryptTemporaryLimitedToken(ltoken)
            self.cleaned_data['username'] = username
            self.cleaned_data['password'] = 'NOTEMPTY'
            self.user_cache = authenticate(self.request, username=username, token=token)
            if self.user_cache is None:
                raise self.get_invalid_token_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        elif username and password:
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

class UserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    list_display = ['username', 'email', 'is_staff']
    # prepopulated_fields = {'username': ('first_name' , 'last_name', 'token')}

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'username', 'password1', 'password2'),
        }),
    )

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'import_bulk', 'extra')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

# Register UserAdmin
admin.site.register(User, UserAdmin)
