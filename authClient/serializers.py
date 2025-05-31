from rest_framework import serializers


# Serializer pour valider les données d'entrée
class ClientAuthMailSerializer(serializers.Serializer):
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
    url_connect = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=255,
        help_text="URL de connexion"
    )
    base_url = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=255,
        help_text="URL de base"
    )
   
    token = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Token JWT pour l'authentification"
    )
    client_id = serializers.CharField(
        required=True,
        max_length=255,
        help_text="Identifiant unique du client"
    )
    lang = serializers.CharField(
        required=True,
        max_length=255,
        help_text="Langue de l'email (par exemple, 'fr', 'en')"
    )
    company = serializers.CharField(
        required=False,
        max_length=255,
        help_text="nom de l'entreprise (optionnel, utilisé pour l'envoi d'email)"
    )
    surfix = serializers.CharField(
        required=False,
        max_length=255,
        help_text="nom de l'entreprise (optionnel, utilisé pour l'envoi d'email)"
    )
    is_send = serializers.BooleanField(
        required=False,
        default=False,
        help_text="Indique si l'email a été envoyé"
    )