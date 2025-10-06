
# apps/notifications/utils.py
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def notify_user(user_id, data):
    """
    Envoyer une notification à un utilisateur via WebSocket
    
    Args:
        user_id: ID de l'utilisateur
        data: Dictionnaire contenant les données à envoyer
    """
    channel_layer = get_channel_layer()
    
    async_to_sync(channel_layer.group_send)(
        f'user_{user_id}',
        {
            'type': 'notification_message',
            'data': data
        }
    )


def notify_multiple_users(user_ids, data):
    """Envoyer une notification à plusieurs utilisateurs"""
    for user_id in user_ids:
        notify_user(user_id, data)