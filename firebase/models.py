# models.py - Modèles Django pour les notifications Firebase

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class FCMToken(models.Model):
    """
    Modèle pour stocker les tokens FCM des utilisateurs
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='fcm_token_info')
    token = models.TextField('Token FCM')
    device_type = models.CharField(
        'Type d\'appareil',
        max_length=20,
        choices=[
            ('android', 'Android'),
            ('ios', 'iOS'),
            ('web', 'Web'),
        ],
        default='android'
    )
    is_active = models.BooleanField('Actif', default=True)
    created_at = models.DateTimeField('Créé le', auto_now_add=True)
    updated_at = models.DateTimeField('Mis à jour le', auto_now=True)
    
    class Meta:
        db_table = 'fcm_tokens'
        verbose_name = 'Token FCM'
        verbose_name_plural = 'Tokens FCM'
    
    def __str__(self):
        return f"{self.user.username} - {self.device_type}"


class NotificationHistory(models.Model):
    """
    Historique des notifications envoyées
    """
    NOTIFICATION_TYPES = [
        ('reading_reminder', 'Rappel de lecture'),
        ('verse_of_day', 'Verset du jour'),
        ('couple_notification', 'Notification de couple'),
        ('reading_plan_update', 'Mise à jour plan de lecture'),
        ('achievement_unlocked', 'Réussite débloquée'),
        ('general', 'Générale'),
    ]
    
    RECIPIENT_TYPES = [
        ('user', 'Utilisateur'),
        ('topic', 'Topic'),
        ('bulk', 'Groupe'),
    ]
    
    STATUS_CHOICES = [
        ('sent', 'Envoyée'),
        ('failed', 'Échec'),
        ('pending', 'En attente'),
    ]
    
    title = models.CharField('Titre', max_length=255)
    body = models.TextField('Corps du message')
    notification_type = models.CharField('Type', max_length=50, choices=NOTIFICATION_TYPES)
    recipient_type = models.CharField('Type de destinataire', max_length=20, choices=RECIPIENT_TYPES)
    
    # Pour les notifications individuelles
    recipient_user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='Destinataire'
    )
    
    # Pour les topics
    topic_name = models.CharField('Nom du topic', max_length=100, blank=True)
    
    # Données personnalisées envoyées
    custom_data = models.JSONField('Données personnalisées', default=dict, blank=True)
    
    # Statut et métadonnées
    status = models.CharField('Statut', max_length=20, choices=STATUS_CHOICES, default='pending')
    firebase_message_id = models.CharField('ID message Firebase', max_length=255, blank=True)
    error_message = models.TextField('Message d\'erreur', blank=True)
    
    # Utilisateur qui a déclenché l'envoi
    sent_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_notifications',
        verbose_name='Envoyé par'
    )
    
    sent_at = models.DateTimeField('Envoyé le', auto_now_add=True)
    
    class Meta:
        db_table = 'notification_history'
        verbose_name = 'Historique de notification'
        verbose_name_plural = 'Historique des notifications'
        ordering = ['-sent_at']
    
    def __str__(self):
        return f"{self.title} - {self.get_notification_type_display()}"


class NotificationPreference(models.Model):
    """
    Préférences de notification des utilisateurs
    """
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='notification_preferences'
    )
    
    # Préférences par type de notification
    reading_reminders = models.BooleanField('Rappels de lecture', default=True)
    verse_of_day = models.BooleanField('Verset du jour', default=True)
    couple_notifications = models.BooleanField('Notifications de couple', default=True)
    reading_plan_updates = models.BooleanField('Mises à jour des plans', default=True)
    achievements = models.BooleanField('Réussites', default=True)
    general_notifications = models.BooleanField('Notifications générales', default=True)
    
    # Horaires préférés pour les notifications
    reminder_time = models.TimeField(
        'Heure des rappels',
        default=timezone.now().replace(hour=9, minute=0).time(),
        help_text='Heure préférée pour recevoir les rappels de lecture'
    )
    
    timezone = models.CharField(
        'Fuseau horaire',
        max_length=50,
        default='Europe/Paris'
    )
    
    created_at = models.DateTimeField('Créé le', auto_now_add=True)
    updated_at = models.DateTimeField('Mis à jour le', auto_now=True)
    
    class Meta:
        db_table = 'notification_preferences'
        verbose_name = 'Préférences de notification'
        verbose_name_plural = 'Préférences de notification'
    
    def __str__(self):
        return f"Préférences de {self.user.username}"


# Extension du modèle User pour ajouter les méthodes FCM
def get_fcm_token(self):
    """Récupère le token FCM actuel de l'utilisateur"""
    try:
        return self.fcm_token_info.token
    except FCMToken.DoesNotExist:
        return None

def has_valid_fcm_token(self):
    """Vérifie si l'utilisateur a un token FCM valide"""
    try:
        return self.fcm_token_info.is_active and bool(self.fcm_token_info.token)
    except FCMToken.DoesNotExist:
        return False

def update_fcm_token(self, token, device_type='android'):
    """Met à jour ou crée le token FCM de l'utilisateur"""
    fcm_token_obj, created = FCMToken.objects.update_or_create(
        user=self,
        defaults={
            'token': token,
            'device_type': device_type,
            'is_active': True
        }
    )
    return fcm_token_obj

# Ajouter ces méthodes au modèle User
User.add_to_class('get_fcm_token', get_fcm_token)
User.add_to_class('has_valid_fcm_token', has_valid_fcm_token)
User.add_to_class('update_fcm_token', update_fcm_token)


# Signals pour automatiser certaines actions
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_notification_preferences(sender, instance, created, **kwargs):
    """Crée automatiquement les préférences de notification pour les nouveaux utilisateurs"""
    if created:
        NotificationPreference.objects.get_or_create(user=instance)