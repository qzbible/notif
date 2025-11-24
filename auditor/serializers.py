from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import datetime
from .models import MissionAudit

class MissionAuditSerializer(serializers.ModelSerializer):
    """
    Serializer pour créer et valider une mission d'audit
    """ 
    # Champs obligatoires pour la création
 
    
    title = serializers.CharField(
        required=True,
        max_length=300,
        help_text="Titre détaillé du projet"
    )
    
    description = serializers.CharField(
        required=True,
        help_text="Description détaillée de la mission"
    )
    
    start_date = serializers.DateTimeField(
        required=True,
        help_text="Date de début de la mission (format ISO: 2025-02-12T22:23:52.900Z)"
    )
    
    # Champs avec valeurs par défaut
    mission_type = serializers.CharField(
        required=False,
        max_length=20,
        default="COMPLIANCE",
        help_text="Type de mission (COMPLIANCE, TECHNICAL, SECURITY, etc.)"
    )
     
    # Dates optionnelles
    end_date = serializers.DateTimeField(
        required=False,
        allow_null=True,
        help_text="Date de fin prévue"
    )
     
    # Acteurs
    auditor_name = serializers.CharField(
        required=False,
        max_length=255,
        help_text="Nom de l'auditeur principal"
    )
    
    auditor_email = serializers.EmailField(
        required=False,
        allow_blank=True,
        help_text="Email de l'auditeur"
    )
     
    company = serializers.CharField(
        required=True,
        max_length=255,
        help_text="Nom de l'organisation auditée"
    )
    
    # URLs
    access_url = serializers.URLField(
        required=False,
        allow_null=True,
        help_text="URL d'accès au module d'audit"
    )
      
    base_url = serializers.URLField(
        required=False,
        allow_null=True,
        help_text="URL de base pour les ressources"
    )
    
    # Sécurité
    jwt_token = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Token JWT d'authentification"
    )
     
    # Références système
    id_client = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="ID du client dans le système"
    )
    
    id_mission = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="ID du projet associé"
    )
     
    # Configuration
    language = serializers.CharField(
        required=False,
        max_length=10,
        default="fr-FR",
        help_text="Langue de communication (fr-FR, en-US, etc.)"
    )
      
    class Meta:
        model = MissionAudit
        fields = [
            "id",
            "title",
            "description",
            "start_date",
            "end_date",
            "mission_type",
            "auditor_name",
            "auditor_email",
            "company",
            "access_url",
            "base_url",
            "jwt_token",
            "id_client",
            "id_mission",
            "language",
        ]
        read_only_fields = ["id"]
        extra_kwargs = {
            "description": {"required": True},
            "title": {"required": True},
            "company": {"required": True},
            "start_date": {"required": True},
        }