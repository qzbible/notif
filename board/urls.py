from django.urls import include, path
#Landry
from rest_framework import routers

from .views import *

router = routers.DefaultRouter()

urlpatterns = [
    path('decision/', DecisionView.as_view(), name='welcome'),
    
    
    
    
]