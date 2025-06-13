
 
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
 

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
        help_text="URL pour le lien front end de l'exigence"
    )
    method = serializers.CharField(
        required=False,
        help_text="Methode  de l'exigence"
    )
    base_url = serializers.URLField(
        required=True,
        help_text="Url pour les image de référence de l'exigence"
    )
    jwt_token = serializers.CharField(
        required=True,
        help_text="Token user config exigence"
    )
    scope = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="Liste des périmètres d'application de l'exigence"
    )
    id_action =  serializers.CharField(
        required=False,
        help_text="Id de l'action"
    )
    id_analysis =  serializers.CharField(
        required=False,
        help_text="Id de l'analysis"
    )
    id_reporting =  serializers.CharField(
        required=False,
        help_text="Id de l'reporting"
    )
    id_indicateur =  serializers.CharField(
        required=False,
        help_text="Id de l'indicateur"
    )
    dealine = serializers.CharField(
        required=False,
        help_text="Deadline de l'exigence"
    )
    time = serializers.CharField(
        required=False,
        help_text="time de l'exigence"
    )
    start_date = serializers.CharField(
        required=False,
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




# Serializer pour valider les données d'entrée
class TaskSerializer(serializers.Serializer):
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
        help_text="URL pour le lien front end de l'exigence"
    )
    method = serializers.CharField(
        required=False,
        help_text="Methode  de l'exigence"
    )
    base_url = serializers.URLField(
        required=True,
        help_text="Url pour les image de référence de l'exigence"
    )
    jwt_token = serializers.CharField(
        required=True,
        help_text="Token user config exigence"
    )

    id_action =  serializers.CharField(
        required=False,
        help_text="Id de l'action"
    )
    during = serializers.CharField(
        required=False,
        help_text="time de l'exigence"
    )
    start_date = serializers.CharField(
        required=False,
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
