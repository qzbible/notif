from django.urls import include, path
#Landry
from rest_framework import routers

from .views import *

router = routers.DefaultRouter()

urlpatterns = [
    path('api/auth/', ExigenceResponsableView.as_view(), name='create-email-task'),
]