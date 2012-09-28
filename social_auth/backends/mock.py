"""
Mock backends.
"""
from social_auth.backends import OAuthBackend, BaseOAuth2, USERNAME
from social_auth.utils import log
from django.contrib.auth import authenticate
from django.conf import settings

import urllib
import urlparse
import time

class MockOAuth2Backend(OAuthBackend):
    name = 'mock-oauth2'

    def get_user_id(self, details, response):
        return details['email']

    def get_user_details(self, response):
        email = response.get('email', '')
        return {
            USERNAME: email.split('@', 1)[0],
            'email': email,
            'fullname': response.get('fullname', ''),
            'first_name': response.get('first_name', ''),
            'last_name': response.get('last_name', '')
        }

class MockOAuth2(BaseOAuth2):
    """Mock OAuth 2"""
    AUTH_BACKEND = MockOAuth2Backend
    SETTINGS_KEY_NAME = 'MOCK_OAUTH2_CLIENT_KEY'
    SETTINGS_SECRET_NAME = 'MOCK_OAUTH2_CLIENT_SECRET'
    REDIRECT_STATE = False
    AUTHORIZATION_URL = '/oauth/callback/mock-oauth2/'

    def auth_url(self):
        """
        Allow us to mock out the user inside the auth url.

        All values desired for user are passed URL-encoded.
        """
        root_auth_url = super(MockOAuth2, self).auth_url()
        path, query_str = urllib.splitquery(root_auth_url)
        query = dict(urlparse.parse_qsl(query_str))
        for k, v in self.request.REQUEST.iteritems():
            query['mock_%s' % k] = v

        return "%s?%s" % (path, urllib.urlencode(query))

    def auth_complete(self, *args, **kwargs):
        """
        Fake out the login completion.  This would be one request.
        """
        time.sleep(1) # HTTP request to provider

        self.validate_state()

        response = {}
        response.update(self.user_data("access_token", response))
        kwargs.update({
            'auth': self,
            'response': response,
            self.AUTH_BACKEND.name: True
        })

        return authenticate(*args, **kwargs)

    def user_data(self, access_token, *args, **kwargs):
        """
        Fake out gathering user data.  This would be another request.
        """
        time.sleep(1) # HTTP request to provider

        user_data = {}
        for k, v in self.request.REQUEST.iteritems():
            if k.startswith('mock_'):
                user_data[k[5:]] = v
        return user_data

    @classmethod
    def enabled(self):
        """
        Only enabled in debug mode
        """
        if settings.DEBUG:
            return True
        return False


BACKENDS = {
    'mock-oauth2': MockOAuth2
}
