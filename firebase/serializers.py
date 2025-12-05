# serializers/notification_serializers.py

from rest_framework import serializers

class SendNotificationSerializer(serializers.Serializer):
    """
    Serializer pour l'envoi de notifications Firebase génériques
    """
    type = serializers.ChoiceField(
        choices=[
            ('reading_reminder', 'Rappel de lecture'),
            ('verse_of_day', 'Verset du jour'),
            ('couple_notification', 'Notification de couple'),
            ('reading_plan_update', 'Mise à jour plan de lecture'),
            ('achievement_unlocked', 'Réussite débloquée'),
            ('general', 'Générale'),
        ],
        help_text="Type de notification à envoyer"
    )
    recipient = serializers.ChoiceField(
        choices=[('token', 'Token FCM'), ('topic', 'Topic Firebase')],
        help_text="Type de destinataire"
    )
    recipient_value = serializers.CharField(
        max_length=500,
        help_text="Token FCM ou nom du topic selon le type de destinataire"
    )
    title = serializers.CharField(
        max_length=255,
        help_text="Titre de la notification"
    )
    body = serializers.CharField(
        max_length=500,
        help_text="Corps du message de la notification"
    )
    data = serializers.DictField(
        required=False,
        help_text="Données personnalisées à envoyer avec la notification"
    )
    image_url = serializers.URLField(
        required=False,
        help_text="URL de l'image à afficher (optionnel)"
    )

class ReadingReminderSerializer(serializers.Serializer):
    """
    Serializer pour l'envoi de rappels de lecture
    """
    user_id = serializers.IntegerField(
        min_value=1,
        help_text="ID de l'utilisateur à qui envoyer le rappel"
    )
    reading_plan_id = serializers.CharField(
        max_length=100,
        help_text="Identifiant du plan de lecture"
    )
    day_number = serializers.IntegerField(
        min_value=1,
        help_text="Numéro du jour dans le plan de lecture"
    )
    chapter = serializers.CharField(
        max_length=200,
        help_text="Chapitre ou passage à lire (ex: 'Jean 3:1-21')"
    )

class VerseOfDaySerializer(serializers.Serializer):
    """
    Serializer pour l'envoi du verset du jour
    """
    verse = serializers.CharField(
        max_length=1000,
        help_text="Texte du verset"
    )
    reference = serializers.CharField(
        max_length=100,
        help_text="Référence biblique (ex: 'Jean 3:16')"
    )
    topic = serializers.CharField(
        max_length=100,
        default='verse_of_day',
        help_text="Topic Firebase (par défaut: verse_of_day)"
    )

class CoupleNotificationSerializer(serializers.Serializer):
    """
    Serializer pour l'envoi de notifications de couple
    """
    couple_id = serializers.CharField(
        max_length=100,
        help_text="Identifiant du couple"
    )
    partner_user_id = serializers.IntegerField(
        min_value=1,
        help_text="ID de l'utilisateur partenaire à notifier"
    )
    action = serializers.ChoiceField(
        choices=[
            ('completed_reading', 'Lecture terminée'),
            ('started_plan', 'Plan de lecture commencé'),
            ('achievement_unlocked', 'Réussite débloquée'),
            ('prayer_request', 'Demande de prière'),
            ('encouragement', 'Encouragement'),
        ],
        help_text="Type d'action à notifier"
    )

class UpdateFCMTokenSerializer(serializers.Serializer):
    """
    Serializer pour la mise à jour du token FCM
    """
    fcm_token = serializers.CharField(
        max_length=500,
        help_text="Nouveau token FCM de l'appareil"
    )
    device_type = serializers.ChoiceField(
        choices=[('android', 'Android'), ('ios', 'iOS'), ('web', 'Web')],
        default='android',
        help_text="Type d'appareil"
    )

class BulkNotificationSerializer(serializers.Serializer):
    """
    Serializer pour l'envoi de notifications en masse
    """
    user_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        min_length=1,
        max_length=1000,
        help_text="Liste des IDs des utilisateurs à notifier (max 1000)"
    )
    title = serializers.CharField(
        max_length=255,
        help_text="Titre de la notification"
    )
    body = serializers.CharField(
        max_length=500,
        help_text="Corps du message de la notification"
    )
    data = serializers.DictField(
        required=False,
        help_text="Données personnalisées à envoyer avec la notification"
    )