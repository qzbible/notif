from django.urls import include, path
#Landry
from rest_framework import routers

from .views import *

router = routers.DefaultRouter()
router.register(r'sendmail', celeryViewSet, basename="sendmail")
router.register(r'accountcreat', ceatedAccountViewSet, basename="ceatedAccountViewSet")
router.register(r'feedback', feedbackCreateClientViewSet, basename="feedbackViewSet")
router.register(r'complateregister', complateRegisterViewSet, basename="complateregister")
router.register(r'initchangepass', initChangePassViewSet, basename="initchangepass")
router.register(r'endchangepass', changePassViewSet, basename="endchangepass")
router.register(r'task', taskView, basename="task")
router.register(r'affectation', affectationView, basename="affectation")
router.register(r'notification', notifViewSet, basename="notification")
router.register(r'askDemo', askDemoViewSet, basename="askDemoViewSet")
router.register(r'resetPassword', resetPasswordViewSet, basename="reset_password")
router.register(r'notifAudit', notifAuditViewSet, basename="audit_notif")

router.register(r'userAccountCreat', ceatedUserAccountViewSet, basename="ceatedUserAccountViewSet")
router.register(r'codeAuth', codeAuthUserViewSet, basename="codeAuthUserViewSet")
 
# Wire up our API using automatic URL routing.   
urlpatterns = [
    path('', include(router.urls)),
]