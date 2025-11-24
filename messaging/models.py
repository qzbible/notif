from django.db import models
import uuid

class OutboxEvent(models.Model):
    """Pattern Outbox pour garantir la livraison des messages"""
    
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('processing', 'En cours'),
        ('completed', 'Terminé'),
        ('failed', 'Échec'),
    ]
    
    event_id = models.UUIDField(default=uuid.uuid4, unique=True)
    exchange = models.CharField(max_length=100)
    routing_key = models.CharField(max_length=100)
    payload = models.JSONField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    attempts = models.PositiveIntegerField(default=0)
    max_attempts = models.PositiveIntegerField(default=3)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    next_retry_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    class Meta:
        db_table = 'messaging_outbox_events'
        indexes = [
            models.Index(fields=['status', 'next_retry_at']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.exchange}/{self.routing_key} - {self.status}"