from rest_framework import serializers

 

# Serializer pour valider les données d'entrée
class AlertSecurityMailSerializer(serializers.Serializer):
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
     