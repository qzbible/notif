from django.db import models
from django.contrib.postgres.fields import ArrayField

# Create your models here.
class InstanceBoard(models.Model):
    id_instance = models.IntegerField(null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    url_connect = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    actors = ArrayField(models.JSONField(), null=True, blank=True)
    perimeter = ArrayField(models.JSONField(), null=True, blank=True)
    type = models.CharField(max_length=255, null=True, blank=True)
    format = models.CharField(max_length=255, null=True, blank=True)
    link = models.CharField(max_length=255, null=True, blank=True)
    recurrence_config = models.JSONField(null=True, blank=True)
    ponctuel_config = models.JSONField(null=True, blank=True)
    client = models.JSONField(null=True, blank=True)
    lang = models.CharField(max_length=10, null=True, blank=True)


    class Meta:
        db_table = 'instance_board'
        verbose_name = 'Instance Board'
        verbose_name_plural = 'Instance Boards'

    def __str__(self):
        return f'Instance Board {self.id_instance}'
     
    