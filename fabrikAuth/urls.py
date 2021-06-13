"""fabrikAuth URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# import json
import os

from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from citizens import views as citizens_views
from citizens.admin import UserLoginForm

# @login_required()
# def userdata(request):
#     user = request.user
#     return HttpResponse(
#         json.dumps({
#             'username': user.username
#         }),
#         content_type='application/json'
#     )


urlpatterns = []


# Note: MODE must not be set, for setupping cachefiles within Dockerfile...
MODE = os.environ.get('MODE')

if not MODE or MODE == "OAUTH":
    # only expose what is necessary for the public!!!
    urlpatterns += [
        path("o/", include('oauth2_provider.urls', namespace='oauth2_provider')),

        # path(r"accounts/emailupdate", citizens_views.AccountsEmailUpdate.as_view(), name="emailupdate"),
        path(r"accounts/emailupdate", csrf_exempt(citizens_views.profileUpdateView), name="emailupdate"),
        path(
            'accounts/login',
            citizens_views.LoginView.as_view(
                template_name="citizens/login.html",
                authentication_form=UserLoginForm
                ),
            name='login')
    ]

if not MODE or MODE != "OAUTH":
    # Do not load oauth functionality here...
    urlpatterns += [
        path('admin/', admin.site.urls),
        # path("o/", include('oauth2_provider.urls', namespace='oauth2_provider')),
        # path('userdata', userdata, name='userdata'),
        path('accounts/', include('django.contrib.auth.urls')),
        path('mailing', include('massmailer.urls')),  # massmailer
    ]
