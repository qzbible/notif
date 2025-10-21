import os
import random
from board.models import InstanceBoard, CommitteeBoard
from board.serializers import ArbitrageCreatedSerializer, CommitteeBoardUpdateSerializer, CommitteeCreatedSerializer, DecisionSerializer, MeetingReminderSerializer
from board.service import mail_arbitrage_created_service, mail_committee_created_service, mail_decision_service, mail_meeting_reminder_service
from board.utils import calculate_next_occurrences, compare_with_now
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
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, inline_serializer
import shutil

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from drf_spectacular.types import OpenApiTypes
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view
from django.template.loader import render_to_string

from celery import current_app

from django.utils import timezone

from service.utils import get_formatted_date, get_lang_request, send_mail_created
from rest_framework import serializers


class DecisionView(APIView):
    """API pour envoyer les décisions du comité par email"""
    
    permission_classes = [AllowAny]
    parser_classes = [JSONParser]

    @extend_schema(
        request=DecisionSerializer,
        responses={
            200: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            500: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                'Exemple de requête valide',
                value={
                    'dest_email': 'client@example.com',
                    'name': 'Ghislain',
                    'committee_name': 'CSE Novembre 2025',
                    'committee_date': '15 novembre 2025',
                    'decisions_list': [
                        'Approbation du budget 2025',
                        'Validation du plan de formation',
                        'Mise en place du télétravail'
                    ],
                    'url_connect': 'https://app.example.com/connect',
                    'instance_name': 'Comité Stratégique des Risques',
                    'instance_description': 'Ce comité a pour objectif d\'examiner les risques critiques...',
                    'company': 'Klivar',
                    'date_debut': '07-07-2025',
                    'date_fin': '25-07-2025',
                    'lieu_reunion': 'Immeuble A Biyemassi',
                    'participants': 'Nguessong Suzy, Ambasa Bienvenue, Nodem Borel',
                    'base_url': 'https://api.example.com/',
                    'client_id': 'client_12345',
                    'lang': 'fr-FR'
                },
                request_only=True,
            ),
            OpenApiExample(
                'Réponse de succès',
                value={
                    'message': 'Email envoyé avec succès',
                    'status': 'success',
                    'code': 200,
                    'data': {
                        'dest_email': 'client@example.com',
                        'committee_name': 'CSE Novembre 2025',
                        'sent_at': '2025-10-15T15:30:00Z'
                    }
                },
                response_only=True,
                status_codes=['200'],
            ),
            OpenApiExample(
                'Réponse d\'erreur - Validation',
                value={
                    'message': 'Erreur de validation des données',
                    'status': 'error',
                    'code': 400,
                    'errors': {
                        'dest_email': ['Ce champ est requis.'],
                        'decisions_list': ['La liste des décisions ne peut pas être vide']
                    }
                },
                response_only=True,
                status_codes=['400'],
            ),
        ],
        description="Envoie un email contenant les décisions du comité aux participants",
        summary="Envoi des décisions du comité",
        tags=["Board"],
    )
    def post(self, request):
        """
        Envoie un email avec les décisions du comité
        """
        try:
            # Validation des données avec le serializer
            serializer = DecisionSerializer(data=request.data)
            
            if not serializer.is_valid():
                return Response(
                    {
                        "message": "Erreur de validation des données",
                        "status": "error",
                        "code": status.HTTP_400_BAD_REQUEST,
                        "errors": serializer.errors
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Récupération des données validées
            validated_data = serializer.validated_data
            
            # Récupération du token Bearer (optionnel)
            auth_header = request.headers.get('Authorization')
            token = ""
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header[7:]
            
            # Construction de l'URL de connexion avec token si nécessaire
            url_connect = validated_data.get('url_connect', '')
            if token and url_connect:
                url_connect = f"{url_connect}?token={token}"
            
            # Envoi de l'email via le service
            result = mail_decision_service(
                name=validated_data.get('name'),
                committee_name=validated_data.get('committee_name'),
                committee_date=validated_data.get('committee_date'),
                decisions_list=validated_data.get('decisions_list'),
                dest_email=validated_data.get('dest_email'),
                url_connect=url_connect,
                instance_name=validated_data.get('instance_name'),
                instance_description=validated_data.get('instance_description', ''),
                company=validated_data.get('company'),
                date_debut=validated_data.get('date_debut'),
                date_fin=validated_data.get('date_fin'),
                lieu_reunion=validated_data.get('lieu_reunion', ''),
                participants=validated_data.get('participants', ''),
                back_host= os.environ.get("BACK_HOST_URL", ""),
                lang=validated_data.get('lang', 'fr-FR')
            ) 
            if result:
                response_data = {
                    "message": "Email envoyé avec succès",
                    "status": "success",
                    "code": status.HTTP_200_OK,
                    "data": {
                        "dest_email": validated_data.get('dest_email'),
                        "committee_name": validated_data.get('committee_name'),
                        "sent_at": timezone.now().isoformat()
                    }
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {
                        "message": "Erreur lors de l'envoi de l'email",
                        "status": "error",
                        "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            return Response(
                {
                    "message": "Erreur lors du traitement de la requête",
                    "status": "error",
                    "error": str(e),
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class MeetingReminderView(APIView):
    """API pour envoyer un rappel de réunion du comité par email"""
    
    permission_classes = [AllowAny]

    @extend_schema(
    request=CommitteeBoardUpdateSerializer,
    responses={
        200: OpenApiTypes.OBJECT,
        400: OpenApiTypes.OBJECT,
        404: OpenApiTypes.OBJECT,
        500: OpenApiTypes.OBJECT,
    },
    examples=[
        OpenApiExample(
            'Exemple de requête valide',
            value={
                "instance_id": 45,
                "old_date": "2025-10-20T14:00:00Z",
                "new_date": "2025-11-20T14:00:00Z",
                "perimeter":[
                    {
                        "id": 607,
                        "label": "Data Breach Risk",
                        "value": "Data Breach Risk",
                        "type_value": "risk",
                        "priority": 2
                    },
                ]
            },
            request_only=True,
        ),
        OpenApiExample(
            'Réponse de succès',
            value={
                'message': 'Réunion reprogrammée avec succès',
                'status': 'success',
                'code': 200,
                'data': {
                    'instance_id': 45,
                    'old_date': '2025-10-20T14:00:00Z',
                    'new_date': '2025-11-20T14:00:00Z',
                    'old_task_id': 'abc123-def456-ghi789',
                    'new_task_id': 'xyz789-uvw456-rst123',
                    'committee_title': 'Comité de Direction'
                }
            },
            response_only=True,
            status_codes=['200'],
        ),
        OpenApiExample(
            'Réponse d\'erreur - Dates identiques',
            value={
                'message': 'Erreur de validation des données',
                'status': 'error',
                'code': 400,
                'errors': {
                    'non_field_errors': ['La nouvelle date doit être différente de l\'ancienne date']
                }
            },
            response_only=True,
            status_codes=['400'],
        ),
        OpenApiExample(
            'Réponse d\'erreur - Date dans le passé',
            value={
                'message': 'Erreur de validation des données',
                'status': 'error',
                'code': 400,
                'errors': {
                    'new_date': ['La nouvelle date doit être dans le futur']
                }
            },
            response_only=True,
            status_codes=['400'],
        ),
        OpenApiExample(
            'Réponse d\'erreur - Réunion non trouvée',
            value={
                'message': 'Réunion non trouvée',
                'status': 'error',
                'code': 404
            },
            response_only=True,
            status_codes=['404'],
        ),
    ],
    description="Modifie la date d'une réunion de comité et reprogramme la tâche de rappel",
    summary="Reprogrammation d'une réunion de comité",
    tags=["Board"],
)
    def patch(self, request):
        """
        Modifie la date d'une réunion et reprogramme la tâche Celery associée
        """
        try:
            # Validation des données
            instance_id = request.data.get('instance_id')
            new_date = request.data.get('new_date')
            old_date = request.data.get('old_date')
            perimeter = request.data.get('perimeter', [])
            
            
            if not instance_id:
                return Response(
                    {
                        "message": "Le champ committee_board_id est requis",
                        "status": "error",
                        "code": status.HTTP_400_BAD_REQUEST
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not new_date:
                return Response(
                    {
                        "message": "Le champ new_date est requis",
                        "status": "error",
                        "code": status.HTTP_400_BAD_REQUEST
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not old_date:
                return Response(
                    {
                        "message": "Le champ old_date est requis",
                        "status": "error",
                        "code": status.HTTP_400_BAD_REQUEST
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Conversion de la date
            try:
                from dateutil import parser
                new_date_parsed = parser.parse(new_date)
                old_date_parsed = parser.parse(old_date)
            except Exception as e:
                return Response(
                    {
                        "message": "Format de date invalide",
                        "status": "error",
                        "error": str(e),
                        "code": status.HTTP_400_BAD_REQUEST
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Vérifier si la date est dans le futur
            is_past, readable = compare_with_now(new_date_parsed, 'fr')
            if is_past:
                return Response(
                    {
                        "message": "La nouvelle date doit être dans le futur",
                        "status": "error",
                        "code": status.HTTP_400_BAD_REQUEST,
                        "details": f"La date fournie est {readable}"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Récupération du CommitteeBoard
            try: 
                committee_meeting = CommitteeBoard.objects.get(instance_board__id=instance_id, date=old_date_parsed)
            except CommitteeBoard.DoesNotExist:
                return Response(
                    {
                        "message": "Réunion non trouvée",
                        "status": "error",
                        "code": status.HTTP_404_NOT_FOUND
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Sauvegarde de l'ancienne date et id_task
            old_date = committee_meeting.date
            old_task_id = committee_meeting.id_task
            
            # Récupération de l'instance board
            instance_board = committee_meeting.instance_board
            validated_data = {
                'title': instance_board.title,
                'description': instance_board.description,
                'link': instance_board.link,
                'url_connect': instance_board.url_connect,
                'client': instance_board.client,
                'recurrence_config': instance_board.recurrence_config,
                'ponctuel_config': instance_board.ponctuel_config,
                'actors': instance_board.actors,
                'perimeter': perimeter,
                'lang': instance_board.lang
            }
            
            company_object = validated_data.get('client')
            
            # Annulation de l'ancienne tâche
            try:
                current_app.control.revoke(old_task_id, terminate=True)
                print(f"Ancienne tâche {old_task_id} annulée avec succès")
            except Exception as e:
                print(f"Impossible d'annuler la tâche {old_task_id}: {str(e)}")
            
            # Création de la nouvelle tâche avec la nouvelle date
            new_task = mail_meeting_reminder_service.apply_async(
                args=[
                    validated_data.get('title', ''),
                    validated_data.get('description', ''),
                    validated_data.get('link', ''),
                    validated_data.get('url_connect', ''),
                    company_object["denomination"] if company_object else "",
                    os.environ.get("BACK_HOST_URL", ""),
                    validated_data.get("recurrence_config", {}),
                    validated_data.get("ponctuel_config", {}),
                    validated_data.get('actors', []),
                    validated_data.get('perimeter', []),
                    new_date_parsed,
                    validated_data.get('lang', 'fr-FR')
                ],
                eta=new_date_parsed
            )
            
            # Mise à jour du CommitteeBoard avec la nouvelle tâche et la nouvelle date
            committee_meeting.id_task = new_task.id
            committee_meeting.date = new_date_parsed
            committee_meeting.save()
            
            response_data = {
                "message": "Réunion reprogrammée avec succès",
                "status": "success",
                "code": status.HTTP_200_OK,
                "data": {
                    "instant_board": instance_id,
                    "old_date": old_date.isoformat() if old_date else None,
                    "new_date": new_date_parsed.isoformat(),
                    "old_task_id": old_task_id,
                    "new_task_id": new_task.id,
                    "committee_title": instance_board.title,
                    "instance_id": instance_board.id_instance
                }
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response(
                {
                    "message": "Erreur lors de la reprogrammation de la réunion",
                    "status": "error",
                    "error": str(e),
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        request=MeetingReminderSerializer,
        responses={
            200: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT,
            500: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                'Exemple de requête valide',
                value={
                    'dest_email': 'ghislain@example.com',
                    'name': 'Ghislain',
                    'committee_name': 'CSE Novembre 2025',
                    'date_reunion': '15 octobre 2025',
                    'heure_reunion': '14:00',
                    'lieu_reunion': 'Salle physique ou lien de visioconférence',
                    'participants': 'Nguessong Suzy, Ambasa Bienvenue, Nodem Borel',
                    'instance_name': 'Comité Stratégique des Risques',
                    'instance_description': 'Ce comité a pour objectif d\'examiner les risques critiques...',
                    'date_debut': '07-07-2025, 13:00',
                    'date_fin': '25-07-2025, 18:00',
                    'url_connect': 'https://app.example.com/meeting/start',
                    'company': 'Klivar',
                    'base_url': 'https://api.example.com/',
                    'client_id': 'client_12345',
                    'lang': 'fr-FR'
                },
                request_only=True,
            ),
            OpenApiExample(
                'Réponse de succès',
                value={
                    'message': 'Rappel de réunion envoyé avec succès',
                    'status': 'success',
                    'code': 200,
                    'data': {
                        'dest_email': 'ghislain@example.com',
                        'committee_name': 'CSE Novembre 2025',
                        'sent_at': '2025-10-15T15:30:00Z'
                    }
                },
                response_only=True,
                status_codes=['200'],
            ),
            OpenApiExample(
                'Réponse d\'erreur - Validation',
                value={
                    'message': 'Erreur de validation des données',
                    'status': 'error',
                    'code': 400,
                    'errors': {
                        'dest_email': ['Ce champ est requis.'],
                        'committee_name': ['Ce champ est requis.']
                    }
                },
                response_only=True,
                status_codes=['400'],
            ),
        ],
        description="Envoie un rappel par email pour une réunion du comité qui se tient aujourd'hui",
        summary="Rappel de réunion du comité",
        tags=["Board"],
    )
    def post(self, request):
        """
        Envoie un rappel de réunion par email
        """
        try:
            # Validation des données avec le serializer
            serializer = MeetingReminderSerializer(data=request.data)
            
            if not serializer.is_valid():
                return Response(
                    {
                        "message": "Erreur de validation des données",
                        "status": "error",
                        "code": status.HTTP_400_BAD_REQUEST,
                        "errors": serializer.errors
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Récupération des données validées
            validated_data = serializer.validated_data
            
            # Récupération du token Bearer (optionnel)
            auth_header = request.headers.get('Authorization')
            token = ""
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header[7:]
            
            # Construction de l'URL de session avec token si nécessaire
            url_connect = validated_data.get('url_connect', '')
            if token and url_connect:
                url_connect = f"{url_connect}?token={token}"
            
            # Envoi de l'email via le service
            result = mail_meeting_reminder_service(
                name=validated_data.get('name'),
                committee_name=validated_data.get('committee_name'),
                date_reunion=validated_data.get('date_reunion'),
                heure_reunion=validated_data.get('heure_reunion'),
                lieu_reunion=validated_data.get('lieu_reunion', ''),
                participants=validated_data.get('participants', ''),
                dest_email=validated_data.get('dest_email'),
                url_connect=url_connect,
                instance_name=validated_data.get('instance_name'),
                instance_description=validated_data.get('instance_description', ''),
                date_debut=validated_data.get('date_debut'),
                date_fin=validated_data.get('date_fin'),
                company=validated_data.get('company'),
                back_host=os.environ.get("BACK_HOST_URL", ""),
                lang=validated_data.get('lang', 'fr-FR')
            )
            
            if result:
                response_data = {
                    "message": "Rappel de réunion envoyé avec succès",
                    "status": "success",
                    "code": status.HTTP_200_OK,
                    "data": {
                        "dest_email": validated_data.get('dest_email'),
                        "committee_name": validated_data.get('committee_name'),
                        "sent_at": timezone.now().isoformat()
                    }
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {
                        "message": "Erreur lors de l'envoi de l'email",
                        "status": "error",
                        "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            return Response(
                {
                    "message": "Erreur lors du traitement de la requête",
                    "status": "error",
                    "error": str(e),
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CommitteeCreatedView(APIView):
    """API pour envoyer une notification de création de comité d'instance"""
    
    permission_classes = [AllowAny]


    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='id_instance',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,  # Reste en QUERY
                description='ID de l\'instance à supprimer',
                required=True
            )
        ],
        responses={
            200: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
            500: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                'Réponse de succès',
                value={
                    'message': 'Comité supprimé avec succès',
                    'status': 'success',
                    'code': 200,
                    'data': {
                        'id_instance': 100,
                        'title': 'Comité de Direction',
                        'deleted_at': '2025-10-20T14:30:00Z',
                        'cancelled_tasks': 5
                    }
                },
                response_only=True,
                status_codes=['200'],
            ),
            OpenApiExample(
                'Réponse d\'erreur - Paramètre manquant',
                value={
                    'message': 'Le paramètre id_instance est requis',
                    'status': 'error',
                    'code': 400
                },
                response_only=True,
                status_codes=['400'],
            ),
            OpenApiExample(
                'Réponse d\'erreur - Non trouvé',
                value={
                    'message': 'Comité non trouvé',
                    'status': 'error',
                    'code': 404
                },
                response_only=True,
                status_codes=['404'],
            ),
        ],
        description="Supprime un comité d'instance et annule toutes les tâches programmées associées",
        summary="Suppression d'un comité",
        tags=["Board"],
    )
    def delete(self, request):
        """
        Supprime un comité d'instance et annule toutes les tâches de rappel programmées
        """
       
        try:
            # Récupération de l'instance
             # Récupération de l'id_instance depuis les query params
            id_instance = request.query_params.get('id_instance')
            
            if not id_instance:
                return Response(
                    {
                        "message": "Le paramètre id_instance est requis",
                        "status": "error",
                        "code": status.HTTP_400_BAD_REQUEST
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            try:
                instance = InstanceBoard.objects.get(id_instance=id_instance)
            except InstanceBoard.DoesNotExist:
                return Response(
                    {
                        "message": "Comité non trouvé",
                        "status": "error",
                        "code": status.HTTP_404_NOT_FOUND
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Récupération des informations avant suppression
            instance_title = instance.title 
            # Récupération et annulation de toutes les tâches planifiées
            committee_meetings = CommitteeBoard.objects.filter(instance_board=instance)
            cancelled_tasks_count = 0
            
            for meeting in committee_meetings:
                try:
                    # Annulation de la tâche Celery
                    current_app.control.revoke(meeting.id_task, terminate=True)
                    cancelled_tasks_count += 1
                    print(f"Tâche {meeting.id_task} annulée avec succès")
                except Exception as e:
                    print(f"Impossible d'annuler la tâche {meeting.id_task}: {str(e)}")
            
            # Suppression des réunions programmées
            committee_meetings.delete()
            
            # Suppression de l'instance
            instance.delete()
            
            response_data = {
                "message": "Comité supprimé avec succès",
                "status": "success",
                "code": status.HTTP_200_OK,
                "data": {
                    "id_instance": id_instance,
                    "title": instance_title,
                    "cancelled_tasks": cancelled_tasks_count,
                    "deleted_at": datetime.now().isoformat()
                }
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response(
                {
                    "message": "Erreur lors de la suppression du comité",
                    "status": "error",
                    "error": str(e),
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    
    @extend_schema(
        request=CommitteeCreatedSerializer,
        responses={
            200: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT,
            500: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                'Exemple de requête valide',
                value={
                        "id_instance": 100,
                        "title": "Comité de Direction",
                        "description": "Réunion hebdomadaire du comité exécutif pour le suivi des projets stratégiques.",
                        "url_connect": "https://plateforme.exemple.com/comite/connexion",
                        "type": "executif",
                        "format": "visioconférence",
                        "link": "https://plateforme.exemple.com/comite/INST-001",
                        "lang": "fr-FR",
                        "client": {
                            "id": "CLI-2025",
                            "denomination": "Entreprise ABC",
                            "secteur": "Finance"
                        },
                        "recurrence_config":  {
                            "start_date": "2025-10-16T13:28:06.092Z",
                            "interval": 1,
                            "unit": "days",
                            "recurrence_config": {},
                            "end_type": "never",
                            "end_date": None,
                            "occurrence_count": None
                        },
                        "ponctuel_config": {
                            "date": "2025-10-17T08:45:18.687Z",
                            "priority": 0
                        },
                        "actors": [
                            {
                            "first_name": " Dupont",
                            "last_name": "Jean ",
                            "email": "jean.dupont@exemple.com",
                            "role": "Président"
                            } 
                        ],
                        "perimeter": [
                             
                        ]
                        },
                request_only=True,
            ),
            OpenApiExample(
                'Réponse de succès',
                value={
                    'message': 'Email de création de comité envoyé avec succès',
                    'status': 'success',
                    'code': 200,
                    'data': {
                        'dest_email': 'ghislain@example.com',
                        'committee_name': 'Comité Stratégique des Risques',
                        'sent_at': '2025-10-15T15:30:00Z'
                    }
                },
                response_only=True,
                status_codes=['200'],
            ),
            OpenApiExample(
                'Réponse d\'erreur - Validation',
                value={
                    'message': 'Erreur de validation des données',
                    'status': 'error',
                    'code': 400,
                    'errors': {
                        'dest_email': ['Ce champ est requis.'],
                        'committee_name': ['Ce champ est requis.']
                    }
                },
                response_only=True,
                status_codes=['400'],
            ),
        ],
        description="Envoie un email de notification lorsqu'un nouveau comité d'instance est créé",
        summary="Notification de création de comité",
        tags=["Board"],
    )
    def post(self, request):
        """
        Envoie un email de notification de création de comité
        """
        try:
            # InstanceBoard.objects.all().delete()
            # CommitteeBoard.objects.all().delete()
            # Validation des données avec le serializer
            serializer = CommitteeCreatedSerializer(data=request.data)
            
            if not serializer.is_valid():
                return Response(
                    {
                        "message": "Erreur de validation des données",
                        "status": "error",
                        "code": status.HTTP_400_BAD_REQUEST,
                        "errors": serializer.errors
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Récupération des données validées
            validated_data = serializer.validated_data
            
            # Récupération du token Bearer (optionnel)
            auth_header = request.headers.get('Authorization')
            token = ""
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header[7:]
            
            # Construction de l'URL de connexion avec token si nécessaire
            url_connect = validated_data.get('url_connect', '')
            if token and url_connect:
                url_connect = f"{url_connect}?token={token}"
            
            ins_created, created = InstanceBoard.objects.get_or_create(
                id_instance=validated_data.get('id_instance'),
                defaults={
                    'title': validated_data.get('title'),
                    'description': validated_data.get('description'),
                    'url_connect': validated_data.get('url_connect'),
                    'type': validated_data.get('type'),
                    'format': validated_data.get('format'),
                    'link': validated_data.get('link'),
                    'lang': validated_data.get('lang'),
                    'client': validated_data.get('client'),
                    'recurrence_config': validated_data.get('recurrence_config', None),
                    'ponctuel_config': validated_data.get('ponctuel_config', None),
                    'perimeter': validated_data.get('perimeter', []),
                    'actors': validated_data.get('actors',[] )
                }
            )
            company_object = validated_data.get('client')
            # Envoi de l'email via le service
             
            result = mail_committee_created_service( 
                title=validated_data.get('title', ''),
                description=validated_data.get('description', ''),
                link=validated_data.get('link', ''),
                actors=validated_data.get('actors',[] ), 
                
                url_connect= validated_data.get('url_connect','' ),
                company = company_object["denomination"] if validated_data.get('client') else "",
                back_host=os.environ.get("BACK_HOST_URL", ""),
                lang=validated_data.get('lang', 'fr-FR'),
                periodicity=validated_data.get("recurrence_config", {}),
                ponctuel_config = validated_data.get("ponctuel_config", {}),
                created=created

            )
            # creation des elements a arbitrer ....
            
            
            
            dates = []
            if validated_data.get('recurrence_config', None) :
                 # on recupere les 5 prochaine date 
                dates = calculate_next_occurrences(validated_data.get('recurrence_config', None), count=5)
            elif validated_data.get('ponctuel_config', None):
                dates.append(validated_data.get('ponctuel_config', None).get('date'))
            if created:
                for date in dates:
                    # print(date)
                   
                    is_past, readable = compare_with_now(date, 'fr' if validated_data.get('lang', 'fr-FR') == 'fr-FR' else 'en') #False (la date est dans le futur),  "dans 364 jours" (ou selon la date actuelle)
                    # if is_past:
                        
                    #     continue 
                    print(date)
                    task = mail_meeting_reminder_service.apply_async(
                        args=[
                            validated_data.get('title', ''),
                            validated_data.get('description', ''),
                            validated_data.get('link', ''),
                            validated_data.get('url_connect','' ),
                            company_object["denomination"] if validated_data.get('client') else "",
                            os.environ.get("BACK_HOST_URL", ""),
                            validated_data.get("recurrence_config", {}),
                            validated_data.get("ponctuel_config", {}),
                            validated_data.get('actors',[] ),
                            validated_data.get('perimeter', []),
                            date,
                            validated_data.get('lang', 'fr-FR')
                        ],
                        eta=date
                    ) 
                    ins_meet, _ = CommitteeBoard.objects.get_or_create(
                            id_task = task,
                            defaults={
                                    "instance_board": ins_created,
                                    "date":date,
                                    }
                    )
                    # send element a arbitrer

             
            else :
                ins_meet = CommitteeBoard.objects.filter(instance_board=ins_created)
                for task in ins_meet:
                    try:
                        current_app.control.revoke(task.id_task, terminate=True)
                        print(f"Tâche {task.id_task} annulée avec succès")
                    except Exception as e:
                        print(f"Impossible d'annuler la tâche {task.id_task}: {str(e)}")
                # supprimer les élément programmer et reprogrammer
                ins_meet.delete()
                for date in dates:
                    is_past, readable = compare_with_now(date,  'fr' if validated_data.get('lang', 'fr-FR') == 'fr-FR' else 'en') #False (la date est dans le futur),  "dans 364 jours" (ou selon la date actuelle)
                    # if is_past:
                    #     continue 
                    print(date)
                    task = mail_meeting_reminder_service.apply_async(
                        args=[
                            validated_data.get('title', ''),
                            validated_data.get('description', ''),
                            validated_data.get('link', ''),
                            validated_data.get('url_connect','' ),
                            company_object["denomination"] if validated_data.get('client') else "",
                            os.environ.get("BACK_HOST_URL", ""),
                            validated_data.get("recurrence_config", {}),
                            validated_data.get("ponctuel_config", {}),
                            validated_data.get('actors',[] ),
                            validated_data.get('perimeter', []),
                            date,
                            validated_data.get('lang', 'fr-FR')
                        ],
                        eta=date
                    ) 
                    ins_meet, _ = CommitteeBoard.objects.get_or_create(
                            id_task = task,
                            defaults={
                                    "instance_board": ins_created,
                                    "date":date, 
                                    }
                    )

            if result:
                response_data = {
                    "message": "Email de création de comité envoyé avec succès",
                    "status": "success",
                    "code": status.HTTP_200_OK, 
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {
                        "message": "Erreur lors de l'envoi de l'email",
                        "status": "error",
                        "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            return Response(
                {
                    "message": "Erreur lors du traitement de la requête",
                    "status": "error",
                    "error": str(e),
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        


class ArbitrageCreatedView(APIView):
    """API pour envoyer une notification de création de dossier d'arbitrage"""
    
    permission_classes = [AllowAny]

    @extend_schema(
        request=ArbitrageCreatedSerializer,
        responses={
            200: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT,
            500: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                'Exemple de requête valide',
                value={
                    'dest_email': 'ghislain@example.com',
                    'name': 'Ghislain',
                    'committee_name': 'CSE Novembre 2025',
                    'committee_date': '25 novembre 2025',
                    'nomber_elements': 12,
                    'type_arbitration_elements': 'Risques, Exigences, Incidents, etc.',
                    'priorite_arbitrage': 'Haute / Moyenne / Basse',
                    'instance_name': 'Comité Stratégique des Risques',
                    'instance_description': 'Ce comité a pour objectif d\'examiner les risques critiques identifiés au sein de l\'organisation...',
                    'instance_start_date': '07 juillet 2025, 13:00',
                    'instance_end_date': '25 juillet 2025, 18:00',
                    'instance_location': 'Immeuble A Biyemassi',
                    'instance_participants': 'Nguessong Suzy, Ambasa Bienvenue, Nodem Borel',
                    'url_connect': 'https://app.example.com/arbitrage/connect',
                    'company': 'Klivar',
                    'base_url': 'https://api.example.com/',
                    'client_id': 'client_12345',
                    'lang': 'fr-FR'
                },
                request_only=True,
            ),
            OpenApiExample(
                'Réponse de succès',
                value={
                    'message': 'Email de création de dossier d\'arbitrage envoyé avec succès',
                    'status': 'success',
                    'code': 200,
                    'data': {
                        'dest_email': 'ghislain@example.com',
                        'committee_name': 'CSE Novembre 2025',
                        'nomber_elements': 12,
                        'sent_at': '2025-10-15T15:30:00Z'
                    }
                },
                response_only=True,
                status_codes=['200'],
            ),
            OpenApiExample(
                'Réponse d\'erreur - Validation',
                value={
                    'message': 'Erreur de validation des données',
                    'status': 'error',
                    'code': 400,
                    'errors': {
                        'dest_email': ['Ce champ est requis.'],
                        'nomber_elements': ['Le nombre d\'éléments doit être supérieur à 0']
                    }
                },
                response_only=True,
                status_codes=['400'],
            ),
        ],
        description="Envoie un email de notification lorsqu'un nouveau dossier d'arbitrage est créé",
        summary="Notification de création de dossier d'arbitrage",
        tags=["Board"],
    )
    def post(self, request):
        """
        Envoie un email de notification de création de dossier d'arbitrage
        """
        try:
            # Validation des données avec le serializer
            serializer = ArbitrageCreatedSerializer(data=request.data)
            
            if not serializer.is_valid():
                return Response(
                    {
                        "message": "Erreur de validation des données",
                        "status": "error",
                        "code": status.HTTP_400_BAD_REQUEST,
                        "errors": serializer.errors
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Récupération des données validées
            validated_data = serializer.validated_data
            
            # Récupération du token Bearer (optionnel)
            auth_header = request.headers.get('Authorization')
            token = ""
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header[7:]
            
            # Construction de l'URL de connexion avec token si nécessaire
            url_connect = validated_data.get('url_connect', '')
            if token and url_connect:
                url_connect = f"{url_connect}?token={token}"
            
            # Envoi de l'email via le service
            result = mail_arbitrage_created_service(
                name=validated_data.get('name'),
                committee_name=validated_data.get('committee_name'),
                committee_date=validated_data.get('committee_date'),
                nomber_elements=validated_data.get('nomber_elements'),
                type_arbitration_elements=validated_data.get('type_arbitration_elements'),
                priorite_arbitrage=validated_data.get('priorite_arbitrage'),
                instance_name=validated_data.get('instance_name'),
                instance_description=validated_data.get('instance_description', ''),
                instance_start_date=validated_data.get('instance_start_date'),
                instance_end_date=validated_data.get('instance_end_date'),
                instance_location=validated_data.get('instance_location', ''),
                instance_participants=validated_data.get('instance_participants', ''),
                dest_email=validated_data.get('dest_email'),
                url_connect=url_connect,
                company=validated_data.get('company'),
                back_host=os.environ.get("BACK_HOST_URL", ""),
                lang=validated_data.get('lang', 'fr-FR')
            )
            
            if result:
                response_data = {
                    "message": "Email de création de dossier d'arbitrage envoyé avec succès",
                    "status": "success",
                    "code": status.HTTP_200_OK,
                    "data": {
                        "dest_email": validated_data.get('dest_email'),
                        "committee_name": validated_data.get('committee_name'),
                        "nomber_elements": validated_data.get('nomber_elements'),
                        "sent_at": timezone.now().isoformat()
                    }
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {
                        "message": "Erreur lors de l'envoi de l'email",
                        "status": "error",
                        "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            return Response(
                {
                    "message": "Erreur lors du traitement de la requête",
                    "status": "error",
                    "error": str(e),
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )