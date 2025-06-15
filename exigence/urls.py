from django.urls import include, path
#Landry
from rest_framework import routers

from .views import *

router = routers.DefaultRouter()

urlpatterns = [
    path('api/responsable/', ExigenceResponsableView.as_view(), name='create-email-task'),
    path('api/approver/', ExigenceApprobatorView.as_view(), name='create-email-task'),
    path('api/notification/', ExigenceNotificationView.as_view(), name='create-email-task'),
    # path('api/responsable/', ExigenceResponsableView.as_view(), name='create-email-task'),
    path("api/user-auth-code/", sendMailAuthCodeView.as_view(), name="create-email-task"),
    path("api/validation-code/", ValidateAuthCodeView.as_view(), name="create-email-task"),

    path("api/end-exigence-scheduled/", EndExigeneTaskView.as_view(), name="exigence-down-scheduled"),
    path("api/update-exigence-scheduled/", UpdateExigeneTaskView.as_view(), name="exigence-down-scheduled"),
]