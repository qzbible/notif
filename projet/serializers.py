
 
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
 

# Serializer pour valider les données d'entrée
 

# Serializer pour valider les données d'entrée
class StartProjectMailSerializer(serializers.Serializer):
    email = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=255,
        help_text="Adresse email du client"
    )
    name = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=255,
        help_text="Nom du client"
    )
    lang = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=255,
        help_text="lang"
    )
     

class IndicatorAlertSerializer(serializers.Serializer):
    """Serializer pour l'envoi des décisions du comité"""
    
    id_indicator = serializers.CharField(
        required=True,
        max_length=255,
        help_text="title"
    )
    id_project = serializers.CharField(
        required=True,
        max_length=255,
        help_text="title"
    )
    # Informations sur le comité
    title = serializers.CharField(
        required=True,
        max_length=255,
        help_text="title"
    )
    description = serializers.CharField(
        required=False,
        help_text="description"
    )
    seuil = serializers.CharField(
        required=True,
        help_text="Date d'échéance de la décision"
    )
    date_alert = serializers.CharField(
        required=False,
        help_text="Date d'échéance de la décision"
    )
    reportion_title = serializers.CharField(
        required=True,
        help_text="Date d'échéance de la décision"
    )
    percent_value = serializers.CharField(
        required=True,
        help_text="Date d'échéance de la décision"
    )
    actors = serializers.ListField(
        child=serializers.JSONField(),
        required=False,
        allow_null=True,
        help_text="Liste des participants au format JSON pour le modèle. Si non fourni, peut être dérivé de 'participants'."
    )
    
     
    # URL et configuration
    url_connect = serializers.URLField(
        required=True,
        help_text="URL de connexion à la plateforme"
    )
    
    client = serializers.JSONField(
        required=False,
        help_text="Fichier JSON optionnel"
    )
    
      
    # Langue
    lang = serializers.ChoiceField(
        choices=['fr-FR', 'en-US'],
        default='fr-FR',
        help_text="Langue de l'email (fr-FR ou en-US)"
    )
    
    
    
    def validate_actors(self, value):
        """Valider la structure des acteurs"""
        if not value:
            raise serializers.ValidationError("La liste des acteurs ne peut pas être vide")
        
        for actor in value:
            if 'email' not in actor:
                raise serializers.ValidationError("Chaque acteur doit avoir un email")
            if 'first_name' not in actor or 'last_name' not in actor:
                raise serializers.ValidationError("Chaque acteur doit avoir un prénom et un nom")
        
        return value
    
    
    