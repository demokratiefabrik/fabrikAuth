import arrow
import jwt as pyjwt

from oauthlib import common
from django.utils import timezone
from django.conf import settings


def generate_access_token(request):

    # SET
    expiry = settings.OAUTH2_PROVIDER.get('ACCESS_TOKEN_EXPIRE_SECONDS', 300)

    # filter only fabrikApi permissionss
    permissions = list(
        filter(
            lambda x:
            x.startswith('oauth2_provider.') and x.find('@') > -1,
            request.user.get_all_permissions())
    )

    # remove overhead
    permissions = list(
        map(lambda x: x[len('oauth2_provider.'):], permissions)
    )
    token = pyjwt.encode({
        "sub": request.user.id,
        "iss": 'demokratiefabrik/fabrikAuth',
        "userEmail": not (not request.user.email),
        "roles": permissions,
        "exp": arrow.utcnow().timestamp + expiry  # five minutes lifetime
    }, request.client.client_secret, algorithm='HS512').decode()

    # update last_login date
    request.user.last_login = timezone.now()
    request.user.save(update_fields=['last_login'])

    return(token)


def generate_refresh_token(request):
    return common.generate_token()
