from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone

class ExigenceMail(models.Model):
    object = models.TextField(
        verbose_name="Description détaillée de l'exigence"
    )
    description = models.TextField(
        verbose_name="Description détaillée de l'exigence"
    )
    company = models.TextField(
        verbose_name="Description détaillée de l'exigence"
    )
    dest_email = models.EmailField(
        verbose_name="Email du destinataire"
    )
    sender_name = models.CharField(
        max_length=255,
        verbose_name="Nom de l'expéditeur"
    )
    dest_name = models.CharField(
        max_length=255,
        verbose_name="Nom du destinataire"
    )
    url = models.TextField(
        verbose_name="Description détaillée de l'exigence"
    )
    method = models.TextField(
        verbose_name="Description détaillée de l'exigence"
    )
    base_url =models.TextField(
        verbose_name="Description détaillée de l'exigence"
    )
    jwt_token = models.TextField(
        verbose_name="Token user config exigence"
    )
    # Utilisation d'ArrayField pour stocker une liste de chaînes (nécessite PostgreSQL)
    scope = ArrayField(
        models.TextField(),
        blank=True,
        null=True,
        verbose_name="Liste des périmètres d'application de l'exigence"
    )
    # Champ pour la date de création
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    is_send =  models.BooleanField(default=False)
    id_action = models.CharField(max_length=255, null=True, blank=True)
    id_analysis = models.CharField(max_length=255, null=True, blank=True)
    id_indicateur = models.CharField(max_length=255, null=True, blank=True)
    id_reporting = models.CharField(max_length=255, null=True, blank=True)
    dealine = models.CharField(
        max_length=255,
        verbose_name="Nom de l'expéditeur",
         null=True,
    )
    time = models.CharField(
        max_length=255,
        verbose_name="Nom de l'expéditeur",
         null=True,
    )
    start_date = models.CharField(
        max_length=255,
        verbose_name="Date de début",
         null=True,
    )
    type_task = models.CharField(
        max_length=255,
        verbose_name="Date de début",
         null=True,
    )
    
    class Meta:
        verbose_name = "Exigence"
        verbose_name_plural = "Exigences"
        ordering = ['-created_at']  # Tri par date de création, du plus récent au plus ancien
    
    def __str__(self):
        return f"{self.object} - {self.company}"


class auth_code(models.Model):
    code = models.CharField(max_length=255, null=True, blank=True)
    token = models.CharField(max_length=255, null=True, blank=True)
    expires_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.code