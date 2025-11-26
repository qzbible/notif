from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import datetime
from .models import  Task


 
from django.utils import timezone
from datetime import timedelta
from dateutil.relativedelta import relativedelta

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
        model = Task
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



# Serializer pour les acteurs
class ActorFollowSerializer(serializers.Serializer):
    role = serializers.CharField(
        required=True,
        help_text="Rôle de l'acteur (ex: RESPONSABLE, COLLABORATEUR)"
    )
    
    id_user = serializers.IntegerField(
        required=True,
        help_text="ID de l'utilisateur"
    )
    
    full_name = serializers.CharField(
        required=True,
        help_text="Nom complet de l'acteur"
    )
    
    email = serializers.EmailField(
        required=True,
        help_text="Email de l'acteur"
    )

    jwt_token = serializers.CharField(
        required=True,
        allow_null=True, 
        help_text="Token user config exigence"
    )


# Serializer principal pour FollowUp
class FollowUpSerializer(serializers.Serializer):
    unit = serializers.ChoiceField(
        choices=['minutes', 'hours', 'days', 'weeks', 'months'],
        required=True,
        help_text="Unité de temps pour le délai"
    )
    
    value = serializers.IntegerField(
        required=True,
        min_value=0,
        help_text="Valeur du délai"
    )
    
    type = serializers.ChoiceField(
        choices=['after', 'before'],
        required=True,
        help_text="Type de calcul (après ou avant la deadline)"
    )
    
    id_project = serializers.IntegerField(
        required=True,
        help_text="ID du projet"
    )
    
    id_action = serializers.IntegerField(
        required=True,
        help_text="ID de l'action"
    )
    
    id_client = serializers.IntegerField(
        required=True,
        help_text="ID du client"
    )
    
    deadline = serializers.DateTimeField(
        required=True,
        help_text="Date limite au format ISO (ex: 2025-02-12T22:23:52.900Z)"
    )
    
    actors = ActorFollowSerializer(
        many=True,
        required=True,
        help_text="Liste des acteurs concernés"
    )
    
    def validate_actors(self, value):
        """Valider qu'il y a au moins un acteur"""
        if not value:
            raise serializers.ValidationError("Au moins un acteur est requis")
        return value
    
    def validate(self, data):
        """Validation globale - calculer et valider l'eta"""
        # Calculer l'eta_datetime
        eta_datetime = self.calcul_date(
            deadline=data['deadline'],
            unit=data['unit'],
            value=data['value'],
            type=data['type']
        )
        
        # Vérifier que la date calculée est dans le futur
        if eta_datetime <= timezone.now():
            raise serializers.ValidationError({
                "eta": "La date calculée doit être dans le futur"
            })
        
        # Ajouter eta_datetime aux données validées
        data['eta_datetime'] = eta_datetime
        
        return data
    
    def calcul_date(self, deadline, unit, value, type):
        """
        Calcule la date d'envoi du mail basée sur la deadline
        """
        # S'assurer que deadline est timezone-aware
        if timezone.is_naive(deadline):
            deadline = timezone.make_aware(deadline)
        
        # Calculer le delta selon l'unité
        if unit == "minutes":
            delta = timedelta(minutes=value)
        elif unit == "hours":
            delta = timedelta(hours=value)
        elif unit == "days":
            delta = timedelta(days=value)
        elif unit == "weeks":
            delta = timedelta(weeks=value)
        elif unit == "months":
            delta = relativedelta(months=value)
        else:
            raise serializers.ValidationError(
                f"Unité '{unit}' non reconnue"
            )
        
        # Appliquer le delta selon le type
        if type == "after":
            result_date = deadline + delta
        elif type == "before":
            result_date = deadline - delta
        else:
            raise serializers.ValidationError(
                f"Type '{type}' non reconnu"
            )
        
        return result_date