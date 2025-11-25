from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone

# Create your models here.
# class MissionAudit(models.Model): 
#     """Modèle représentant une mission d'audit"""
#     title = models.CharField(
#         max_length=300,
#         null=True, 
#     )
    
#     description = models.TextField( 
#         null=True, 
#     )
    
#     mission_type = models.CharField(
#         max_length=20,
#         null=True, 
#     )
     
#     start_date = models.DateTimeField(
#         verbose_name="Date de début",
#         help_text="Date de lancement de la mission"
#     )
    
#     end_date = models.DateTimeField(
#         verbose_name="Date de fin prévue",
#         null=True,
#         blank=True
#     )
     
#     # === ACTEURS DE LA MISSION ===
#     auditor_name = models.CharField(
#         max_length=255,
#         null=True, 
#     )
    
#     auditor_email = models.EmailField(
#         verbose_name="Email de l'auditeur",
#          null=True,
#         blank=True
#     )
     
#     company = models.CharField(
#         max_length=255,
#         null=True,
#         blank=True
#     )
    
#     # === URLS ET LIENS ===
#     access_url = models.URLField(
#         verbose_name="URL d'accès au module",
#         null=True,
#         blank=True,
#         help_text="Lien vers l'interface d'audit"
#     )
    
#     base_url = models.URLField(
#         verbose_name="URL de base",
#         null=True,
#         blank=True,
#         help_text="URL de base pour les ressources (images, etc.)"
#     )
    
#     # === AUTHENTIFICATION ET SÉCURITÉ ===
#     jwt_token = models.TextField(
#         verbose_name="Token JWT",
#         null=True,
#         blank=True,
#         help_text="Token d'authentification pour l'accès"
#     )
    
#     access_code = models.CharField(
#         max_length=50,
#         verbose_name="Code d'accès",
#         null=True,
#         blank=True,
#         help_text="Code d'accès temporaire si nécessaire"
#     )
    
#     # === RÉFÉRENCES SYSTÈME ===
#     id_client = models.BigIntegerField(
#         verbose_name="ID Client",
#         null=True,
#         blank=True
#     )
    
#     id_project = models.BigIntegerField(
#         verbose_name="ID Projet",
#         null=True,
#         blank=True
#     )
#     id_demande = models.BigIntegerField(
#         verbose_name="ID Projet",
#         null=True,
#         blank=True
#     )
     
#     # === CONFIGURATION ===
#     language = models.CharField(
#         max_length=10,
#         null=True,
#         blank=True,
#         verbose_name="Langue de communication"
#     )
     
#     created_at = models.DateTimeField(
#         auto_now_add=True,
#         verbose_name="Date de création"
#     )
    
#     updated_at = models.DateTimeField(
#         auto_now=True,
#         verbose_name="Date de modification"
#     )
#     is_mission =  models.BooleanField(default=False)
#     is_demande =  models.BooleanField(default=False)

#     test = models.CharField(
#         max_length=255,
#         null=True,
#         blank=True
#     )
#     jwt_token = models.CharField(
#         max_length=255,
#         null=True,
#         blank=True
#     )
    
#     expires_code_at = models.DateTimeField(default=timezone.now)


#     class Meta:
#         verbose_name = "Exigence"
#         verbose_name_plural = "Exigences"
#         ordering = ['-created_at']  # Tri par date de création, du plus récent au plus ancien
    
#     def __str__(self):
#         return f"{self.object} - {self.company}"
    


# Create your models here.
class Task(models.Model): 
    """Modèle représentant une mission d'audit"""
    title = models.CharField(
        max_length=300,
        null=True, 
    )
    
    description = models.TextField( 
        null=True, 
    )
    
    mission_type = models.CharField(
        max_length=20,
        null=True, 
    )
     
    start_date = models.DateTimeField(
        verbose_name="Date de début",
        help_text="Date de lancement de la mission"
    )
    
    end_date = models.DateTimeField(
        verbose_name="Date de fin prévue",
        null=True,
        blank=True
    )
     
    # === ACTEURS DE LA MISSION ===
    auditor_name = models.CharField(
        max_length=255,
        null=True, 
    )
    
    auditor_email = models.EmailField(
        verbose_name="Email de l'auditeur",
         null=True,
        blank=True
    )
     
    company = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    
    # === URLS ET LIENS ===
    access_url = models.URLField(
        verbose_name="URL d'accès au module",
        null=True,
        blank=True,
        help_text="Lien vers l'interface d'audit"
    )
    
    base_url = models.URLField(
        verbose_name="URL de base",
        null=True,
        blank=True,
        help_text="URL de base pour les ressources (images, etc.)"
    )
    
    # === AUTHENTIFICATION ET SÉCURITÉ ===
    jwt_token = models.TextField(
        verbose_name="Token JWT",
        null=True,
        blank=True,
        help_text="Token d'authentification pour l'accès"
    )
    
    access_code = models.CharField(
        max_length=50,
        verbose_name="Code d'accès",
        null=True,
        blank=True,
        help_text="Code d'accès temporaire si nécessaire"
    )
    
    # === RÉFÉRENCES SYSTÈME ===
    id_client = models.BigIntegerField(
        verbose_name="ID Client",
        null=True,
        blank=True
    )
    
    id_project = models.BigIntegerField(
        verbose_name="ID Projet",
        null=True,
        blank=True
    )
    id_demande = models.BigIntegerField(
        verbose_name="ID Projet",
        null=True,
        blank=True
    )
     
    # === CONFIGURATION ===
    language = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        verbose_name="Langue de communication"
    )
     
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de modification"
    )
    is_mission =  models.BooleanField(default=False)
    is_demande =  models.BooleanField(default=False)

    test = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    # jwt_token = models.CharField(
    #     max_length=255,
    #     null=True,
    #     blank=True
    # )
    
    expires_code_at = models.DateTimeField(default=timezone.now)


    class Meta:
        verbose_name = "Exigence"
        verbose_name_plural = "Exigences"
        ordering = ['-created_at']  # Tri par date de création, du plus récent au plus ancien
    
    def __str__(self):
        return f"{self.object} - {self.company}"
    

 
