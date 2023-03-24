from django.urls import include, path
#Landry
from rest_framework import routers

from .views import *

router = routers.DefaultRouter()
router.register(r'sendmail', celeryViewSet, basename="sendmail")
router.register(r'complateRegister', complateRegisterViewSet, basename="complateRegister")


# Wire up our API using automatic URL routing.
urlpatterns = [
    path('', include(router.urls)),
]