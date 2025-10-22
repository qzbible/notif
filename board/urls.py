from django.urls import include, path
#Landry
from rest_framework import routers

from .views import *

router = routers.DefaultRouter()

urlpatterns = [
    path('decision/', DecisionView.as_view(), name='welcome'),
    path('meeting/', MeetingReminderView.as_view(), name='welcome'),
    path('instance/', CommitteeCreatedView.as_view(), name='welcome'),
    path('arbitrage/', ArbitrageCreatedView.as_view(), name='welcome'),
    path('comment/', SendCommentCreatedEmailAPIView.as_view(), name='welcome'),
    path('decision-one/', DecisionOneView.as_view(), name='welcome'),
    # DecisionView
    
    
    
    
]