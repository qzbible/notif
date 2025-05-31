from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone


class ClientAuthMail(models.Model):
    """
        Model to store client authentication email details.
    """
    email = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    url_connect = models.CharField(max_length=255, blank=True, null=True)
    base_url = models.CharField(max_length=255, blank=True, null=True)
    # url_auth_code = models.CharField(max_length=255, blank=True, null=True)
    jwt_token = models.TextField(null=True, blank=True)
    client_id = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_send = models.BooleanField(default=False)
    lang = models.CharField(max_length=10, blank=True, null=True)
    company = models.CharField(max_length=255, blank=True, null=True)
    surfix = models.CharField(max_length=255, blank=True, null=True)



class authCodeClient(models.Model):
    code = models.CharField(max_length=255, null=True, blank=True)
    token = models.CharField(max_length=255, null=True, blank=True)
    expires_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.code
