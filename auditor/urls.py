from django.urls import include, path
#Landry
from rest_framework import routers

from .views import *

router = routers.DefaultRouter()

urlpatterns = [
    
    path('api/mission-audit/', MissionAuditCreateView.as_view(), name='create-mission-audit'),
    path('api/demande-audit/', DemandeCreateView.as_view(), name='create-demande-audit'),

    path("api/user-auth-code/", sendMailAuthCodeView.as_view(), name="create-email-task"),
    path("api/validation-code/", ValidateAuthCodeView.as_view(), name="create-email-task"),

    
]

# 