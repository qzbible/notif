from django.shortcuts import render
 
# from mailing.serializers import StartProjectMailSerializer  
# from mailing.service import mail_notification_end_projet_service, mail_notification_start_projet_service
from projet.models import ProjetMail
from projet.service import mail_notification_start_projet_service
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




# Vue API

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
        
