"""
Mock backends.
"""
from social_auth.backends import OAuthBackend, BaseOAuth2, USERNAME
from django.contrib.auth import authenticate
from urllib import urlencode

import time

class MockOAuth2Backend(OAuthBackend):
    name = 'mock-oauth2'

    def get_user_id(self, details, response):
        return details['email']

    def get_user_details(self, response):
        email = response.get('email', '')
        return {USERNAME: email.split('@', 1)[0],
                'email': email,
                'fullname': response.get('fullname', ''),
                'first_name': response.get('first_name', ''),
                'last_name': response.get('last_name', '')},

class MockOAuth2(BaseOAuth2):
    """Mock OAuth 2"""
    AUTH_BACKEND = MockOAuth2Backend
    SETTINGS_KEY_NAME = 'MOCK_OAUTH2_CLIENT_KEY'
    SETTINGS_SECRET_NAME = 'MOCK_OAUTH2_CLIENT_SECRET'
    REDIRECT_STATE = False
    #AUTHORIZATION_URL = '/oauth/callback/mock-oauth2/'

    def auth_url(self):
        """
        Fake redirect URL -- goes straight to confirmation.
        """
        state = self.state_token()

        # Store state in session for further request validation. The state
        # value is passed as state parameter (as specified in OAuth2 spec), but
        # also added to redirect_uri, that way we can still verify the request
        # if the provider doesn't implement the state parameter.
        self.request.session[self.AUTH_BACKEND.name + '_state'] = state

        args = {
            'state': state,
            'code': 'foobar',
            'redirect_uri': self.get_redirect_uri(state),
            'response_type': 'code'
        }
        return '/oauth/callback/mock-oauth2/?' + urlencode(args)

    def auth_complete(self, *args, **kwargs):
        """
        Fake out the login completion.  This would be one request.
        """
        time.sleep(1)

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

        TODO: method for populating this data
        """
        time.sleep(1)
        return {
            "access_token": access_token,
            "expires_in": 3600,
            "expires": 3600,
            "id": "00000000000000",
            "email": "fred.example@gmail.com",
            "fullname": "Fred Example",
            "first_name": "Fred",
            "last_name": "Example",
            "picture": "https://lh5.googleusercontent.com/-2Sv-4bBMLLA/AAAAAAAAAAI/AAAAAAAAABo/bEG4kI2mG0I/photo.jpg",
            "gender": "male",
            "locale": "en-US"
        }

    @classmethod
    def enabled(self):
        """
        TODO: only enable this in debug mode?
        """
        return True


BACKENDS = {
    'mock-oauth2': MockOAuth2
}
