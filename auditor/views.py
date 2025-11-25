import os
from django.shortcuts import render
import random
# Create your views here.
from auditor.models import Task
from auditor.serializers import  MissionAuditSerializer
from auditor.service import service_demand, service_mission
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework import serializers

from rest_framework.permissions import AllowAny
from django.utils import timezone
from django.template.loader import render_to_string

from datetime import datetime, timedelta

from service.utils import get_formatted_date, send_mail_created

class MissionAuditCreateView(APIView):
    permission_classes = [AllowAny]
    """Vue pour créer et lancer une mission d'audit"""
    
    @extend_schema(
        request=MissionAuditSerializer,
        responses={
            201: MissionAuditSerializer,
            400: serializers.Serializer,  # Erreurs de validation
        },
        examples=[
            OpenApiExample(
                'Exemple de mission d\'audit',
                value={
                    'mission_name': 'Audit RGPD Q1 2025',
                    'title': 'Évaluation de conformité RGPD - Premier trimestre',
                    'description': 'Audit complet de la conformité RGPD incluant l\'analyse des traitements de données personnelles et des mesures de sécurité.',
                    'mission_type': 'COMPLIANCE', 
                    'start_date': '2025-02-01T09:00:00Z',
                    'end_date': '2025-02-21T17:00:00Z', 
                    'company': 'Entreprise ABC',
                    'auditor' : [
                       {
                            "name": "Jean Martin",
                            "email" : "samyfabiol@gmail.com"
                       }
                    ],
                   
                    'access_url': 'https://app.klivar.com/audit/123',
                    'base_url': 'https://api.klivar.com/',
                    'language': 'fr-FR',
                    'id_client': 456,
                    'id_mission': 789
                },
                request_only=True,
            ),
        ],
        description="Crée une nouvelle mission d'audit et envoie une notification de lancement",
        summary="Créer une mission d'audit",
        tags=["Missions d'Audit"],
    )
    def post(self, request):
        
        
        try:
            # Créer la mission 
            data = request.data
            users = data.get("auditor", [{}])
            for user in users:
                instance = Task.objects.create(
                    title=data.get("title"),
                    description=data.get("description"),
                    mission_type=data.get("mission_type", "COMPLIANCE"),
                    start_date=data.get("start_date"),
                    end_date=data.get("end_date"),
                    auditor_name=user.get("name"),
                    auditor_email=user.get("email"),
                    company=data.get("company"),
                    access_url=data.get("access_url"),
                    base_url=data.get("base_url"),
                    is_mission=True,
                )
                # Ici vous pourriez déclencher l'envoi d'email
                # launch_mission_email.delay(mission.id)
                if 'fr' in request.data.get('language', 'fr-FR'): 
                    prefix_object = "[MISSION D'AUDIT]"
                else: 
                    prefix_object = "[AUDIT MISSION]"
                print('urls', os.environ.get("BACK_HOST_URL", ""))
                task = service_mission.apply_async(
                    args=[
                        prefix_object + " "+data.get("title"),
                        data.get("title"),
                        data.get("mission_name"),
                        data.get("description"),
                        user.get("email"),
                        data.get("mission_type"),
                        user.get("name"),
                        data.get("company"), 
                        data.get("access_url"),
                        data.get("start_date", ''),
                        data.get("end_date", ''), 
                        None,
                        data.get("language", 'fr-FR'),
                    ]
                ) 
            # Sauvegarder l'ID de la tâche 
            return Response(
                {
                    "message": "Mission d'audit créée avec succès",
                    "status": "success",
                    "code": 201,
                    "mission_id": instance.id
                },
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            return Response(
                {
                    "message": "Erreur lors de la création de la mission " + str(e),
                    "status": "error"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class DemandeCreateView(APIView):
    permission_classes = [AllowAny]
    """Vue pour créer et lancer une mission d'audit"""
    
    @extend_schema(
        request=MissionAuditSerializer,
        responses={
            201: MissionAuditSerializer,
            400: serializers.Serializer,  # Erreurs de validation
        },
        examples=[
            OpenApiExample(
                'Exemple de mission d\'audit',
                value={ 
                    'title': 'Évaluation de conformité RGPD - Premier trimestre',
                    'description': 'Audit complet de la conformité RGPD incluant l\'analyse des traitements de données personnelles et des mesures de sécurité.', 
                    'start_date': '2025-02-01T09:00:00Z',
                    'end_date': '2025-02-21T17:00:00Z', 
                    'company': 'Entreprise ABC',
                    "auditor_name": "Jean Martin",
                    "auditor_email" : "samyfabiol@gmail.com", 
                    'access_url': 'https://app.klivar.com/audit/123',
                    'base_url': 'https://api.klivar.com/',
                    'language': 'fr-FR',
                    'jwt_token': 'yrtyrgtryugh ytoton jwt', 
                    "test": "Ceci est un test",
                    'id_client': 456,
                    'id_demande': 789
                },
                request_only=True,
            ),
        ],
        description="Crée une nouvelle mission d'audit et envoie une notification de lancement",
        summary="Créer une mission d'audit",
        tags=["Missions d'Audit"],
    )
    def post(self, request):
        try:
            # Créer la mission 
            data = request.data 
            instance = Task.objects.create(
                title=data.get("title"),
                description=data.get("description"),
                mission_type=data.get("mission_type", ""),
                start_date=data.get("start_date"),
                end_date=data.get("end_date"),
                auditor_name=data.get("auditor_name"),
                auditor_email=data.get("auditor_email"),
                company=data.get("company"),
                access_url=data.get("access_url"),
                base_url=data.get("base_url"),
                test=data.get("test", ""),
                jwt_token=data.get("jwt_token", ""),
                is_demande=True,
                id_demande = data.get("id_demande", None )
            )
            # Ici vous pourriez déclencher l'envoi d'email
            # launch_mission_email.delay(mission.id)
            if 'fr' in request.data.get('language', 'fr-FR'): 
                prefix_object = "[DEMANDE]"
            else: 
                prefix_object = "[REQUEST]"
            print('urls', os.environ.get("BACK_HOST_URL", ""))
            task = service_demand(
                    prefix_object + " "+data.get("title"),
                    data.get("title"),
                    data.get("description"),
                    data.get("auditor_email"),
                    data.get("auditor_name"), 
                    data.get("company"), 
                    data.get("access_url"),
                    data.get("test"), 
                    data.get("start_date", ''),
                    data.get("end_date", ''), 
                    None,
                    data.get("language", 'fr-FR'),
            ) 
            # Sauvegarder l'ID de la tâche 
            return Response(
                {
                    "message": "Mission d'audit créée avec succès",
                    "status": "success",
                    "code": 201,
                    "mission_id": instance.id
                },
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            return Response(
                {
                    "message": "Erreur lors de la création de la mission " + str(e),
                    "status": "error"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

# Vue API
class sendMailAuthCodeView(APIView):
    permission_classes = [AllowAny]

    @extend_schema( 
        description=" ",
        summary="Créer une exigence",
        tags=["Missions d'Audit"],
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
            custom_ins = Task.objects.all().filter(jwt_token=jwt_token, is_demande=True).first()
            if custom_ins == None:
                return  Response({
                    "message": "Token not found",
                    "status": "error", 
                    "code": status.HTTP_404_NOT_FOUND,
                },
                status=status.HTTP_404_NOT_FOUND
            ) 
            custom_ins.access_code=verification_code
            custom_ins.expires_code_at=expires_at
            custom_ins.save()
             
             # Sauvegarder le code d'authentification dans la base de données
            
            if 'fr' in custom_ins.language:
                path = "user-management/2fa_auth/2FA-auth-fr.html"
                object = "Code d'authentification" + " " + get_formatted_date(custom_ins.lang)
            elif  'en' in  custom_ins.language :
                path = "user-management/2fa_auth/2FA-auth-en.html"
                object = "Authentication code" + " " +  get_formatted_date(custom_ins.lang)

            else:
                path = "user-management/2fa_auth/2FA-auth-fr.html"
                object = "Code d'authentification" + " "  +get_formatted_date(custom_ins.lang)

            path_txt = "user-management/2fa_auth/2FA-auth.txt"
            
            context = {  
                "user_name": '',
                "code_auth": verification_code,
                "company": custom_ins.company,
                "name" : custom_ins.dest_name,
                "back_url" :  os.getenv("BACK_HOST_URL", "")
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
        tags=["Missions d'Audit"],
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
                auth_code_instance = Task.objects.get(jwt_token=jwt_token, access_code=data['code'])
            except Task.DoesNotExist:
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
            
            # Suppression du code d'authentification après utilisation
            # auth_code_instance.delete() 
            return Response(
                {
                   
                    "id_demande": auth_code_instance.is_demande, 
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
