
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.core.files.storage import default_storage
from .models import *


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)

        # Vérification de l'existence du fichier sur le stockage
        file_path = instance.file.name  # Nom du fichier dans le storage
        if not default_storage.exists(file_path):
            print('fichier introuvable')
            # from rest_framework.exceptions import NotFound
            # raise NotFound(f"Le fichier {file_path} est introuvable sur le serveur.")
        
        if data.get('file'):
            # Récupère l'URL du fichier
            file_url = instance.file.url if instance.file else None
            if file_url: 
                if file_url.startswith('http'):
                    # Extrait le chemin relatif (tout après le domaine)
                    from urllib.parse import urlparse
                    parsed = urlparse(file_url)
                    file_path = parsed.path
                else:
                    file_path = file_url 
                # Retire le préfixe /media/ s'il existe
                if file_path.startswith('/media/'):
                    file_path = file_path[7:]  # Retire les 7 premiers caractères (/media/)
                
                data['file'] = file_path

        return data

 
