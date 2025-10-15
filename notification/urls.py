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

 

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('board/', include('board.urls')),
    path('exigence/', include('exigence.urls')),
    path('file/', include('file.urls')),
    path('update/', include('updateMaster.urls')),
    path('auth-client/', include('authClient.urls')),
    path('security/', include('alert_security.urls')),
    path('notif/', include('mailing.urls')),
    path('projet/', include('projet.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),  # Endpoint pour le schéma JSON/YAML
    
    # Interface Swagger UI
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # Interface ReDoc (alternative à Swagger UI)
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('__healthcheck/', include('health_check.urls')),
]
