import os
import random
from board.serializers import DecisionSerializer, MeetingReminderSerializer
from board.service import mail_decision_service
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

from service.utils import get_formatted_date, get_lang_request, send_mail_created


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
            
            print("BACK_HOST_URL",os.environ.get("BACK_HOST_URL", "") )
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
                    'url_session': 'https://app.example.com/meeting/start',
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
            url_session = validated_data.get('url_session', '')
            if token and url_session:
                url_session = f"{url_session}?token={token}"
            
            # Envoi de l'email via le service
            result = mail_meeting_reminder_service(
                name=validated_data.get('name'),
                committee_name=validated_data.get('committee_name'),
                date_reunion=validated_data.get('date_reunion'),
                heure_reunion=validated_data.get('heure_reunion'),
                lieu_reunion=validated_data.get('lieu_reunion', ''),
                participants=validated_data.get('participants', ''),
                dest_email=validated_data.get('dest_email'),
                url_session=url_session,
                instance_name=validated_data.get('instance_name'),
                instance_description=validated_data.get('instance_description', ''),
                date_debut=validated_data.get('date_debut'),
                date_fin=validated_data.get('date_fin'),
                company=validated_data.get('company'),
                back_url=validated_data.get('base_url'),
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