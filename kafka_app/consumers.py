import json
import logging
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from django.conf import settings

logger = logging.getLogger(__name__)

class KafkaConsumerClient:
    def __init__(self, topics, group_id=None):
        """
        Initialise un consumer Kafka
        
        Args:
            topics (list): Liste des topics à écouter
            group_id (str, optional): ID du consumer group
        """
        self.topics = topics if isinstance(topics, list) else [topics]
        
        config = settings.KAFKA_CONSUMER_CONFIG.copy()
        if group_id:
            config['group_id'] = group_id
        else:
            config['group_id'] = settings.KAFKA_CONSUMER_GROUP
        
        try:
            self.consumer = KafkaConsumer(*self.topics, **config)
            logger.info(f"✅ Kafka Consumer initialized for topics: {self.topics}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Kafka Consumer: {e}")
            raise

    def consume_messages(self, handler_func):
        """
        Consomme les messages et les traite avec une fonction handler
        
        Args:
            handler_func (callable): Fonction qui traite chaque message
        """
        logger.info(f"🎧 Listening to topics: {self.topics}")
        
        try:
            for message in self.consumer:
                try:
                    logger.info(
                        f"📨 Received message - "
                        f"Topic: {message.topic}, "
                        f"Partition: {message.partition}, "
                        f"Offset: {message.offset}"
                    )
                    
                    # Traiter le message
                    handler_func(message)
                    
                except Exception as e:
                    logger.error(f"❌ Error processing message: {e}")
                    # Optionnel : envoyer vers un Dead Letter Queue
                    
        except KeyboardInterrupt:
            logger.info("⏹️  Consumer interrupted by user")
        except Exception as e:
            logger.error(f"❌ Consumer error: {e}")
        finally:
            self.close()

    def close(self):
        """Ferme proprement le consumer"""
        if self.consumer:
            self.consumer.close()
            logger.info("Kafka Consumer closed")


# === HANDLERS POUR DIFFÉRENTS TYPES DE MESSAGES ===

def handle_user_event(message):
    """Handler pour les événements utilisateurs"""
    data = message.value
    event_type = data.get('event_type')
    
    logger.info(f"👤 User event: {event_type}")
    
    if event_type == 'user.created':
        # Logique métier
        user_id = data.get('user_id')
        logger.info(f"New user created: {user_id}")
        
    elif event_type == 'user.updated':
        # Logique métier
        pass


def handle_order_event(message):
    """Handler pour les événements commandes"""
    data = message.value
    event_type = data.get('event_type')
    
    logger.info(f"📦 Order event: {event_type}")
    
    if event_type == 'order.created':
        order_id = data.get('order_id')
        # Envoyer notification, mettre à jour stock, etc.
        logger.info(f"New order: {order_id}")


def handle_notification_event(message):
    """Handler pour les notifications"""
    data = message.value
    notification_type = data.get('type')
    recipient = data.get('recipient')
    
    logger.info(f"🔔 Notification: {notification_type} to {recipient}")
    
    # Envoyer email, SMS, push notification, etc.