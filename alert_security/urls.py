from django.urls import include, path
#Landry
from rest_framework import routers

from .views import *

router = routers.DefaultRouter()

urlpatterns = [
    path('api/alert-security/', AlertSecurityMailView.as_view(), name='alert-security'),
    path("api/user-auth-code/", sendAuthCodeView.as_view(), name="alert-security-code-send"),
    path("api/validation-code/", ValidateAuthCodeView.as_view(), name="validate-email-auth-client"),
    # path("validate-devise/<int:pk>/", validate_device, name="validate-divise"),
    path('api/notification-network-security/', NotificationNetworkView.as_view(), name='notification-network-security'),
    
]