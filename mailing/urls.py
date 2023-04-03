from django.urls import include, path
#Landry
from rest_framework import routers

from .views import *

router = routers.DefaultRouter()
router.register(r'sendmail', celeryViewSet, basename="sendmail")
router.register(r'complateregister', complateRegisterViewSet, basename="complateregister")
router.register(r'initchangepass', initChangePassViewSet, basename="initchangepass")
router.register(r'endchangepass', changePassViewSet, basename="endchangepass")
router.register(r'task', taskView, basename="task")
router.register(r'affectation', affectationView, basename="affectation")


# Wire up our API using automatic URL routing.
urlpatterns = [
    path('', include(router.urls)),
]