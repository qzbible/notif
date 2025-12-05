# urls/notification_urls.py

from django.urls import path
from .views import (
    SendNotificationAPIView,
    SendReadingReminderAPIView,
    SendVerseOfDayAPIView,
    SendCoupleNotificationAPIView,
    UpdateFCMTokenAPIView,
    BulkNotificationAPIView
)

app_name = 'notifications'

urlpatterns = [
    # API générale pour envoyer des notifications
    path('send/', SendNotificationAPIView.as_view(), name='send_notification'),
    
    # APIs spécifiques BibleCouple
    path('reading-reminder/', SendReadingReminderAPIView.as_view(), name='send_reading_reminder'),
    path('verse-of-day/', SendVerseOfDayAPIView.as_view(), name='send_verse_of_day'),
    path('couple-notification/', SendCoupleNotificationAPIView.as_view(), name='send_couple_notification'),
    path('bulk/', BulkNotificationAPIView.as_view(), name='bulk_notification'),
    
    # Gestion des tokens FCM
    path('update-token/', UpdateFCMTokenAPIView.as_view(), name='update_fcm_token'),
]

# Dans votre urls.py principal
# from django.urls import path, include
# 
# urlpatterns = [
#     # ... autres patterns
#     path('api/notifications/', include('yourapp.urls.notification_urls')),
# ]