import os
from django.shortcuts import render
 
# from mailing.serializers import StartProjectMailSerializer  
# from mailing.service import mail_notification_end_projet_service, mail_notification_start_projet_service
from projet.models import ProjetMail
from projet.serializers import IndicatorAlertSerializer, StartProjectMailSerializer
from projet.service import mail_alert_seuil_indicator, mail_notification_end_projet_service, mail_notification_start_projet_service
from rest_framework.permissions import AllowAny
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from rest_framework.response import Response
from rest_framework import status
from django.template.loader import render_to_string
from django.utils import timezone
import random
from datetime import datetime, timedelta
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes, authentication_classes

from service.utils import send_mail_created
# Create your views here.
from celery import current_app
# Vue API
class NotificationStartProjetView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=StartProjectMailSerializer,
        responses={
            201: StartProjectMailSerializer,
            400: StartProjectMailSerializer,
            401: OpenApiTypes.OBJECT,
            500: OpenApiTypes.OBJECT,
        },
        examples=[
                OpenApiExample(
                    'Exemple de requête valide',
                value={
                    'name': 'samuel',
                    'projet_id': 100,
                    'email': 'client@example.com',
                    'title': 'Ziyouma',
                    'end_date': 'Jean Dupont',
                    'start_date':  'Ziyouma',
                    'company': 'Ziyouma',
                    'description': 'Ziyouma',
                    'url': '', 
                    'base_url': 'https://api.example.com',
                    'lang' :"Fr-fr" 
                },
                    request_only=True,
                ),
                OpenApiExample(
                    'Réponse de succès',
                    value={
                        'message': 'Mail créée avec succès',
                        'status': 'success',
                        'code': 201
                    },
                    response_only=True,
                    status_codes=['201'],
                ),
            ],
            description="",
            summary="Créer une auth code auth",
            tags=["Projet audit"],
        )
    
    
    def post(self, request):
        """
            Envoie un code d'authentification à 2 facteurs par email
        """
        try:   
            data = request.data 
            
    # task_id = models.CharField(max_length=255, null=True, blank=True)
            project_ins = ProjetMail.objects.create(
                projet_id = data.get('projet_id', None),
                user_email = data.get('email', None)
            )
            mail_notification_start_projet_service( 
                name = data.get('name', ''),
                dest_email = data.get('email', None),
                company = data.get('company', 'klivar'), 
                title= data.get('title', None),
                end_date = data.get('end_date', None),
                start_date= data.get('start_date', None),
                description = data.get('description', None),
                url = data.get('url', None),  
                lang=data.get('lang', None)
            )
            # Inclure le token JWT dans la réponse si récupéré
            response_data = {
                "message": "your request was do successfully",
                "status": "success", 
                "code": status.HTTP_200_OK,
            } 
            return Response(response_data, status.HTTP_200_OK)
                
        except Exception as e:
            return Response(
                {
                    "message": "Erreur lors de l'envoi du code d'authentification",
                    "status": "error",
                    "error": str(e),
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        


# Vue API
class NotificationEndProjetView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=StartProjectMailSerializer,
        responses={
            201: StartProjectMailSerializer,
            400: StartProjectMailSerializer,
            401: OpenApiTypes.OBJECT,
            500: OpenApiTypes.OBJECT,
        },
        examples=[
                OpenApiExample(
                    'Exemple de requête valide',
                value={
                    'name': 'samuel',
                    'email': 'client@example.com',
                    'title': 'Ziyouma', 
                    'company': 'Ziyouma',
                    'description': 'Ziyouma',
                    'url': '', 
                    'base_url': 'https://api.example.com',
                    'lang' :"Fr-fr" 
                },
                    request_only=True,
                ),
                OpenApiExample(
                    'Réponse de succès',
                    value={
                        'message': 'Mail créée avec succès',
                        'status': 'success',
                        'code': 201
                    },
                    response_only=True,
                    status_codes=['201'],
                ),
            ],
            description="",
            summary="Créer une auth code auth",
            tags=["Projet audit"],
        )
    
    
    def post(self, request):
        """
            Envoie un code d'authentification à 2 facteurs par email
        """
        try:   
            data = request.data 
            mail_notification_end_projet_service( 
                name = data.get('name', ''),
                dest_email = data.get('email', None),
                company = data.get('company', 'klivar'), 
                title= data.get('title', None), 
                description = data.get('description', None),
                url = data.get('url', None),  
                lang=data.get('lang', None)
            )
            # Inclure le token JWT dans la réponse si récupéré
            response_data = {
                "message": "your request was do successfully",
                "status": "success", 
                "code": status.HTTP_200_OK,
            } 
            return Response(response_data, status.HTTP_200_OK)
                
        except Exception as e:
            return Response(
                {
                    "message": "Erreur lors de l'envoi du code d'authentification",
                    "status": "error",
                    "error": str(e),
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        



class IndicatorAlertView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=IndicatorAlertSerializer,
        responses={
            201: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT,
            500: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                'Exemple de requête valide',
                value={
                    'id_indicator': 20,
                    'id_project': 20,
                    'title': 'Taux de satisfaction client',
                    'description': 'Indicateur de satisfaction en baisse critique',
                    'seuil': '80%',
                    'date_alert': '2025-10-16T13:28:06.092Z',
                    'reportion_title': 'Rapport Q3 2025',
                    'percent_value': '65%',
                    'url_connect': 'https://app.klivar.fr/dashboard/indicators/123',
                    'lang': 'fr-FR',
                    'actors': [
                        {
                            'email': 'manager@company.com',
                            'first_name': 'Jean',
                            'last_name': 'Dupont',
                            'role': 'Manager'
                        },
                        {
                            'email': 'director@company.com',
                            'first_name': 'Marie',
                            'last_name': 'Martin',
                            'role': 'Directeur'
                        }
                    ],
                    'client': {
                        'id': 'contact@client.com',
                        'denomination': 'Société ABC',
                        
                    }
                },
                request_only=True,
            ),
            OpenApiExample(
                'Réponse de succès',
                value={
                    'message': 'Alerte envoyée avec succès',
                    'status': 'success',
                    'code': 201,
                    'data': {
                        'alert_id': 123,
                        'emails_sent': 3,
                        'task_id': 'alert-task-xyz123'
                    }
                },
                response_only=True,
                status_codes=['201'],
            ),
            OpenApiExample(
                'Erreur de validation',
                value={
                    'message': 'Données invalides',
                    'status': 'error',
                    'code': 400,
                    'errors': {
                        'title': ['Ce champ est requis.'],
                        'actors': ['La liste des acteurs ne peut pas être vide']
                    }
                },
                response_only=True,
                status_codes=['400'],
            ),
        ],
        description="Envoie une notification d'alerte lorsqu'un indicateur passe sous le seuil défini. "
                    "L'alerte est envoyée à tous les acteurs spécifiés et optionnellement au client.",
        summary="Envoyer une alerte d'indicateur sous le seuil",
        tags=["Alertes & Notifications"],
    )
    def post(self, request):
        """
        Envoie une alerte par email lorsqu'un indicateur passe sous le seuil
        """
        try:
            # Validation des données avec le serializer
            serializer = IndicatorAlertSerializer(data=request.data)
            
            if not serializer.is_valid():
                return Response(
                    {
                        "message": "Données invalides",
                        "status": "error",
                        "code": status.HTTP_400_BAD_REQUEST,
                        "errors": serializer.errors
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            validated_data = serializer.validated_data
            
            # Créer l'enregistrement dans la base de données
            alert_instance,  created = IndicatorAlertSerializer.objects.get_or_create(
                id_indicator =  validated_data.get('id_indicator'),
                id_project =  validated_data.get('id_project'),
                title=validated_data.get('title'),
                description=validated_data.get('description'),
                seuil=validated_data.get('seuil'),
                date_alert=validated_data.get('date_alert'),
                reporting_title=validated_data.get('reportion_title'),
                percent_value=validated_data.get('percent_value'),
                actors=validated_data.get('actors', []),
                url_connect=validated_data.get('url_connect'),
                client=validated_data.get('client', None)
            )
            client = validated_data.get('client', None)
            # si is allready created remove old task
            if created == False :
                if alert_instance.task_id :
                    current_app.control.revoke(alert_instance.task_id, terminate=True) 
                    print(f"Tâche {alert_instance.task_id} annulée avec succès")
                     
            if validated_data.get('date_alert', None):
                new_task = mail_alert_seuil_indicator.apply_async(
                            args=[
                                validated_data.get('reportion_title'),
                                validated_data.get('msg'),
                                validated_data.get('title'),
                                validated_data.get('percent_value'),
                                validated_data.get('seuil'),
                                client.get('denomination', 'Klivar') if client else 'Klivar',
                                validated_data.get('date_alert'),
                                validated_data.get('description'),
                                validated_data.get('url_connect'),
                                os.environ.get("BACK_HOST_URL", ""),
                                validated_data.get('lang', 'fr-FR'),
                                validated_data.get('actors', []) 
                            ],
                            eta=validated_data.get('date_alert', None)
                        )
                alert_instance.task_id = new_task.id
                alert_instance.save()
            else:
                mail_alert_seuil_indicator.apply_async(
                            args=[
                                validated_data.get('reportion_title'),
                                validated_data.get('msg'),
                                validated_data.get('title'),
                                validated_data.get('percent_value'),
                                validated_data.get('seuil'),
                                client.get('denomination', 'Klivar') if client else 'Klivar',
                                validated_data.get('date_alert'),
                                validated_data.get('description'),
                                validated_data.get('url_connect'),
                                os.environ.get("BACK_HOST_URL", ""),
                                validated_data.get('lang', 'fr-FR'),
                                validated_data.get('actors', []) 
                            ]
                        )
                alert_instance.task_id = new_task.id
                alert_instance.save()
            
            response_data = {
                "message": "Alerte envoyée avec succès",
                "status": "success",
                "code": status.HTTP_201_CREATED,
                "data": {
                    "alert_id": alert_instance.id,
                    "emails_sent": len(validated_data.get('actors', [])) ,
                    "task_id": alert_instance.task_id, 
                }
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {
                    "message": "Erreur lors de l'envoi de l'alerte",
                    "status": "error",
                    "error": str(e),
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

