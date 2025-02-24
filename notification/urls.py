"""notification URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.conf.urls.static import static
from django.conf import settings

#Relatif à la Documentation
from rest_framework import permissions
from drf_yasg.views import get_schema_view as getshemaview
from drf_yasg import openapi
# from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

schema_view = getshemaview(
    openapi.Info(
        title="Documentation application de notification",
        default_version=' V0.00.01',
        description="Documentation des API",
        terms_of_service="http://5.189.181.239:9005/",
        contact=openapi.Contact(email="contact@ziyouma-agency.com"),
        license=openapi.License(name="Ziyouma Agency"),
    ),
    public=True,  # True to expose all API and False to exclude token's API
    # if IsAuthenticated 401 AllowAny
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('celery/', include('mailing.urls')),
    path(
        'doc/swagger.json',
        schema_view.without_ui(cache_timeout=0),
        name='schema-json'
    ),
    path(
        '',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui'
    ),
    path(
        'redoc/',
        schema_view.with_ui('redoc', cache_timeout=0),
        name='schema-redoc'
    ),
    path('__healthcheck/', include('health_check.urls')),
]
