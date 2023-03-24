from django.urls import include, path
#Landry
from rest_framework import routers

from .views import *

router = routers.DefaultRouter()
router.register(r'sendmail', celeryViewSet, basename="sendmail")
router.register(r'complateregister', complateRegisterViewSet, basename="complateregister")
router.register(r'initchangepass', initChangePassViewSet, basename="initchangepass")
router.register(r'endchangepass', changePassViewSet, basename="endchangepass")


# Wire up our API using automatic URL routing. changePassViewSet
urlpatterns = [
    path('', include(router.urls)),
]