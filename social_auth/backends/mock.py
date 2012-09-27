"""
Mock backends.
"""
from social_auth.backends import OAuthBackend, BaseOAuth2, USERNAME
from django.contrib.auth import authenticate

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

    def auth_complete(self, *args, **kwargs):
        """
        Fake out the login completion.  This would be one request.
        """
        response = {}
        response.update(self.user_data(None, response))
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
        return {
             "id": "00000000000000",
             "email": "fred.example@gmail.com",
             "fullname": "Fred Example",
             "first_name": "Fred",
             "last_name": "Example",
             "picture": "https://lh5.googleusercontent.com/-2Sv-4bBMLLA/AAAAAAAAAAI/AAAAAAAAABo/bEG4kI2mG0I/photo.jpg",
             "gender": "male",
             "locale": "en-US"
        }

BACKENDS = {
    'mock-oauth2': MockOAuth2
}
