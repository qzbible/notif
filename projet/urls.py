from django.urls import include, path
#Landry
from rest_framework import routers

from .views import *

router = routers.DefaultRouter()

urlpatterns = [
    path('api/projet-start-audit/', NotificationStartProjetView.as_view(), name='create-email-task'),
    path('api/projet-end-audit/', NotificationEndProjetView.as_view(), name='create-email-task'),
]