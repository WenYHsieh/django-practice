from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserRegistrationSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from utils.cookie import CookieMixin
from django.conf import settings

class UserRegistrationView(CookieMixin, APIView):
    @swagger_auto_schema(
        operation_summary="新增帳號（註冊）",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description="Email"),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description="密碼"),
            },
        ),
        responses={
            status.HTTP_201_CREATED: openapi.Response(
                description="User successfully registered",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'email': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            status.HTTP_400_BAD_REQUEST: "Bad request"
        }
    )
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            
            response = Response(
                {'detail': 'User registered successfully'},
                status=status.HTTP_201_CREATED
            )
            
            # Set cookies
            self.set_token_cookie(response, access_token, 'access')
            self.set_token_cookie(response, refresh_token, 'refresh')
            
            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenObtainPairView(CookieMixin, TokenObtainPairView):
    authentication_classes = ()
    @swagger_auto_schema(
        operation_summary="登入",
    )
    def post(self, request, *args, **kwargs):
        # TokenObtainPairView.post()
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # Set cookies, CookieMixin.set_token_cookie() 
            self.set_token_cookie(response, response.data['access'], 'access')
            self.set_token_cookie(response, response.data['refresh'], 'refresh')
            
            # Remove tokens from response body
            response.data = {'detail': 'Successfully logged in'}
            
        return response

class CustomTokenRefreshView(CookieMixin, TokenRefreshView):
    @swagger_auto_schema(
        operation_summary="refresh cookie 的 token pair",
        operation_description='''
        當 access token 過期時，使用 refresh token 得到新的 access token 及 refresh token。
        當 refresh token 過期時，會回傳 401 Unauthorized，前端應提示使用者重新登入。
        ''',
    )
    def post(self, request, *args, **kwargs):
        # Get refresh token from cookie
        refresh_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'])
        if refresh_token:
            request.data['refresh'] = refresh_token
        
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # Set new access token and refresh token cookie
            self.set_token_cookie(response, response.data['access'], 'access')
            self.set_token_cookie(response, response.data['refresh'], 'refresh')
            
            # Remove token from response body
            response.data = {'detail': 'Token refreshed successfully'}
            
        return response
    
class LogoutView(APIView):
    @swagger_auto_schema(
        operation_summary="登出",
    )
    def post(self, request):
        response = Response({'detail': 'Successfully logged out'})
        response.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE'])
        response.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'])
        
        return response