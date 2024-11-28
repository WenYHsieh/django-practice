from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import PermissionDenied
from django.middleware.csrf import CsrfViewMiddleware
from django.middleware.csrf import get_token

class CookieMixin:
    def set_token_cookie(self, response, token: str, token_type: str):
        cookie_name: str = (
            settings.SIMPLE_JWT['AUTH_COOKIE'] 
            if token_type == 'access' 
            else settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH']
        )
        
        response.set_cookie(
            cookie_name,
            token,
            max_age=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds() 
            if token_type == 'access' 
            else settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds(),
            secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
            httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
            samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
            # domain=settings.SIMPLE_JWT['AUTH_COOKIE_DOMAIN'],
            path=settings.SIMPLE_JWT['AUTH_COOKIE_PATH'],
        )
        
        response.set_cookie(
            'csrftoken',
            get_token(self.request),
            samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
            secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
        )
        
        
class CookieJWTAuthentication(JWTAuthentication):
    def enforce_csrf(self, request):
        """
        Enforce CSRF validation for cookie based authentication.
        """
        reason = CsrfViewMiddleware(get_response=lambda r: None).process_view(
            request, None, (), {}
        )
        if reason:
            raise PermissionDenied('CSRF Failed: %s' % reason)


    def authenticate(self, request):
        raw_token = request.COOKIES.get('access_token')
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        
        self.enforce_csrf(request)
        
        return self.get_user(validated_token), validated_token
