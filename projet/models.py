from django.db import models
from django.contrib.postgres.fields import ArrayField
# Create your models here. 
class ProjetMail(models.Model):
    projet_id = models.CharField(max_length=255, null=True, blank=True)
    user_email = models.CharField(max_length=255, null=True, blank=True)
    task_id = models.CharField(max_length=255, null=True, blank=True)
    

class AlertIndicatorEmail(models.Model):
    id_indicator = models.IntegerField(null=True, blank=True)
    id_project = models.IntegerField(null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    seuil = models.CharField(max_length=255, null=True, blank=True)
    date_alert = models.CharField(max_length=255, null=True, blank=True)
    reporting_title = models.CharField(max_length=255, null=True, blank=True)
    percent_value = models.CharField(max_length=255, null=True, blank=True)
    url_connect = models.CharField(max_length=255, null=True, blank=True)
    task_id = models.CharField(max_length=255, null=True, blank=True)
    actors = ArrayField(models.JSONField(), null=True, blank=True)
    client = models.JSONField(null=True, blank=True)