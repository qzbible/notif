from django.db import models

# Create your models here. 
class ProjetMail(models.Model):
    projet_id = models.CharField(max_length=255, null=True, blank=True)
    user_email = models.CharField(max_length=255, null=True, blank=True)
    task_id = models.CharField(max_length=255, null=True, blank=True)
    