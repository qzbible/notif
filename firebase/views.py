# views/notification_views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiExample
from drf_spectacular.openapi import OpenApiParameter
from django.contrib.auth.models import User
from .service import firebase_service
from .serializers import (
    SendNotificationSerializer,
    ReadingReminderSerializer,
    VerseOfDaySerializer,
    CoupleNotificationSerializer,
    UpdateFCMTokenSerializer,
    BulkNotificationSerializer
)
import logging

logger = logging.getLogger(__name__)

from rest_framework.permissions import AllowAny
class SendNotificationAPIView(APIView):
    """
    API pour envoyer des notifications Firebase personnalisées
    """
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=SendNotificationSerializer,
        examples=[
            OpenApiExample(
                'Notification de rappel de lecture',
                value={
                    "type": "reading_reminder",
                    "recipient": "token",
                    "recipient_value": "fcm_token_ey1234567890abcdef",
                    "title": "📖 Temps de lecture",
                    "body": "Il est temps de lire Jean 3:1-21",
                    "data": {
                        "reading_plan_id": "bible_year",
                        "day_number": "15",
                        "chapter": "Jean 3:1-21",
                        "screen": "reading"
                    },
                    "image_url": "https://example.com/bible-icon.png"
                },
                request_only=True,
            ),
            OpenApiExample(
                'Notification vers un topic',
                value={
                    "type": "verse_of_day",
                    "recipient": "topic",
                    "recipient_value": "verse_of_day",
                    "title": "✨ Verset du jour",
                    "body": "Car Dieu a tant aimé le monde...",
                    "data": {
                        "verse": "Car Dieu a tant aimé le monde qu'il a donné son Fils unique...",
                        "reference": "Jean 3:16",
                        "screen": "verse_of_day"
                    }
                },
                request_only=True,
            ),
            OpenApiExample(
                'Réponse de succès',
                value={
                    'message': 'Notification envoyée avec succès',
                    'status': 'success',
                    'code': 200,
                    'data': {
                        'firebase_message_id': 'projects/evangelists-febb9/messages/0:1234567890',
                        'notification_type': 'reading_reminder',
                        'recipient': 'token'
                    }
                },
                response_only=True,
                status_codes=['200'],
            ),
        ],
        description="Envoie une notification Firebase personnalisée à un token FCM ou un topic",
        summary="Envoyer une notification Firebase",
        tags=["Notifications Firebase"],
    )
    def post(self, request):
        serializer = SendNotificationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'message': 'Données invalides',
                'status': 'error',
                'code': 400,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            validated_data = serializer.validated_data
            notification_type = validated_data['type']
            recipient = validated_data['recipient']
            recipient_value = validated_data['recipient_value']
            title = validated_data['title']
            body = validated_data['body']
            data = validated_data.get('data', {})
            image_url = validated_data.get('image_url')
            
            # Ajouter le type dans les données
            data['type'] = notification_type
            
            # Envoyer selon le type de destinataire
            if recipient == 'token':
                result = firebase_service.send_to_token(recipient_value, title, body, data, image_url)
            elif recipient == 'topic':
                result = firebase_service.send_to_topic(recipient_value, title, body, data, image_url)
            
            if result['success']:
                return Response({
                    'message': 'Notification envoyée avec succès',
                    'status': 'success',
                    'code': 200,
                    'data': {
                        'firebase_message_id': result.get('message_id'),
                        'notification_type': notification_type,
                        'recipient': recipient
                    }
                })
            else:
                return Response({
                    'message': 'Erreur lors de l\'envoi de la notification',
                    'status': 'error',
                    'code': 500,
                    'error': result['error']
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Erreur dans SendNotificationAPIView: {e}")
            return Response({
                'message': 'Erreur serveur',
                'status': 'error',
                'code': 500,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SendReadingReminderAPIView(APIView):
    """
    API pour envoyer des rappels de lecture BibleCouple
    """
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=ReadingReminderSerializer,
        examples=[
            OpenApiExample(
                'Rappel de lecture quotidienne',
                value={
                    "user_id": 123,
                    "reading_plan_id": "bible_year_plan",
                    "day_number": 45,
                    "chapter": "Jean 3:1-21"
                },
                request_only=True,
            ),
            OpenApiExample(
                'Réponse de succès',
                value={
                    'message': 'Rappel de lecture envoyé avec succès',
                    'status': 'success',
                    'code': 200,
                    'data': {
                        'user_name': 'Marie Dubois',
                        'reading_plan': 'bible_year_plan',
                        'day_number': 45,
                        'chapter': 'Jean 3:1-21',
                        'firebase_message_id': 'projects/evangelists-febb9/messages/0:1234567890'
                    }
                },
                response_only=True,
                status_codes=['200'],
            ),
        ],
        description="Envoie un rappel de lecture quotidienne personnalisé à un utilisateur spécifique",
        summary="Envoyer un rappel de lecture",
        tags=["Notifications BibleCouple"],
    )
    def post(self, request):
        serializer = ReadingReminderSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'message': 'Données invalides',
                'status': 'error',
                'code': 400,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            validated_data = serializer.validated_data
            user_id = validated_data['user_id']
            reading_plan_id = validated_data['reading_plan_id']
            day_number = validated_data['day_number']
            chapter = validated_data['chapter']
            
            # Récupérer l'utilisateur et son token FCM
            try:
                user = User.objects.get(id=user_id)
                if not user.has_valid_fcm_token():
                    return Response({
                        'message': 'Utilisateur sans token FCM valide',
                        'status': 'error',
                        'code': 400,
                        'error': f'L\'utilisateur {user.username} n\'a pas de token FCM'
                    }, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({
                    'message': 'Utilisateur non trouvé',
                    'status': 'error',
                    'code': 404,
                    'error': f'Aucun utilisateur avec l\'ID {user_id}'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Envoyer la notification
            result = firebase_service.send_reading_reminder(
                user.get_fcm_token(),
                reading_plan_id,
                day_number,
                chapter,
                user.first_name
            )
            
            if result['success']:
                return Response({
                    'message': 'Rappel de lecture envoyé avec succès',
                    'status': 'success',
                    'code': 200,
                    'data': {
                        'user_name': f'{user.first_name} {user.last_name}'.strip(),
                        'reading_plan': reading_plan_id,
                        'day_number': day_number,
                        'chapter': chapter,
                        'firebase_message_id': result.get('message_id')
                    }
                })
            else:
                return Response({
                    'message': 'Erreur lors de l\'envoi du rappel',
                    'status': 'error',
                    'code': 500,
                    'error': result['error']
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Erreur dans SendReadingReminderAPIView: {e}")
            return Response({
                'message': 'Erreur serveur',
                'status': 'error',
                'code': 500,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SendVerseOfDayAPIView(APIView):
    """
    API pour envoyer le verset du jour
    """
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=VerseOfDaySerializer,
        examples=[
            OpenApiExample(
                'Verset du jour',
                value={
                    "verse": "Car Dieu a tant aimé le monde qu'il a donné son Fils unique, afin que quiconque croit en lui ne périsse point, mais qu'il ait la vie éternelle.",
                    "reference": "Jean 3:16",
                    "topic": "verse_of_day"
                },
                request_only=True,
            ),
            OpenApiExample(
                'Réponse de succès',
                value={
                    'message': 'Verset du jour envoyé avec succès',
                    'status': 'success',
                    'code': 200,
                    'data': {
                        'verse_reference': 'Jean 3:16',
                        'topic': 'verse_of_day',
                        'firebase_message_id': 'projects/evangelists-febb9/messages/0:1234567890'
                    }
                },
                response_only=True,
                status_codes=['200'],
            ),
        ],
        description="Envoie le verset du jour à tous les abonnés d'un topic",
        summary="Envoyer le verset du jour",
        tags=["Notifications BibleCouple"],
    )
    def post(self, request):
        serializer = VerseOfDaySerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'message': 'Données invalides',
                'status': 'error',
                'code': 400,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            validated_data = serializer.validated_data
            verse = validated_data['verse']
            reference = validated_data['reference']
            topic = validated_data.get('topic', 'verse_of_day')
            
            result = firebase_service.send_verse_of_day(topic, verse, reference)
            
            if result['success']:
                return Response({
                    'message': 'Verset du jour envoyé avec succès',
                    'status': 'success',
                    'code': 200,
                    'data': {
                        'verse_reference': reference,
                        'topic': topic,
                        'firebase_message_id': result.get('message_id')
                    }
                })
            else:
                return Response({
                    'message': 'Erreur lors de l\'envoi du verset',
                    'status': 'error',
                    'code': 500,
                    'error': result['error']
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Erreur dans SendVerseOfDayAPIView: {e}")
            return Response({
                'message': 'Erreur serveur',
                'status': 'error',
                'code': 500,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SendCoupleNotificationAPIView(APIView):
    """
    API pour envoyer des notifications de couple
    """
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=CoupleNotificationSerializer,
        examples=[
            OpenApiExample(
                'Notification de couple',
                value={
                    "couple_id": "couple_123",
                    "partner_user_id": 456,
                    "action": "completed_reading"
                },
                request_only=True,
            ),
            OpenApiExample(
                'Réponse de succès',
                value={
                    'message': 'Notification de couple envoyée avec succès',
                    'status': 'success',
                    'code': 200,
                    'data': {
                        'couple_id': 'couple_123',
                        'partner_name': 'Marie Dubois',
                        'action': 'completed_reading',
                        'sender_name': 'Jean Dupont',
                        'firebase_message_id': 'projects/evangelists-febb9/messages/0:1234567890'
                    }
                },
                response_only=True,
                status_codes=['200'],
            ),
        ],
        description="Envoie une notification d'activité de couple (lecture terminée, nouvelle réussite, etc.)",
        summary="Envoyer une notification de couple",
        tags=["Notifications BibleCouple"],
    )
    def post(self, request):
        serializer = CoupleNotificationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'message': 'Données invalides',
                'status': 'error',
                'code': 400,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            validated_data = serializer.validated_data
            couple_id = validated_data['couple_id']
            partner_user_id = validated_data['partner_user_id']
            action = validated_data['action']
            
            # Récupérer le partenaire
            try:
                partner = User.objects.get(id=partner_user_id)
                if not partner.has_valid_fcm_token():
                    return Response({
                        'message': 'Partenaire sans token FCM valide',
                        'status': 'error',
                        'code': 400,
                        'error': f'Le partenaire {partner.username} n\'a pas de token FCM'
                    }, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({
                    'message': 'Partenaire non trouvé',
                    'status': 'error',
                    'code': 404,
                    'error': f'Aucun utilisateur avec l\'ID {partner_user_id}'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Envoyer la notification
            current_user_name = request.user.first_name or request.user.username
            result = firebase_service.send_couple_notification(
                couple_id,
                current_user_name,
                action,
                partner.get_fcm_token()
            )
            
            if result['success']:
                return Response({
                    'message': 'Notification de couple envoyée avec succès',
                    'status': 'success',
                    'code': 200,
                    'data': {
                        'couple_id': couple_id,
                        'partner_name': f'{partner.first_name} {partner.last_name}'.strip(),
                        'action': action,
                        'sender_name': current_user_name,
                        'firebase_message_id': result.get('message_id')
                    }
                })
            else:
                return Response({
                    'message': 'Erreur lors de l\'envoi de la notification',
                    'status': 'error',
                    'code': 500,
                    'error': result['error']
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Erreur dans SendCoupleNotificationAPIView: {e}")
            return Response({
                'message': 'Erreur serveur',
                'status': 'error',
                'code': 500,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateFCMTokenAPIView(APIView):
    """
    API pour mettre à jour le token FCM d'un utilisateur
    """
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=UpdateFCMTokenSerializer,
        examples=[
            OpenApiExample(
                'Mise à jour token FCM',
                value={
                    "fcm_token": "ey1234567890abcdef_nouveau_token_fcm",
                    "device_type": "android"
                },
                request_only=True,
            ),
            OpenApiExample(
                'Réponse de succès',
                value={
                    'message': 'Token FCM mis à jour avec succès',
                    'status': 'success',
                    'code': 200,
                    'data': {
                        'user_id': 123,
                        'username': 'marie_dubois',
                        'device_type': 'android',
                        'token_updated': True
                    }
                },
                response_only=True,
                status_codes=['200'],
            ),
        ],
        description="Met à jour le token FCM de l'utilisateur connecté pour recevoir les notifications",
        summary="Mettre à jour le token FCM",
        tags=["Gestion FCM"],
    )
    def post(self, request):
        serializer = UpdateFCMTokenSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'message': 'Données invalides',
                'status': 'error',
                'code': 400,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            validated_data = serializer.validated_data
            fcm_token = validated_data['fcm_token']
            device_type = validated_data.get('device_type', 'android')
            
            # Mettre à jour le token FCM de l'utilisateur
            user = request.user
            user.update_fcm_token(fcm_token, device_type)
            
            logger.info(f"Token FCM mis à jour pour l'utilisateur {user.id}: {fcm_token[:20]}...")
            
            return Response({
                'message': 'Token FCM mis à jour avec succès',
                'status': 'success',
                'code': 200,
                'data': {
                    'user_id': user.id,
                    'username': user.username,
                    'device_type': device_type,
                    'token_updated': True
                }
            })
            
        except Exception as e:
            logger.error(f"Erreur dans UpdateFCMTokenAPIView: {e}")
            return Response({
                'message': 'Erreur serveur',
                'status': 'error',
                'code': 500,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BulkNotificationAPIView(APIView):
    """
    API pour envoyer des notifications en masse
    """
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=BulkNotificationSerializer,
        examples=[
            OpenApiExample(
                'Notification en masse',
                value={
                    "user_ids": [1, 2, 3, 4, 5],
                    "title": "🎉 Nouvelle fonctionnalité",
                    "body": "Découvrez les nouveaux plans de lecture de BibleCouple !",
                    "data": {
                        "type": "app_update",
                        "screen": "reading_plans",
                        "feature": "new_reading_plans"
                    }
                },
                request_only=True,
            ),
            OpenApiExample(
                'Réponse de succès',
                value={
                    'message': 'Notification en masse envoyée avec succès',
                    'status': 'success',
                    'code': 200,
                    'data': {
                        'total_users_targeted': 5,
                        'users_with_fcm_token': 4,
                        'notifications_sent': 4,
                        'firebase_message_id': 'projects/evangelists-febb9/messages/0:1234567890'
                    }
                },
                response_only=True,
                status_codes=['200'],
            ),
        ],
        description="Envoie une notification à plusieurs utilisateurs en une seule requête",
        summary="Envoyer des notifications en masse",
        tags=["Notifications Firebase"],
    )
    def post(self, request):
        serializer = BulkNotificationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'message': 'Données invalides',
                'status': 'error',
                'code': 400,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            validated_data = serializer.validated_data
            user_ids = validated_data['user_ids']
            title = validated_data['title']
            body = validated_data['body']
            data = validated_data.get('data', {})
            
            # Récupérer les utilisateurs avec tokens FCM valides
            users = User.objects.filter(
                id__in=user_ids,
                fcm_token_info__is_active=True
            ).exclude(fcm_token_info__token__isnull=True).exclude(fcm_token_info__token='')
            
            fcm_tokens = [user.get_fcm_token() for user in users if user.get_fcm_token()]
            
            if not fcm_tokens:
                return Response({
                    'message': 'Aucun utilisateur avec token FCM trouvé',
                    'status': 'error',
                    'code': 400,
                    'error': f'Parmi les {len(user_ids)} utilisateurs ciblés, aucun n\'a de token FCM valide'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Envoyer la notification
            result = firebase_service.send_to_multiple_tokens(fcm_tokens, title, body, data)
            
            if result['success']:
                return Response({
                    'message': 'Notification en masse envoyée avec succès',
                    'status': 'success',
                    'code': 200,
                    'data': {
                        'total_users_targeted': len(user_ids),
                        'users_with_fcm_token': len(users),
                        'notifications_sent': len(fcm_tokens),
                        'firebase_message_id': result.get('message_id')
                    }
                })
            else:
                return Response({
                    'message': 'Erreur lors de l\'envoi en masse',
                    'status': 'error',
                    'code': 500,
                    'error': result['error']
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Erreur dans BulkNotificationAPIView: {e}")
            return Response({
                'message': 'Erreur serveur',
                'status': 'error',
                'code': 500,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)