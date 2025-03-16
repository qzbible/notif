import random
from exigence.models import ExigenceMail, auth_code
from exigence.serializers import ErrorResponseSerializer, ExigenceResponseSerializer
from exigence.service import exigence_approver, exigence_responsable
from exigence.serializers import ExigenceSerializer
from exigence.utils import send_mail_created
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from django.shortcuts import get_object_or_404

from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
 
from rest_framework.permissions import IsAuthenticated
from collections import OrderedDict
 
import json
 
from rest_framework.views import APIView
import uuid
from datetime import datetime, timedelta
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
import shutil
 
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from drf_spectacular.types import OpenApiTypes
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view
from django.template.loader import render_to_string

from django.utils import timezone

# Vue API
class ExigenceResponsableView(APIView):
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=ExigenceSerializer,
        responses={
            201: ExigenceResponseSerializer,
            400: ErrorResponseSerializer,
            401: OpenApiTypes.OBJECT,
            500: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                'Exemple de requête valide',
                value={
                    'object': 'Demande d\'exigence',
                    'description': 'Description détaillée de l\'exigence',
                    'company': 'Ziyouma',
                    'dest_email': 'destinataire@example.com',
                    'sender_name': 'Jean Dupont',
                    'dest_name': 'Marie Martin',
                    'url': 'https://example.com/exigence/123',
                    'method': 'POST',
                    'base_url': 'https://api.example.com',
                    'jwt_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
                    'scope': ['Périmètre 1', 'Périmètre 2'],
                    'id_action':"10"
                },
                request_only=True,
            ),
            OpenApiExample(
                'Réponse de succès',
                value={
                    'message': 'Exigence créée avec succès',
                    'status': 'success',
                    'code': 201
                },
                response_only=True,
                status_codes=['201'],
            ),
        ],
        description="Crée une exigence et envoie une notification par email",
        summary="Créer une exigence",
        tags=["Exigences"],
    )
    def post(self, request):
        serializer = ExigenceSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {
                    "message": "Erreur de validation des données",
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Récupération des données validées
        validated_data = serializer.validated_data
        
        try:
            # Sauvegarde des données dans le modèle
            exigence = ExigenceMail.objects.create(
                object=validated_data.get("object"),
                description=validated_data.get("description"),
                company=validated_data.get("company"),
                dest_email=validated_data.get("dest_email"),
                sender_name=validated_data.get("sender_name"),
                dest_name=validated_data.get("dest_name"),
                url=validated_data.get("url"),
                method=validated_data.get("method"),
                base_url=validated_data.get("base_url"),
                jwt_token=validated_data.get("jwt_token"),
                id_action = validated_data.get("id_action")
            )
            
            
            # Gestion des scopes (s'il s'agit du modèle avec ArrayField)
            if "scope" in validated_data and validated_data.get("scope"):
                exigence.scope = validated_data.get("scope")
                exigence.save()
            
            
            # Envoi de l'email
            mail = exigence_responsable(
                validated_data.get("object"),
                validated_data.get("description"),
                validated_data.get("dest_email"),
                validated_data.get("sender_name"),
                validated_data.get("dest_name"),
                validated_data.get("company"),
                validated_data.get("url")
            )
            
            return Response(
                {
                    "message": "Exigence créée avec succès",
                    "status": "success",
                    "code": 201,
                    "id": exigence.id
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            # Log l'erreur pour le débogage
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erreur lors de la création de l'exigence: {str(e)}")
            
            return Response(
                {
                    "message": "Une erreur est survenue lors du traitement de la demande",
                    "status": "error"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

# Vue API
class ExigenceApprobatorView(APIView):
    permission_classes = [AllowAny]
    @extend_schema(
        request=ExigenceSerializer,
        responses={
            201: ExigenceResponseSerializer,
            400: ErrorResponseSerializer,
            401: OpenApiTypes.OBJECT,
            500: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                'Exemple de requête valide',
                value={
                    'object': 'Demande d\'exigence',
                    'description': 'Description détaillée de l\'exigence',
                    'company': 'Ziyouma',
                    'dest_email': 'destinataire@example.com',
                    'sender_name': 'Jean Dupont',
                    'dest_name': 'Marie Martin',
                    'url': 'https://example.com/exigence/123'
                },
                request_only=True,
            ),
            OpenApiExample(
                'Réponse de succès',
                value={
                    'message': 'Exigence créée avec succès',
                    'status': 'success',
                    'code': 201
                },
                response_only=True,
                status_codes=['201'],
            ),
        ],
        description="Crée une exigence et envoie une notification par email",
        summary="Créer une exigence",
        tags=["Exigences"],
    )
    def post(self, request):
        serializer = ExigenceSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {
                    "message": "Erreur de validation des données",
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            ) 
        # Récupération des données validées
        object_text = serializer.validated_data.get("object") 
        description = serializer.validated_data.get("description")
        company = serializer.validated_data.get("company")
        dest_email = serializer.validated_data.get("dest_email")
        sender_name = serializer.validated_data.get("sender_name")
        dest_name = serializer.validated_data.get("dest_name")
        url = serializer.validated_data.get("url")
 
        # Création de la tâche Celery
        try:
            mail = exigence_approver(object_text,description, dest_email, sender_name, dest_name, company, url )
            return Response( status=status.HTTP_201_CREATED )
        except Exception as e:
            return Response( status=status.HTTP_500_INTERNAL_SERVER_ERROR )
        


# Vue API
class sendMailAuthCodeView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        """
        Envoie un code d'authentification à 2 facteurs par email
        """
        try:  
            auth_header = request.headers.get('Authorization')
            jwt_token = None
            
            if auth_header and auth_header.startswith('Bearer '):
                jwt_token = auth_header[7:]  # Enlever le préfixe 'Bearer '
            
            # Générer le code de vérification
            verification_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            expires_at =  timezone.now() + timezone.timedelta(minutes=30)
            
            nbr = (
                auth_code.objects.all()
                .filter(
                    token=jwt_token,
                )
                .count()
            ) 
            
            if nbr == 0: 
                auth_code_instance = auth_code.objects.create(
                    code=verification_code, 
                    token=jwt_token, 
                    expires_at=expires_at
                )
                
                path = "notification/2fa_auth/2FA-auth.html"
                path_txt = "notification/2fa_auth/2FA-auth.txt"
                
                context = {  
                    "user_name": '',
                    "code_auth": auth_code_instance.code,
                }
                
                html_content = render_to_string(path, context)
                text_content = render_to_string(path_txt, context) 
                object = "code d'authentification"
                
              
                custom_ins = ExigenceMail.objects.all().filter(jwt_token=jwt_token).first()
                send_mail_created(
                    [custom_ins.dest_email], 
                    object, 
                    text_content, 
                    html_content,
                    custom_ins.company
                )
            else: 
                auth_code_instance = auth_code.objects.get(token=jwt_token)
                auth_code_instance.code = verification_code
                auth_code_instance.expires_at = expires_at
                auth_code_instance.save() 
                
                path = "notification/2fa_auth/2FA-auth.html"
                path_txt = "notification/2fa_auth/2FA-auth.txt" 
                
                context = {  
                    "user_name": "",
                    "code_auth": verification_code,
                } 
                
                html_content = render_to_string(path, context)
                text_content = render_to_string(path_txt, context) 
                object = "code d'authentification"
                
                custom_ins = ExigenceMail.objects.all().filter(jwt_token=jwt_token).first()
                send_mail_created(
                    [custom_ins.dest_email], 
                    object, 
                    text_content, 
                    html_content,
                    custom_ins.company
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
class ValidateAuthCodeView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Envoie un code d'authentification à 2 facteurs par email
        """
        try:  
            auth_header = request.headers.get('Authorization')
            jwt_token = None
            
            if auth_header and auth_header.startswith('Bearer '):
                jwt_token = auth_header[7:]  
            auth_code_instance = auth_code.objects.get(token=jwt_token) 
            date_str = auth_code_instance.expires_at 
            now = datetime.now() 
        
            id_action = None 
        
            instance_customUser = ExigenceMail.objects.filter(jwt_token=jwt_token).last() 
            id_action = instance_customUser.id_action
            # auth_code_instance.delete()
            return Response({"id":id_action}, status.HTTP_200_OK)  
        except  Exception as e:
            return Response(
                {
                    "message": "validation auth Not Found",
                    "status": "Not Found",
                    "error": str(e),
                    "code": status.HTTP_404_NOT_FOUND,
                }
            )
        


@api_view(["POST"]) 
def validateAuthCode(request, token=None):
    """
    list all users permissions a model instance by {{id}} from data source
    :param self:
    :param pk:
    :return:
    """  
    try:  
        auth_header = request.headers.get('Authorization')
        jwt_token = None
        
        if auth_header and auth_header.startswith('Bearer '):
            jwt_token = auth_header[7:]  
        auth_code_instance = auth_code.objects.get(token=jwt_token) 
        date_str = auth_code_instance.expires_at 
        now = datetime.now() 
        if date_str <= now: 
            return Response(
                {
                    "message": "your request was do successfully",
                    "status": "success",
                    "code": status.HTTP_408_REQUEST_TIMEOUT,
                },
                status.HTTP_408_REQUEST_TIMEOUT,
            )
        else: 
            id_action = None 
            if str(auth_code_instance.code)==str(request.data['code']): 

                instance_customUser = ExigenceMail.objects.filter(token=jwt_token).last() 
                id_action = instance_customUser.id_action
                # auth_code_instance.delete()
                return Response({"id":id_action}, status.HTTP_200_OK)  
    except  Exception as e:
        return Response(
            {
                "message": "validation auth Not Found",
                "status": "Not Found",
                "error": str(e),
                "code": status.HTTP_404_NOT_FOUND,
            }
        )


            

 