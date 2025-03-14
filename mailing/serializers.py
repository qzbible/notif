
 
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
 

# Serializer pour valider les données d'entrée
class ExigenceSerializer(serializers.Serializer):
    object = serializers.CharField(required=True, help_text="Objet du mail (ex: Demande de permission)")
    user_name = serializers.CharField(required=True, help_text="Nom d'utilisateur")
    destinator = serializers.ListField(
        child=serializers.EmailField(),
        required=True,
        help_text="Liste des adresses email des destinataires"
    )
    company = serializers.CharField(required=True, help_text="Nom de l'entreprise")
    url = serializers.URLField(required=True, help_text="URL (ex: https://example.com)")

    def validate_destinator(self, value):
        if not value:
            raise serializers.ValidationError(_("La liste des destinataires ne peut pas être vide."))
        return value