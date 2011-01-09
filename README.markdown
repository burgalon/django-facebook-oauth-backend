h1. Facebook authroziation bacend for Facebook

h3. Based on the original SDK published https://github.com/facebook/python-sdk

h3. Installation
# In settings.py add 'facebook' to your INSTALLED_APPS
# In settings.py add:
	AUTHENTICATION_BACKENDS = ('facebook.auth.backends.FacebookBackend',)
# In settings.py add (from www.facebook.com/developers/):
	FACEBOOK_APP_ID = ''
	FACEBOOK_APP_SECRET = ''
# In your urls.py add:
    url(r'^accounts/', include('facebook.auth.urls'))
# You might want to take a look at facebook/auth/views.py and change the 'scope' parameter according to the permissions your application needs (http://developers.facebook.com/docs/authentication/permissions)