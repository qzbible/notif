from mailing.serializers import ExigenceSerializer
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
from datetime import datetime

from .utils import *
import shutil
 
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Vue API
class ExigenceResponsableView(APIView):
    permission_classes = [IsAuthenticated]

    # Schémas pour la documentation Swagger
    success_schema = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties=OrderedDict((
            ("message", openapi.Schema(type=openapi.TYPE_STRING,
             example="Votre requête a été traitée avec succès")),
            ("status", openapi.Schema(type=openapi.TYPE_STRING, example="success")),
            ("code", openapi.Schema(type=openapi.TYPE_INTEGER,
             example=status.HTTP_201_CREATED)),
        ))
    )

    request_body_schema = openapi.Schema(
        description="Description du corps de la requête",
        type=openapi.TYPE_OBJECT,
        properties=OrderedDict((
            ("object", openapi.Schema(type=openapi.TYPE_STRING,
             example="Demande de permission")),
            ("user_name", openapi.Schema(type=openapi.TYPE_STRING,
             example="John Doe")),
            ("destinator", openapi.Schema(type=openapi.TYPE_ARRAY, 
                items=openapi.Items(type=openapi.TYPE_STRING),
             example=["email1@example.com", "email2@example.com"])), 
            ("company", openapi.Schema(type=openapi.TYPE_STRING, 
            example="Ziyouma")),
            ("url", openapi.Schema(type=openapi.TYPE_STRING, 
            example="https://example.com")),
        ))
    )

    bad_token_schema = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties=OrderedDict((
            ("message", openapi.Schema(
                type=openapi.TYPE_STRING, example="Token invalide ou expiré")),
            ("Gateway_code", openapi.Schema(type=openapi.TYPE_INTEGER, example=401)),
        ))
    )

    @swagger_auto_schema(
        operation_description="Cette API crée une tâche Celery pour l'envoi d'emails",
        request_body=request_body_schema,
        responses={ 
            status.HTTP_201_CREATED: success_schema,
            status.HTTP_401_UNAUTHORIZED: bad_token_schema,
            status.HTTP_400_BAD_REQUEST: "Erreur de paramètres.",
            status.HTTP_404_NOT_FOUND: 'Ressource non trouvée',
        }
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
        user_name = serializer.validated_data.get("user_name")
        destinator = serializer.validated_data.get("destinator")
        company = serializer.validated_data.get("company")
        url = serializer.validated_data.get("url")
        
        # Création de la tâche Celery
        try:
            # task = send_email_task.delay(
            #     object_text=object_text,
            #     user_name=user_name,
            #     destinator=destinator,
            #     company=company,
            #     url=url
            # )

            return Response(
                {
                    "message": "Tâche d'envoi d'email créée avec succès",
                    "status": "success",
                    "code": status.HTTP_201_CREATED,
                    # "task_id": task.id
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {
                    "message": f"Erreur lors de la création de la tâche: {str(e)}",
                    "status": "error"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        


# Vue API
class ExigenceApprobatorView(APIView):
    permission_classes = [IsAuthenticated]

    # Schémas pour la documentation Swagger
    success_schema = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties=OrderedDict((
            ("message", openapi.Schema(type=openapi.TYPE_STRING,
             example="Votre requête a été traitée avec succès")),
            ("status", openapi.Schema(type=openapi.TYPE_STRING, example="success")),
            ("code", openapi.Schema(type=openapi.TYPE_INTEGER,
             example=status.HTTP_201_CREATED)),
        ))
    )

    request_body_schema = openapi.Schema(
        description="Description du corps de la requête",
        type=openapi.TYPE_OBJECT,
        properties=OrderedDict((
            ("object", openapi.Schema(type=openapi.TYPE_STRING,
             example="Demande de permission")),
            ("user_name", openapi.Schema(type=openapi.TYPE_STRING,
             example="John Doe")),
            ("destinator", openapi.Schema(type=openapi.TYPE_ARRAY, 
                items=openapi.Items(type=openapi.TYPE_STRING),
             example=["email1@example.com", "email2@example.com"])), 
            ("company", openapi.Schema(type=openapi.TYPE_STRING, 
            example="Ziyouma")),
            ("url", openapi.Schema(type=openapi.TYPE_STRING, 
            example="https://example.com")),
        ))
    )

    bad_token_schema = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties=OrderedDict((
            ("message", openapi.Schema(
                type=openapi.TYPE_STRING, example="Token invalide ou expiré")),
            ("Gateway_code", openapi.Schema(type=openapi.TYPE_INTEGER, example=401)),
        ))
    )

    @swagger_auto_schema(
        operation_description="Cette API crée une tâche Celery pour l'envoi d'emails",
        request_body=request_body_schema,
        responses={ 
            status.HTTP_201_CREATED: success_schema,
            status.HTTP_401_UNAUTHORIZED: bad_token_schema,
            status.HTTP_400_BAD_REQUEST: "Erreur de paramètres.",
            status.HTTP_404_NOT_FOUND: 'Ressource non trouvée',
        }
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
        user_name = serializer.validated_data.get("user_name")
        destinator = serializer.validated_data.get("destinator")
        company = serializer.validated_data.get("company")
        url = serializer.validated_data.get("url")
        
        # Création de la tâche Celery
        try:
            # task = send_email_task.delay(
            #     object_text=object_text,
            #     user_name=user_name,
            #     destinator=destinator,
            #     company=company,
            #     url=url
            # )

            return Response(
                {
                    "message": "Tâche d'envoi d'email créée avec succès",
                    "status": "success",
                    "code": status.HTTP_201_CREATED,
                    # "task_id": task.id
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {
                    "message": f"Erreur lors de la création de la tâche: {str(e)}",
                    "status": "error"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# Vue API
class ExigenceInformateurView(APIView):
    permission_classes = [IsAuthenticated]

    # Schémas pour la documentation Swagger
    success_schema = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties=OrderedDict((
            ("message", openapi.Schema(type=openapi.TYPE_STRING,
             example="Votre requête a été traitée avec succès")),
            ("status", openapi.Schema(type=openapi.TYPE_STRING, example="success")),
            ("code", openapi.Schema(type=openapi.TYPE_INTEGER,
             example=status.HTTP_201_CREATED)),
        ))
    )

    request_body_schema = openapi.Schema(
        description="Description du corps de la requête",
        type=openapi.TYPE_OBJECT,
        properties=OrderedDict((
            ("object", openapi.Schema(type=openapi.TYPE_STRING,
             example="Demande de permission")),
            ("user_name", openapi.Schema(type=openapi.TYPE_STRING,
             example="John Doe")),
            ("destinator", openapi.Schema(type=openapi.TYPE_ARRAY, 
                items=openapi.Items(type=openapi.TYPE_STRING),
             example=["email1@example.com", "email2@example.com"])), 
            ("company", openapi.Schema(type=openapi.TYPE_STRING, 
            example="Ziyouma")),
            ("url", openapi.Schema(type=openapi.TYPE_STRING, 
            example="https://example.com")),
        ))
    )

    bad_token_schema = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties=OrderedDict((
            ("message", openapi.Schema(
                type=openapi.TYPE_STRING, example="Token invalide ou expiré")),
            ("Gateway_code", openapi.Schema(type=openapi.TYPE_INTEGER, example=401)),
        ))
    )

    @swagger_auto_schema(
        operation_description="Cette API crée une tâche Celery pour l'envoi d'emails",
        request_body=request_body_schema,
        responses={ 
            status.HTTP_201_CREATED: success_schema,
            status.HTTP_401_UNAUTHORIZED: bad_token_schema,
            status.HTTP_400_BAD_REQUEST: "Erreur de paramètres.",
            status.HTTP_404_NOT_FOUND: 'Ressource non trouvée',
        }
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
        user_name = serializer.validated_data.get("user_name")
        destinator = serializer.validated_data.get("destinator")
        company = serializer.validated_data.get("company")
        url = serializer.validated_data.get("url")
        
        # Création de la tâche Celery
        try:
            # task = send_email_task.delay(
            #     object_text=object_text,
            #     user_name=user_name,
            #     destinator=destinator,
            #     company=company,
            #     url=url
            # )

            return Response(
                {
                    "message": "Tâche d'envoi d'email créée avec succès",
                    "status": "success",
                    "code": status.HTTP_201_CREATED,
                    # "task_id": task.id
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {
                    "message": f"Erreur lors de la création de la tâche: {str(e)}",
                    "status": "error"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
