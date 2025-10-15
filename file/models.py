from django.db import models
import os
from django.conf import settings
import shutil

# Create your models here.

# File Model
class File(models.Model): 
    file = models.FileField(blank=False, null=False)
    remark = models.CharField(max_length=255)
    path = models.CharField(max_length=255, null=True, blank=True)
    fileType = models.CharField(max_length=255,  blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
     
    @classmethod
    def initialize_data(cls, directory_path='file/icons', destination='icons'):

        images_directory = os.path.join(settings.BASE_DIR_FOLDER, directory_path)  
        print("f", images_directory)
        destination_directory = os.path.join(settings.MEDIA_ROOT, destination)
        print("f", destination_directory)
        # Vérifie si le dossier destination existe, sinon le créer
        os.makedirs(destination_directory, exist_ok=True)

        for filename in os.listdir(images_directory):
            if filename.endswith(('.jpg', '.jpeg', '.png', '.gif', '.svg')): 
                source_file = os.path.join(images_directory, filename)
                destination_file = os.path.join(destination_directory, filename)

                # Copier le fichier si ce n'est pas déjà fait
                if not os.path.exists(destination_file): 
                    shutil.copy(source_file, destination_file) 
                    
                # Enregistrer dans la base avec le bon chemin
                file_instance, created = File.objects.get_or_create(
                    file=f'{destination}/{filename}',  # Correction ici
                    remark=filename,
                    fileType="type"
                )
                if created:
                    print(f"✅ Ajout en base : {file_instance.file}")
                else:
                    print(f"ℹ️ Fichier déjà en base : {file_instance.file}")