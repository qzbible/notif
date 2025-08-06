from django.db import models
from django.utils import timezone
# Create your models here.


class DeviseAuthMail(models.Model):
    """
        Model to store client authentication email details.
    """
    email = models.CharField(max_length=255, blank=True, null=True)
    device_type = models.CharField(max_length=255, blank=True, null=True)
    device_name = models.CharField(max_length=255, blank=True, null=True)
    os_name = models.CharField(max_length=255, blank=True, null=True)
    browser_name = models.CharField(max_length=255, blank=True, null=True)
    # browser_version = models.CharField(max_length=255, blank=True, null=True)
    device_fingerprint = models.CharField(max_length=255, blank=True, null=True)
    # request_path = models.CharField(max_length=255, blank=True, null=True)
    # forwarded_ips = models.CharField(max_length=255, blank=True, null=True)
    url_connect = models.CharField(max_length=255, blank=True, null=True)
    url_verification = models.CharField(max_length=255, blank=True, null=True)
    base_url = models.CharField(max_length=255, blank=True, null=True)
    # url_auth_code = models.CharField(max_length=255, blank=True, null=True)
    token = models.TextField(null=True, blank=True)
    client_id = models.CharField(max_length=255, null=True)
    device_id = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    is_send = models.BooleanField(default=False)
    lang = models.CharField(max_length=10, blank=True, null=True)
    company = models.CharField(max_length=255, blank=True, null=True)
    surfix = models.CharField(max_length=255, blank=True, null=True)


class authCode(models.Model):
    code = models.CharField(max_length=255, null=True, blank=True)
    token = models.CharField(max_length=255, null=True, blank=True)
    expires_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.code

class EmailVerification(models.Model):
    code = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    expires_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.code

