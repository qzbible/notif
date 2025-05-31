from django.urls import include, path
#Landry
from rest_framework import routers

from .views import *

router = routers.DefaultRouter()

urlpatterns = [
    path('api/auth-client/', welcomeMailView.as_view(), name='welcome'),
    path("api/user-auth-code/", sendAuthClientCodeView.as_view(), name="create-email-auth-client"),
    path("api/validation-code/", ValidateAuthCodeView.as_view(), name="validate-email-auth-client"),

    path("api/otp-email/", MailVerificationView.as_view(), name="otp-emailt"),
    path("api/validate-email/", MailCodeValidationView.as_view(), name="validate-emailt"),
]