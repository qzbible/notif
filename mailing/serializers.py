
 
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
     