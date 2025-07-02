
 
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

# Update url_image to be a list of strings
class AssignBugSerializer(serializers.Serializer):
    name = serializers.CharField(
        required=False, 
        help_text="Objet de l'exigence"
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Description détaillée de l'exigence"
    )
    company = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Nom de l'entreprise"
    )
    module = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Nom de l'entreprise"
    )
    fichiers_urls = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="Liste des noms des expéditeurs"
    )
    to_emails = serializers.ListField(
        child=serializers.CharField(),
        required=True,
        help_text="Liste des noms des expéditeurs"
    )
    status = serializers.CharField(
        required=False,
        allow_blank=False,
        help_text="Description détaillée de l'exigence"
    )
    back_url =  serializers.CharField(
        required=False,
        allow_blank=False,
        help_text="Description détaillée de l'exigence"
    )
    lang = serializers.CharField(
        required=False,
        allow_blank=False,
        help_text="Description détaillée de l'exigence"
    ) 

# Serializer pour valider les données d'entrée
class ResolveBugSerializer(serializers.Serializer):
    module = serializers.CharField(
        required=True, 
        help_text="Objet de l'exigence"
    )
    old_date = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Description détaillée de l'exigence"
    )
    to_emails = serializers.ListField(
        child=serializers.CharField(),
        required=True,
        help_text="Liste des noms des expéditeurs"
    )
    back_url =  serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Description détaillée de l'exigence"
    )


 
