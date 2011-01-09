import cgi
import logging
import urllib

from google.appengine.api import urlfetch

from django.utils import simplejson
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend
from django.conf import settings

import facebook


class FacebookBackend(ModelBackend):
    def authenticate(self, request):
        verification_code = request.GET.get("code")
        if not verification_code:
            return None

        # Strip the CODE out of the redirect URI
        redirect_uri = request.build_absolute_uri()
        redirect_uri_split = redirect_uri.split('code=')
        redirect_uri = redirect_uri_split[0]
        redirect_uri = redirect_uri.rstrip('&?')

        args = dict(client_id=settings.FACEBOOK_APP_ID, redirect_uri=redirect_uri)
        args["client_secret"] = settings.FACEBOOK_APP_SECRET
        args["code"] = verification_code
        response = urlfetch.fetch(
                "https://graph.facebook.com/oauth/access_token?" +
                urllib.urlencode(args), deadline=10)
        if response.status_code != 200:
            return None
        response = cgi.parse_qs(response.content)
        access_token = response["access_token"][-1]

        # Download the user profile and cache a local instance of the
        # basic profile info
        response = urlfetch.fetch(
            "https://graph.facebook.com/me?" +
            urllib.urlencode(dict(access_token=access_token)), deadline=10)
        profile = simplejson.loads(response.content)
        user = User(id=str(profile["id"]),
                    username=str(profile["id"]),
                    email=profile.get("email", ''),
                    first_name=profile["first_name"],
                    last_name=profile["last_name"],
                    password=access_token
                    )
        user.save() # update the user profile with the new token
        return user