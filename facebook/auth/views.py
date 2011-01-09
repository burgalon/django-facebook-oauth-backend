import base64
import cgi
import hashlib
import hmac
import time
import logging
import urllib

from django.contrib.auth.models import User
from django.utils import simplejson
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import login as django_login, \
    authenticate as django_authenticate, logout as django_logout

from google.appengine.api import users

def parse_cookie(value):
    """Parses and verifies a cookie value from set_cookie"""
    if not value: return None
    parts = value.split("|")
    if len(parts) != 3: return None
    if cookie_signature(parts[0], parts[1]) != parts[2]:
        logging.warning("Invalid cookie signature %r", value)
        return None
    timestamp = int(parts[1])
    if timestamp < time.time() - 30 * 86400:
        logging.warning("Expired cookie %r", value)
        return None
    try:
        return base64.b64decode(parts[0]).strip()
    except:
        return None


def cookie_signature(*parts):
    """Generates a cookie signature.

    We use the Facebook app secret since it is different for every app (so
    people using this example don't accidentally all use the same secret).
    """
    hash = hmac.new(settings.FACEBOOK_APP_SECRET, digestmod=hashlib.sha1)
    for part in parts: hash.update(part)
    return hash.hexdigest()

def set_cookie(response, name, value, domain=None, path="/", max_age=None):
    """Generates and signs a cookie for the give name/value"""
    timestamp = str(int(time.time()))
    value = base64.b64encode(value)
    signature = cookie_signature(value, timestamp)
    response.set_cookie(name,
                        "|".join([value, timestamp, signature]),
                        max_age=max_age,
                        path='/',
                        domain=domain)

# redirects to the google user api generated login url
def login(request):
    verification_code = request.GET.get("code")
    if verification_code:
        return authenticate(request)
    args = dict(client_id=settings.FACEBOOK_APP_ID, redirect_uri=request.build_absolute_uri())
    scope = "publish_stream,friends_relationships,offline_access, friends_of_friends"
    return HttpResponseRedirect('https://graph.facebook.com/oauth/authorize?scope=%s&%s' %
                                (scope, urllib.urlencode(args)))


# redirects to the google user api generated login url
def logout(request):
    django_logout(request)
    return HttpResponseRedirect(users.create_logout_url("/"))



def authenticate(request):
    user = django_authenticate(request=request)
    if user is not None:
        django_login(request, user)
        #redirect to valid login page
        response = HttpResponseRedirect(request.GET.get('next', '/'))
        set_cookie(response, "fb_user", user.id,
                   max_age=30 * 86400)
        return response
    else:
        # return invalid login page
        return HttpResponse('Invalid', 'text/plain')