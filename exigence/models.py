from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone

class ExigenceMail(models.Model):
    object = models.TextField(
        verbose_name="Description détaillée de l'exigence",
          null=True,
        blank=True
    )
    description = models.TextField(
        verbose_name="Description détaillée de l'exigence",
        null=True,
        blank=True

    )
    company = models.TextField(
        verbose_name="Description détaillée de l'exigence",
          null=True,
        blank=True
    )
    dest_email = models.EmailField(
        verbose_name="Email du destinataire",
          null=True,
        blank=True
    )
    sender_name = models.CharField(
        max_length=255,
        verbose_name="Nom de l'expéditeur",
          null=True,
        blank=True
    )
    dest_name = models.CharField(
        max_length=255,
        verbose_name="Nom du destinataire",
          null=True,
        blank=True
    )
    url = models.TextField(
        verbose_name="Description détaillée de l'exigence",
          null=True,
        blank=True
    )
    method = models.TextField(
        verbose_name="Description détaillée de l'exigence",
          null=True,
        blank=True
    )
    base_url =models.TextField(
        verbose_name="Description détaillée de l'exigence",
          null=True,
        blank=True
    )
    jwt_token = models.TextField(
        verbose_name="Token user config exigence",
          null=True,
        blank=True
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
    is_notification =  models.BooleanField(default=False)
    is_approver =  models.BooleanField(default=False)
    is_send =  models.BooleanField(default=False)
    is_answer =  models.BooleanField(default=False)
    id_action = models.CharField(max_length=255, null=True, blank=True)
    id_project = models.CharField(max_length=255, null=True, blank=True)
    id_analysis = models.CharField(max_length=255, null=True, blank=True)
    id_indicateur = models.CharField(max_length=255, null=True, blank=True)
    id_reporting = models.CharField(max_length=255, null=True, blank=True)
    id_answer = models.CharField(max_length=255, null=True, blank=True)
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
    lang = models.CharField(max_length=255, default="fr-FR") #fr/en

    sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    task_id = models.CharField(max_length=255, null=True, blank=True)
    
    id_client = models.BigIntegerField(null=True, blank=True)


    class Meta:
        verbose_name = "Exigence"
        verbose_name_plural = "Exigences"
        ordering = ['-created_at']  # Tri par date de création, du plus récent au plus ancien
    
    def __str__(self):
        return f"{self.object} - {self.company}"



class FollowUp(models.Model): 
    unit = models.CharField(max_length=255, null=True, blank=True)  
    value =  models.IntegerField(default=0)
    type =  models.CharField(max_length=255, null=True, blank=True) #before/after
    id_project = models.BigIntegerField(null=True, blank=True)
    id_action = models.BigIntegerField(null=True, blank=True)
    id_client = models.BigIntegerField(null=True, blank=True)
    deadline = models.DateTimeField(null=True, blank=True)
    



class ActorFollow(models.Model):
    role = models.TextField(null=True, blank=True) #responsable/approver/notification
    id_user = models.BigIntegerField(null=True, blank=True)
    full_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True) 
    follow_up = models.ForeignKey(FollowUp, on_delete=models.CASCADE, related_name="actor_follow_up", null=True)
    task_id = models.CharField(max_length=255, null=True, blank=True)




class auth_code(models.Model):
    code = models.CharField(max_length=255, null=True, blank=True)
    token = models.CharField(max_length=255, null=True, blank=True)
    expires_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.code
    
