import random
from exigence.models import ExigenceMail, auth_code
from exigence.serializers import AcceptSerializer, ErrorResponseSerializer, ExigenceResponseSerializer, ExigenceSheduleSerializer, ExigenceUpdateSheduleSerializer, TaskSerializer
from exigence.service import accept_anwser, exigence_approver, exigence_notification, exigence_responsable, rejet_anwser, task_responsable
from exigence.serializers import ExigenceSerializer
# from exigence.utils import send_mail_created
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

from service.utils import send_mail_created
from celery import current_app
from dateutil.parser import parse as dateutil_parse
import pytz

def get_current_date_iso():
    now_utc = datetime.now(pytz.UTC)
    return now_utc.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

def add_days(date_str, days=30):
    dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    new_dt = dt + timedelta(days=days)
    return new_dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

def parse_date_to_730(date_str):
    """
    Convertit une date en datetime à 7h30.
    Si la date est dans le passé, retourne None pour exécution immédiate.
    """
    try:
        if '/' in date_str:
            # Format: '26/04/2025'
            day, month, year = date_str.split('/')
            target_datetime = timezone.make_aware(
                datetime(int(year), int(month), int(day), 7, 30, 0)
            )
        else:
            # Format ISO: '2025-02-12T22:23:52.900Z' ou autres formats
        
            parsed_date = dateutil_parse(date_str)
            # Remplacer l'heure par 7h30
            target_datetime = timezone.make_aware(
                datetime(parsed_date.year, parsed_date.month, parsed_date.day, 7, 30, 0)
            )
        
        return None
        # Vérifier si la date est dans le passé
        # now = timezone.now()
        # print(f"✅ Date actuelle: {now}")
        # if target_datetime <= now:
        #     print(f"⚠️ Date dans le passé détectée: {target_datetime}")
        #     print(f"   Heure actuelle: {now}")
        #     print("   → Exécution immédiate programmée")
        #     return None  # None = exécution immédiate pour Celery
        
        # print(f"✅ Tâche programmée pour: {target_datetime}")
        # return target_datetime
        
    except (ValueError, AttributeError) as e:
        raise ValueError(f"Format de date non supporté: {date_str}")

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
                    'id_action':"10",
                    'id_analysis':"10",
                    'id_reporting':"10",
                    'id_indicateur':"10",
                    'dealine': '12/02/2025',
                    'start_date' : "2025-02-12T22:23:52.900Z",
                    'time' : "20",
                    "type_task" : "EXIGENCE",
                    "lang":"en-US"
                    
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
        data = request.data
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
        # 2025-04-03T22:23:52.900Z
        try:

            if validated_data.get("type_task") == "EXIGENCE":
            # Envoi de l'email
                if validated_data.get("lang") != "fr-FR":
                    type_task="Requirement"
                else :
                    type_task="Exigence"
            elif validated_data.get("type_task") == "ACTION":
                type_task = "Action corrective"
                if validated_data.get("lang") != "fr-FR":
                    type_task="Corrective action"

            
            # Sauvegarde des données dans le modèle
            exigence = ExigenceMail.objects.create(
                object=validated_data.get("object"),
                description=validated_data.get("description"),
                company=validated_data.get("company"),
                dest_email=validated_data.get("dest_email"),
                sender_name=validated_data.get("sender_name"),
                dest_name=validated_data.get("dest_name"),
                url=validated_data.get("url"),
                method=validated_data.get("method" ) if validated_data.get("method" ) else "",
                base_url=validated_data.get("base_url"),
                jwt_token=validated_data.get("jwt_token"),
                id_action = validated_data.get("id_action"),
                id_analysis = validated_data.get("id_analysis"),
                id_reporting = validated_data.get("id_reporting"),
                id_indicateur = validated_data.get("id_indicateur"),
                dealine = validated_data.get("dealine") if validated_data.get("dealine") else add_days(get_current_date_iso()),
                start_date = validated_data.get("start_date") if validated_data.get("start_date") else get_current_date_iso(),
                time = validated_data.get("time"),
                type_task = validated_data.get("type_task"),
                lang = validated_data.get("lang", "fr-FR"),
            )
            
            # Gestion des scopes (s'il s'agit du modèle avec ArrayField)
            if "scope" in validated_data and validated_data.get("scope"):
                exigence.scope = validated_data.get("scope")
                exigence.save()
             
            if validated_data.get("type_task") == "EXIGENCE":
                # print("str(get_current_date_iso())", str(get_current_date_iso()))
                # print("str(get_current_date_iso()) valid", validated_data.get("start_date") if validated_data.get("start_date") else get_current_date_iso())
                # print('Exigence data start', parse_date_to_730(validated_data.get("start_date") if validated_data.get("start_date") else get_current_date_iso()))
                # target_time = timezone.now() + timedelta(minutes=2)
                

                eta_datetime = parse_date_to_730(validated_data.get("start_date") if validated_data.get("start_date") else get_current_date_iso())
                if eta_datetime is None:
                    task = exigence_responsable.apply_async(
                        args=[
                            validated_data.get("object"),
                            type_task,
                            validated_data.get("description"),
                            validated_data.get("dest_email"),
                            validated_data.get("sender_name"),
                            validated_data.get("dest_name"),
                            validated_data.get("company"), 
                            validated_data.get("url"),
                            validated_data.get("scope", []),
                            validated_data.get("time"),
                            validated_data.get("dealine") if validated_data.get("dealine") else add_days(get_current_date_iso()),
                            validated_data.get("start_date") if validated_data.get("start_date") else get_current_date_iso(),
                            None,
                            validated_data.get("lang")
                        ],
                        # eta=parse_date_to_730(validated_data.get("start_date"))
                    )
                else:
                    task = exigence_responsable.apply_async(
                        args=[
                            validated_data.get("object"),
                            type_task,
                            validated_data.get("description"),
                            validated_data.get("dest_email"),
                            validated_data.get("sender_name"),
                            validated_data.get("dest_name"),
                            validated_data.get("company"), 
                            validated_data.get("url"),
                            validated_data.get("scope", []),
                            validated_data.get("time"),
                            validated_data.get("dealine") if validated_data.get("dealine") else add_days(get_current_date_iso()),
                            validated_data.get("start_date") if validated_data.get("start_date") else get_current_date_iso(),
                            None,
                            validated_data.get("lang")
                        ],
                        eta=parse_date_to_730(validated_data.get("start_date"))
                    )
                # Sauvegarder l'ID de la tâche
                exigence.task_id = task.id
                exigence.save()
            elif validated_data.get("type_task") == "ACTION":
                type_task = "Action corrective"
                if validated_data.get("lang") != "fr-FR":
                    type_task="Corrective action"
                mail = task_responsable(
                    object= validated_data.get("object"),
                    type_task = type_task,
                    description= validated_data.get("description"),
                    dest_email=validated_data.get("dest_email"),
                    sender_name=validated_data.get("sender_name"),
                    dest_name= validated_data.get("dest_name"),
                    company= validated_data.get("company"), 
                    url= validated_data.get("url"),
                    during= validated_data.get("time"), 
                    start_date= validated_data.get("start_date"),
                    scope= validated_data.get("scope", []),
                    lang=validated_data.get("lang")
                )
            # Envoi de l'email 
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
                    'url': 'https://example.com/exigence/123',
                    'base_url': 'https://api.example.com',
                    'jwt_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
                    'scope': ['Périmètre 1', 'Périmètre 2'],
                    'id_action':"10",
                    'id_answer':"10",
                    'dealine': '12/02/2025',
                    'start_date' : "2025-02-12T22:23:52.900Z",
                    'time' : "20",
                    "type_task" : "EXIGENCE",
                    "lang":"en-US"
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
        data= request.data
       
        # Création de la tâche Celery
        try:
            # Sauvegarde des données dans le modèle
            exigence = ExigenceMail.objects.create(
                object=data.get("object"),
                description=data.get("description"),
                company=data.get("company"),
                dest_email=data.get("dest_email"),
                sender_name=data.get("sender_name"),
                dest_name=data.get("dest_name"),
                url=data.get("url"),
                method=data.get("method", "Sondage"),
                base_url=data.get("base_url"),
                jwt_token=data.get("jwt_token"),
                id_action = data.get("id_action", None), 
                dealine = data.get("dealine", None),
                start_date = data.get("start_date", None),
                time = data.get("time", None),
                type_task = data.get("type_task", None),
                id_answer = data.get("id_answer", None),
                lang = data.get("lang", "fr-FR"),
                is_notification=False,
                is_approver=True,

            )
            
            # Gestion des scopes (s'il s'agit du modèle avec ArrayField)
            if "scope" in data and data.get("scope"):
                exigence.scope = data.get("scope")
                exigence.save()
            
             
            if data.get("type_task") == "EXIGENCE":
                type_task = "Exigence"
                if data.get("lang") != "fr-FR":
                    type_task="Requirement"
            
                mail = exigence_approver(
                    object= data.get("object"),
                    type_task = type_task,
                    description= data.get("description"),
                    dest_email=data.get("dest_email"),
                    sender_name=data.get("sender_name"),
                    dest_name= data.get("dest_name"),
                    company= data.get("company"), 
                    url= data.get("url"),
                    time= data.get("time"),
                    deadline= data.get("dealine"),
                    start_date= data.get("start_date"),
                    scope= data.get("scope", []),
                    lang=data.get("lang")
                )
            elif data.get("type_task") == "CORRECT_ACTION":
                type_task = "Action corrective"
                # mail = task_responsable(
                #     object= validated_data.get("object"),
                #     type_task = type_task,
                #     description= validated_data.get("description"),
                #     dest_email=validated_data.get("dest_email"),
                #     sender_name=validated_data.get("sender_name"),
                #     dest_name= validated_data.get("dest_name"),
                #     company= validated_data.get("company"), 
                #     url= validated_data.get("url"),
                #     during= validated_data.get("time"), 
                #     start_date= validated_data.get("start_date"),
                #     scope= validated_data.get("scope", [])
                # )
            
            return Response( status=status.HTTP_201_CREATED )
        except Exception as e:
            return Response( status=status.HTTP_500_INTERNAL_SERVER_ERROR )
        
# Vue API
class ExigenceNotificationView(APIView):
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
                    'id_action':"10",
                    'id_answer':"10",
                    'dealine': '12/02/2025',
                    'start_date' : "2025-02-12T22:23:52.900Z",
                    'time' : "20",
                    "type_task" : "EXIGENCE",
                    "lang":"en-US"
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
        
        data = request.data
 
        # Création de la tâche Celery
        try:
            # Sauvegarde des données dans le modèle
            exigence = ExigenceMail.objects.create(
                object=data.get("object"),
                description=data.get("description"),
                company=data.get("company"),
                dest_email=data.get("dest_email"),
                sender_name=data.get("sender_name"),
                dest_name=data.get("dest_name"),
                url=data.get("url"),
                id_answer = data.get("id_answer", None),
                base_url=data.get("base_url"),
                jwt_token=data.get("jwt_token"),
                id_action = data.get("id_action"),
                is_notification = True,
                dealine = data.get("dealine"),
                start_date = data.get("start_date"),
                time = data.get("time"),
                type_task = data.get("type_task"),
                lang = data.get("lang", "fr-FR"),
            )
            
            # Gestion des scopes (s'il s'agit du modèle avec ArrayField)
            if "scope" in data and data.get("scope"):
                exigence.scope = data.get("scope")
                exigence.save()
            
             
            if data.get("type_task") == "EXIGENCE":
                type_task = "Exigence"
                if data.get("lang") != "fr-FR":
                    type_task="Requirement"
                mail = exigence_notification(
                    object= data.get("object"),
                    type_task = type_task,
                    description= data.get("description"),
                    dest_email=data.get("dest_email"),
                    sender_name=data.get("sender_name"),
                    dest_name= data.get("dest_name"),
                    company= data.get("company"), 
                    url= data.get("url"),
                    time= data.get("time"),
                    deadline= data.get("dealine"),
                    start_date= data.get("start_date"),
                    scope= data.get("scope", []),
                    lang=data.get("lang")
                )
            elif data.get("type_task") == "CORRECT_ACTION":
                type_task = "Action"
                # mail = task_responsable(
                #     object= validated_data.get("object"),
                #     type_task = type_task,
                #     description= validated_data.get("description"),
                #     dest_email=validated_data.get("dest_email"),
                #     sender_name=validated_data.get("sender_name"),
                #     dest_name= validated_data.get("dest_name"),
                #     company= validated_data.get("company"), 
                #     url= validated_data.get("url"),
                #     during= validated_data.get("time"), 
                #     start_date= validated_data.get("start_date"),
                #     scope= validated_data.get("scope", [])
                # )
            
            return Response( status=status.HTTP_201_CREATED )
        except Exception as e:
            return Response( status=status.HTTP_500_INTERNAL_SERVER_ERROR )
        
# Vue API
class sendMailAuthCodeView(APIView):
    permission_classes = [AllowAny]

    @extend_schema( 
        description=" ",
        summary="Créer une exigence",
        tags=["Exigences"],
    )
    
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
            expires_at =  timezone.now() + timezone.timedelta(minutes=3)
            custom_ins = ExigenceMail.objects.all().filter(jwt_token=jwt_token).first()
            if custom_ins == None:
                return  Response({
                    "message": "Token not found",
                    "status": "error", 
                    "code": status.HTTP_404_NOT_FOUND,
                },
                status=status.HTTP_404_NOT_FOUND
            )
            nbr = (
                auth_code.objects.all()
                .filter(
                    token=jwt_token,
                )
                .count()
            ) 
            current_datetime = datetime.now()
            current_datetime_string = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
            if nbr == 0:  
                auth_code_instance = auth_code.objects.create(
                    code=verification_code, 
                    token=jwt_token, 
                    expires_at=expires_at
                )
                if custom_ins !=None and custom_ins.lang == "fr-FR":
                    path = "notification/2fa_auth/2FA-auth-fr.html"
                    object = "Code d'authentification" + "[" + current_datetime_string  + "]"
                elif custom_ins !=None and custom_ins.lang == "en-US":
                    path = "notification/2fa_auth/2FA-auth-en.html"
                    object = "Authentication code" + "[" + current_datetime_string  + "]"

                else:
                    path = "notification/2fa_auth/2FA-auth-fr.html"
                    object = "Code d'authentification" + "[" + current_datetime_string  + "]"

                path_txt = "notification/2fa_auth/2FA-auth.txt"
                
                context = {  
                    "user_name": '',
                    "code_auth": auth_code_instance.code,
                    "company": custom_ins.company,
                    "name" : custom_ins.dest_name,
                    "back_url" :  "https://dev-backend.app.klivar.com/"
                } 
                html_content = render_to_string(path, context)
                text_content = render_to_string(path_txt, context)  
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
                
                if custom_ins !=None and custom_ins.lang == "fr-FR":
                    path = "notification/2fa_auth/2FA-auth-fr.html"
                    object = "Code d'authentification" + "[" + current_datetime_string  + "]"
                elif custom_ins !=None and custom_ins.lang == "en-US":
                    path = "notification/2fa_auth/2FA-auth-en.html"
                    object = "Authentication code" + "[" + current_datetime_string  + "]"

                else:
                    path = "notification/2fa_auth/2FA-auth-fr.html"
                    object = "Code d'authentification" + "[" + current_datetime_string  + "]"

                path_txt = "notification/2fa_auth/2FA-auth.txt" 

                context = {  
                    "user_name": "",
                    "code_auth": verification_code,
                    "company": custom_ins.company,
                    "name" : custom_ins.sender_name,
                    "back_url" :  "https://dev-backend.app.klivar.com/"
                } 
                
                html_content = render_to_string(path, context)
                text_content = render_to_string(path_txt, context) 
                
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

    @extend_schema( 
        description=" ",
        summary="Créer une exigence",
        tags=["Exigences"],
    )
    
    def post(self, request):
        """
        Valide un code d'authentification à 2 facteurs
        """
        try:  
            auth_header = request.headers.get('Authorization')
            jwt_token = None
            
            if auth_header and auth_header.startswith('Bearer '):
                jwt_token = auth_header[7:]  
            
            data = request.data
            
            try:
                auth_code_instance = auth_code.objects.get(token=jwt_token, code=data['code'])
            except auth_code.DoesNotExist:
                return Response(
                    {
                        "message": "Code d'authentification invalide",
                        "status": "error",
                        "code": status.HTTP_404_NOT_FOUND,
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
            
            # Vérification de l'expiration
            now = timezone.now()
            
            if auth_code_instance.expires_at < now:
                return Response(
                    {
                        "message": "Le code d'authentification a expiré",
                        "status": "error",
                        "code": status.HTTP_408_REQUEST_TIMEOUT,
                    },
                    status=status.HTTP_408_REQUEST_TIMEOUT,
                )
            
            # Le code est valide et non expiré
            id_action = None 
        
            instance_customUser = ExigenceMail.objects.filter(jwt_token=jwt_token).last() 
            
            if not instance_customUser:
                return Response(
                    {
                        "message": "Données utilisateur non trouvées",
                        "status": "error",
                        "code": status.HTTP_404_NOT_FOUND,
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
                
            id_action = instance_customUser.id_action
            id_analysis = instance_customUser.id_analysis
            scope = instance_customUser.scope
            id_reporting = instance_customUser.id_reporting
            id_indicateur = instance_customUser.id_indicateur
            type_task = instance_customUser.type_task
            
            # Suppression du code d'authentification après utilisation
            auth_code_instance.delete()
            
            if instance_customUser.is_notification :
                return Response(
                    {
                        "id_answer": instance_customUser.id_answer, 
                        "id_task": instance_customUser.id_action, 
                        "type_task": type_task, 
                        "is_read": True
                    }, 
                    status=status.HTTP_200_OK
                )
            if instance_customUser.is_approver :
                return Response(
                    {
                        "id_answer": instance_customUser.id_answer, 
                        "id_task": instance_customUser.id_action, 
                        "type_task": type_task, 
                        "is_read": False
                    }, 
                    status=status.HTTP_200_OK
                )
          
            return Response(
                {
                    "id": id_action, 
                    "id_analysis": id_analysis, 
                    "scope": scope, 
                    "id_reporting": id_reporting, 
                    "id_indicateur": id_indicateur, 
                    "type_task": type_task, 
                    "is_read": False
                }, 
                status=status.HTTP_200_OK
            )  
                
        except Exception as e:
            return Response(
                {
                    "message": "Erreur lors de la validation du code",
                    "status": "error",
                    "error": str(e),
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
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

  
# Vue API
class EndExigeneTaskView(APIView):
    permission_classes = [AllowAny]
    @extend_schema(  
        request=ExigenceSheduleSerializer,
        responses={
            201: ExigenceSheduleSerializer,
            400: ErrorResponseSerializer,
            401: OpenApiTypes.OBJECT,
            500: OpenApiTypes.OBJECT,
        },
        description=" ",
        summary="Créer une exigence",
         examples=[
            OpenApiExample(
                'Exemple de requête valide',
                value={
                    'id': 2
                    
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
        tags=["Exigences"],
    )
    
    def post(self, request):
        """
        Valide un code d'authentification à 2 facteurs
        """
        reporting_id = request.data.get('id')
     
        if not reporting_id:
            return Response({'error': 'id requis'}, status=400)
        
        task_exigences = ExigenceMail.objects.filter(id_reporting=str(reporting_id))
        for task in task_exigences:
            try:
                current_app.control.revoke(task.task_id, terminate=True)
                print(f"Tâche {task.task_id} annulée avec succès")
            except Exception as e:
                print(f"Impossible d'annuler la tâche {task.task_id}: {str(e)}")

        return Response({
            'message': f'Tâches reporting  annulée'
        })
    

# Vue API
class UpdateExigeneTaskView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(  
        request=ExigenceUpdateSheduleSerializer,
        responses={
            201: ExigenceUpdateSheduleSerializer,
            400: ErrorResponseSerializer,
            401: OpenApiTypes.OBJECT,
            500: OpenApiTypes.OBJECT,
        },
        description=" ",
        summary="Créer une exigence",
         examples=[
            OpenApiExample(
                'Exemple de requête valide',
                value={
                    'id': 2,
                    'new_date': '2025-02-12T22:23:52.900Z'
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
        tags=["Exigences"],
    )
    
    def post(self, request):
        """
        Valide un code d'authentification à 2 facteurs
        """
        reporting_id = request.data.get('id')
        new_date = request.data.get('new_date')
    
        if not reporting_id:
            return Response({'error': 'id requis'}, status=400)
        
        task_exigences = ExigenceMail.objects.filter(id_reporting=str(reporting_id))
        for task in task_exigences:
            try:
                current_app.control.revoke(task.task_id, terminate=True)
                print(f"Tâche {task.task_id} annulée avec succès")
            except Exception as e:
                print(f"Impossible d'annuler la tâche {task.task_id}: {str(e)}")

            # target_time = timezone.now() + timedelta(minutes=3)
            label = " [ Période de rapport mise à jour ]"
            if task.lang != "fr-FR":
                label = " [ Updated reporting period ]"
            eta_datetime = parse_date_to_730(new_date)
            if eta_datetime is None:
                task_revoke = exigence_responsable.apply_async(
                    args=[
                        task.object + label, 
                        task.type_task,
                        task.description,
                        task.dest_email,
                        task.sender_name,
                        task.dest_name,
                        task.company,
                        task.url,
                        task.scope,
                        task.time,
                        task.dealine,
                        task.start_date,
                        None,
                        task.lang
                    ],
                    # eta=parse_date_to_730(validated_data.get("start_date"))
                )
            else:
                task_revoke = exigence_responsable.apply_async(
                    args=[
                        task.object + label, 
                        task.type_task,
                        task.description,
                        task.dest_email,
                        task.sender_name,
                        task.dest_name,
                        task.company,
                        task.url,
                        task.scope,
                        task.time,
                        task.dealine,
                        task.start_date,
                        None,
                        task.lang
                    ],
                    eta=eta_datetime
                )
            # Sauvegarder l'ID de la tâche
            task.task_id = task_revoke.id
            task.save()
        # Récupérer l'ID de la tâche à annuler 
        return Response({
            'message': f'Tâche reprogrammer avec succès',
        })


# Vue API
class AcceptExigenceView(APIView):
    permission_classes = [AllowAny]
    @extend_schema(
        request=AcceptSerializer,
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
                    'title': '',
                    'email': 'destinataire@example.com', 
                    'dest_name': 'Marie Martin', 
                    'base_url': 'https://api.example.com', 
                    "type_task" : "EXIGENCE",
                    "lang":"en-US"
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
        tags=["Accept-Rejet"],
    )
    def post(self, request):
        data = request.data
        # Création de la tâche Celery
        print(f"Approve or rejet a task ----> {data}")
        
        try:
            if data.get("type_task") == "EXIGENCE":
            # Envoi de l'email
                if data.get("lang") != "fr-FR":
                    type_task="Requirement"
                else : 
                    type_task="Exigence"
            
            accept_anwser(
                data.get("object", ""),
                data.get("email", ""),
                type_task,
                data.get("description", ""),
                data.get("title", ""),
                data.get("dest_name", ""),
                data.get("company", ""),
                data.get("back_url", None),
                data.get("lang", "")
            ) 
            return Response( status=status.HTTP_201_CREATED )
        except Exception as e:
            return Response( status=status.HTTP_500_INTERNAL_SERVER_ERROR )
        
        
# Vue API
class RejetExigenceView(APIView):
    permission_classes = [AllowAny]
    @extend_schema(
        request=AcceptSerializer,
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
                     'title': '',
                    'email': 'destinataire@example.com', 
                    'dest_name': 'Marie Martin', 
                    'base_url': 'https://api.example.com', 
                    "type_task" : "EXIGENCE",
                    "lang":"en-US"
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
        tags=["Accept-Rejet"],
    )
    def post(self, request):
        data = request.data
        # Création de la tâche Celery
        try:
            if data.get("type_task") == "EXIGENCE":
            # Envoi de l'email
                if data.get("lang") != "fr-FR":
                    type_task="Requirement"
                else : 
                    type_task="Exigence"
            rejet_anwser(
                data.get("object", ""),
                data.get("email", ""),
                type_task,
                data.get("description", ""),
                data.get("title", ""),
                data.get("dest_name", ""),
                data.get("company", ""),
                data.get("back_url", None),
                data.get("lang", "")
            ) 
            return Response( status=status.HTTP_201_CREATED )
        except Exception as e:
            return Response( status=status.HTTP_500_INTERNAL_SERVER_ERROR )
        