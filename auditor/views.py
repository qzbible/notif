import os
from django.shortcuts import render
import random
# Create your views here.
from auditor.models import ActorFollow, FollowUp, Task
from auditor.serializers import  FollowUpSerializer, MissionAuditSerializer
from auditor.service import service_demand, service_mission, service_test
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
            custom_ins = Task.objects.all().filter(jwt_token=jwt_token).first()
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



class TestCreateView(APIView):
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
                    'date': '2025-02-01T09:00:00Z',
                    "type":{
                        "code": "COMPLIANCE",
                        "label": "Conformité"
                    },
                    'actors': [
                        {
                            "name": "Jean Martin",
                            "email": "samyfabiol@gmail.com"
                        }
                    ],
                    'perimeter': 'Contrôle', 
                    'audit_method': 'Contrôle', 
                    'company': 'Entreprise ABC', 
                    'access_url': 'https://app.klivar.com/audit/123', 
                    'language': 'fr-FR',
                    'jwt_token': 'yrtyrgtryugh ytoton jwt', 
                    "test": "Ceci est un test",
                    "lieu": "Ceci est un test",
                    'id_client': 456,
                    'id_test': 789
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
            type = data.get("type", None)
            actors = data.get("actors", [])
            for act in actors:

                instance = Task.objects.create(
                    title=data.get("title"),
                    description=data.get("description"),
                    type_test=type.get("code", ""),
                    type_test_label=type.get("label", ""),  

                    end_date=data.get("date"),
                    auditor_name=act.get("name"),
                    auditor_email=act.get("email"),

                    scope_test = data.get("perimeter", ""),
                    company=data.get("company"),
                    access_url=data.get("access_url"),
                    base_url=data.get("base_url", None),
                    test=data.get("test", ""),
                    jwt_token=data.get("jwt_token", ""),
                    is_test=True,
                    id_test = data.get("id_test", None ),
                    id_client = data.get("id_client", None),
                    audit_method = data.get("audit_method", ""),
                    lieu = data.get("lieu", "")

                )
                # Ici vous pourriez déclencher l'envoi d'email
                # launch_mission_email.delay(mission.id)
                if 'fr' in request.data.get('language', 'fr-FR'): 
                    prefix_object = "[TEST]"
                else: 
                    prefix_object = "[TEST]"
                print('urls', os.environ.get("BACK_HOST_URL", ""))
                task = service_test(
                        prefix_object + " "+data.get("title"),
                        data.get("title"),
                        data.get("description"),
                        act.get("email"),
                        act.get("name"), 
                        data.get("company"), 
                        data.get("access_url"),
                        data.get("test"), 
                        data.get("perimeter", ''),
                        type.get("code", ""),
                        type.get("label", ""),
                        data.get("lieu", ""), 
                        data.get("audit_method", ""),
                        data.get("date", ''),  
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
        


class FollowUpAuditView(APIView):
    permission_classes = [AllowAny]
    
    @extend_schema( 
        request=FollowUpSerializer(many=True),
        examples=[
             
            OpenApiExample(
                'Exemple de requête valide',
                value=
                    {
                        'unit': 'minutes',
                        'value': 20,
                        'type': 'after',
                        'id_project': 20,
                        'id_action': 20,
                        'id_client': 20, 
                      
                        'deadline': '2025-02-12T22:23:52.900Z',
                        'actors': [
                            {
                                'role': 'Responsable',
                                'id_user': 10,
                                'full_name': 'John Doe',
                                "token" : "jhqguyq_kjsiuq jsiuiqs",
                                'email': 'samyfabiol@gmail.com'
                            }
                        ] 
                    }
                ,
                request_only=True,
            ),
            OpenApiExample(
                'Réponse de succès',
                value={
                    'message': 'Follow Up créée avec succès',
                    'status': 'success',
                    'code': 201,
                    'data': {
                        'total_created': 1,
                        'follow_ups': [
                            {
                                'id_project': 20,
                                'id_action': 20,
                                'scheduled_for': '2025-02-12T22:43:52.900Z'
                            }
                        ]
                    }
                },
                response_only=True,
                status_codes=['201'],
            ),
        ],
        description="Crée une exigence et programme l'envoi de notifications par email",
        summary="Créer une exigence avec follow-up",
        tags=["Exigences"],
    )
    def post(self, request):
        id_project = request.query_params.get('id_project', None)
        id_action = request.query_params.get('id_action', None)
        # Valider toutes les données en une fois
        # 
        if id_project and id_action:
            delete_follow_up(id_project,  id_action)
            
        serializer = FollowUpSerializer(data=request.data, many=True)
        
        if not serializer.is_valid():
            return Response(
                {
                    "message": "Données invalides",
                    "status": "error",
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created_follow_ups = []
        
        for item_data in serializer.validated_data:
            try:
                # Créer ou récupérer le FollowUp
                follow_up_instance, created = FollowUp.objects.get_or_create( 
                    id_project=item_data["id_project"],
                    id_action=item_data["id_action"],
                    id_client=item_data["id_client"],
                    defaults={
                        "unit": item_data["unit"],
                        "value": item_data["value"],
                        "type": item_data["type"],
                        "deadline": item_data["deadline"]
                       
                    }
                )
                
                # Récupérer l'eta_datetime déjà calculé et validé
                eta_datetime = item_data["eta_datetime"]
                
                actors_data = item_data["actors"]
                scheduled_actors = []
                
                for actor_data in actors_data:
                    # Créer ou récupérer l'acteur
                    ins_acto, _ = ActorFollow.objects.get_or_create(
                        follow_up=follow_up_instance,
                        id_user=actor_data["id_user"],
                        defaults={
                            "role": actor_data["role"],
                            "full_name": actor_data["full_name"],
                            "email": actor_data["email"],
                             "jwt_token": actor_data["jwt_token"],
                        }
                    )
                    
                    # Programmer l'envoi du mail avec Celery
                    task_result = follow_up_task.apply_async(
                        args=[
                            item_data["id_project"], 
                            item_data["id_action"],
                            actor_data["role"],
                            item_data["id_client"],
                            actor_data["email"],
                            actor_data["full_name"],
                            os.environ.get("DEPLOYER_SERVICE_NAME", ""),
                            follow_up_instance.pk,
                            actor_data["id_user"],
                            actor_data["jwt_token"]
                        ],
                        eta=eta_datetime
                    )
                    
                    # Sauvegarder le task_id pour pouvoir révoquer si besoin
                    ins_acto.task_id = task_result.id
                    ins_acto.save()
                    
                    scheduled_actors.append({
                        "email": actor_data["email"],
                        "task_id": task_result.id
                    })
                
                created_follow_ups.append({
                    "id_project": item_data["id_project"],
                    "id_action": item_data["id_action"],
                    "scheduled_for": eta_datetime.isoformat(),
                    "actors": scheduled_actors
                })
                
            except Exception as e:
                # Si une erreur survient, annuler toutes les tâches déjà créées
                for follow_up_data in created_follow_ups:
                    for actor in follow_up_data.get("actors", []):
                        if actor.get("task_id"): 
                            current_app.control.revoke(actor["task_id"], terminate=True)
                
                return Response(
                    {
                        "message": "Une erreur est survenue lors du traitement",
                        "status": "error",
                        "error": str(e),
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(
            {
                "message": "Follow Up créée avec succès",
                "status": "success",
                "code": 201,
                "data": {
                    "total_created": len(created_follow_ups),
                    "follow_ups": created_follow_ups
                }
            },
            status=status.HTTP_201_CREATED
        )
    

def delete_follow_up(id_project,  id_action  ):
    inst_filter = FollowUp.objects.filter(
        id_project=id_project,
        id_action=id_action
    )
    for inst in inst_filter:
        actors = ActorFollow.objects.filter(follow_up=inst)
        for actor in actors:
            try:
                current_app.control.revoke(actor.task_id, terminate=True)
              
            except Exception as e:
                print(f"Impossible d'annuler la tâche {actor.task_id}: {str(e)}")
            actor.delete()
        inst.delete()
    return True