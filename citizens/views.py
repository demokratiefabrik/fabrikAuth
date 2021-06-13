import logging
import json
from django.http.response import Http404, HttpResponseForbidden
from jsonview.decorators import json_view
# from jsonview.decorators import json_view
from jsonview.views import JsonView
from django.http import HttpResponse

from django.contrib.auth import views as django_views
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from citizens.admin import JWTEmailUpdateForm
from citizens.AuthBackend import JWTProtectedResourceMixin

log = logging.getLogger("oauth2_provider")


class LoginView (django_views.LoginView):
    """ Login View """
    # Not used, since citizens use oAuth Login View...
    pass


@json_view
def profileUpdateView(request):
    # STORE EMAILADRESS
    # assert request.user
    # assert request.client.client_secret
    try:
        request.POST = json.loads(request.body)
    except json.decoder.JSONDecodeError:
        raise Http404

    form = JWTEmailUpdateForm(request.user, request.POST)
    jwtauth = JWTProtectedResourceMixin(form)
    authenticated = jwtauth.dispatch(request)
    if not authenticated:
        return HttpResponseForbidden()

    # print(request.user)
    # Submit userprofile
    #  or form.data.get('lastname')
    form = JWTEmailUpdateForm(request.user, request.POST)
    if form.data.get('email'):
        if form.is_valid() and form.cleaned_data.get('email'):
            form.save()
            return HttpResponse(
                content=json.dumps({'ok': True}),
                status=200,
                content_type="application/json"
            )
        else:
            return HttpResponse(
                status=404,
                content_type="application/json"
            )


    # Just read current profile data
    return HttpResponse(
        content=json.dumps({
            'email': request.user.email
            # 'last_name': request.user.last_name,
            # 'extra': request.user.extra,
            # 'first_name': request.user.first_name
        }),
        status=200,
        content_type="application/json"
    )
