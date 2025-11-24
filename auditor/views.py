from django.shortcuts import render

# Create your views here.
from auditor.models import MissionAudit
from auditor.serializers import  MissionAuditSerializer
from auditor.service import service_mission
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework import serializers

from rest_framework.permissions import AllowAny

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
                    'auditor_name': 'Jean Martin',
                    'auditor_email': 'jean.martin@klivar.com', 
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

            instance = MissionAudit.objects.create(
                title=data.get("title"),
                description=data.get("description"),
                mission_type=data.get("mission_type", "COMPLIANCE"),
                start_date=data.get("start_date"),
                end_date=data.get("end_date"),
                auditor_name=data.get("auditor_name"),
                auditor_email=data.get("auditor_email"),
                company=data.get("company"),
                access_url=data.get("access_url"),
                base_url=data.get("base_url"),
            )
            # Ici vous pourriez déclencher l'envoi d'email
            # launch_mission_email.delay(mission.id)
            if 'fr' in request.data.get('language', 'fr-FR'): 
                prefix_object = "[MISSION D'AUDIT]"
            else: 
                prefix_object = "[AUDIT MISSION]"

            task = service_mission.apply_async(
                args=[
                    prefix_object + " "+data.get("title"),
                    data.get("title"),
                    data.get("mission_name"),
                    data.get("description"),
                    data.get("auditor_email"),
                    data.get("mission_type"),
                    data.get("auditor_name"),
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