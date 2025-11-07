
 
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
 
from django.utils import timezone
from datetime import timedelta
from dateutil.relativedelta import relativedelta
# Serializer pour valider les données d'entrée
class ExigenceSerializer(serializers.Serializer):
    object = serializers.CharField(
        required=True, 
        help_text="Objet de l'exigence"
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Description détaillée de l'exigence"
    )
    company = serializers.CharField(
        required=True,
        allow_blank=True,
        help_text="Nom de l'entreprise"
    )
    dest_email = serializers.EmailField(
        required=True,
        help_text="Email du destinataire"
    )
    sender_name = serializers.CharField(
        required=True,
         allow_blank=True,
        help_text="Nom de l'expéditeur"
    )
    dest_name = serializers.CharField(
        required=True,
         allow_blank=True,
        help_text="Nom du destinataire"
    )
    url = serializers.URLField(
        required=True,
        allow_null=True, 
        help_text="URL pour le lien front end de l'exigence"
    )
    method = serializers.CharField(
        required=False,
        allow_null=True, 
        allow_blank=True,
        help_text="Methode  de l'exigence"
    )
    base_url = serializers.URLField(
        required=False,
        allow_null=True, 
        help_text="Url pour les image de référence de l'exigence"
    )
    jwt_token = serializers.CharField(
        required=True,
        allow_null=True, 
        help_text="Token user config exigence"
    )
    scope = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="Liste des périmètres d'application de l'exigence"
    )
    id_action =  serializers.CharField(
        required=False,
        allow_null=True, 
        help_text="Id de l'action"
    )
    id_project =  serializers.CharField(
        required=False,
        allow_null=True, 
        help_text="Id de project"
    )
    id_analysis =  serializers.CharField(
        required=False,
        allow_null=True, 
        help_text="Id de l'analysis"
    )
    id_reporting =  serializers.CharField(
        required=False,
        allow_null=True, 
        help_text="Id de l'reporting"
    )
    id_indicateur =  serializers.CharField(
        required=False,
        allow_null=True, 
        help_text="Id de l'indicateur"
    )
    id_client =  serializers.CharField(
        required=False,
        allow_null=True, 
        help_text="Id de l'indicateur"
    )
    dealine = serializers.CharField(
        required=False,
        allow_null=True, 
        help_text="Deadline de l'exigence"
    )
    time = serializers.CharField(
        required=False,
        help_text="time de l'exigence"
    )
    start_date = serializers.CharField(
        required=False,
        allow_null=True, 
        help_text="time de l'exigence"
    )

    type_task = serializers.CharField(
        required=False,
        help_text="time de l'exigence"
    )
    lang = serializers.CharField(
        required=False,
        help_text="time de l'exigence"
    )
    role = serializers.CharField(
        required=False,
        help_text="role de l'acteurs"
    )

 


# Serializer pour valider les données d'entrée
class ExigenceSheduleSerializer(serializers.Serializer):
    id = serializers.CharField(
        required=True, 
        help_text="Objet de l'exigence"
    )
    


# Serializer pour valider les données d'entrée
class ExigenceUpdateSheduleSerializer(serializers.Serializer):
    id = serializers.CharField(
        required=True, 
        help_text="Objet de l'exigence"
    )
    new_date = serializers.CharField(
        required=True, 
        help_text="Objet de l'exigence"
    )
    
# Serializer pour la réponse
class ExigenceResponseSerializer(serializers.Serializer):
    message = serializers.CharField(default="Exigence créée avec succès")
    status = serializers.CharField(default="success")
    code = serializers.IntegerField(default=201)


# Serializer pour les erreurs
class ErrorResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    errors = serializers.JSONField(required=False)



# Serializer pour valider les données d'entrée
class AcceptSerializer(serializers.Serializer):
    
    object = serializers.CharField(
        required=True, 
        help_text="Objet de l'exigence"
    )

    description = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Description détaillée de l'exigence"
    )

    company = serializers.CharField(
        required=True,
        allow_blank=True,
        help_text="Nom de l'entreprise"
    )

    email = serializers.EmailField(
        required=True,
        help_text="Email du destinataire"
    )

    name = serializers.CharField(
        required=True,
         allow_blank=True,
        help_text="Nom de l'expéditeur"
    )

    dest_name = serializers.CharField(
        required=True,
         allow_blank=True,
        help_text="Nom du destinataire"
    )
    consulted = serializers.ListField(
        child=serializers.JSONField(),
        required=False,
        allow_null=True,
        help_text="Liste des participants au format JSON pour le modèle. Si non fourni, peut être dérivé de 'participants'."
    )

    action_id = serializers.IntegerField(
        required=False,
        min_value=1,
        help_text="Nombre d'éléments à arbitrer"
    )
    reporting_id = serializers.IntegerField(
        required=False,
        min_value=1,
        help_text="Nombre d'éléments à arbitrer"
    )
    analysis_id = serializers.IntegerField(
        required=False,
        min_value=1,
        help_text="Nombre d'éléments à arbitrer"
    )
    project_id = serializers.IntegerField(
        required=False,
        min_value=1,
        help_text="Nombre d'éléments à arbitrer"
    )

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
