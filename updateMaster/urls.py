from django.urls import include, path
#Landry
from rest_framework import routers

from .views import *

router = routers.DefaultRouter()

urlpatterns = [
    path('api/assign-bug/', AssignBugView.as_view(), name='create-email-task'),
    path('api/resolve-bug/', ResolveBugView.as_view(), name='resolve-task') 
]