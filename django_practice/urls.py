"""
URL configuration for django_practice project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from accounts.views import UserRegistrationView, CustomTokenObtainPairView, CustomTokenRefreshView
from rest_framework.permissions import IsAdminUser
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.contrib.auth.decorators import login_required
from accounts.views import LogoutView

schema_view = get_schema_view(
    openapi.Info(
        title="Dinner 🐍",
        default_version='v1',
        description="This is a practice project for Django",
        contact=openapi.Contact(email="wendy-hsieh@big-data.com.tw"),
    ),
    public=True,
    permission_classes=(IsAdminUser,)
)

urlpatterns = [
    # using __hiddenadmin, __hiddenswagger instead of admin, swagger to avoid being accessed by malicious users/bots
    # Modern Restful API design prefer not using tailing slashes!!!
    # DRF will match URLs exactly as specified in your urls.py, so there's no automatic redirection from posts to posts/ 
    path('__hiddenadmin/', admin.site.urls),
    path('__hiddenswagger<format>/', login_required(schema_view.without_ui(cache_timeout=0)), name='schema-json'),
    path('__hiddenswagger/', login_required(schema_view.with_ui('swagger', cache_timeout=0)), name='schema-swagger-ui'),
    path('__hiddenredoc/', login_required(schema_view.with_ui('redoc', cache_timeout=0)), name='schema-redoc'),
    path('accounts/register', UserRegistrationView.as_view(), name='register'),
    path('accounts/token', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('accounts/token/refresh', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('accounts/logout', LogoutView.as_view(), name='logout'),
    path('posts', include('posts.urls')),
]
