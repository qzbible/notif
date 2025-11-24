import pika
import json
import logging
from typing import Dict, Any, Optional, Callable
from contextlib import contextmanager
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)

class RabbitMQConnection:
    """Gestionnaire de connexions RabbitMQ avec lazy initialization"""
    
    def __init__(self):
        self._connection = None
        self._channel = None
        self._connection_params = None
        self._setup_connection_params()
    
    def _setup_connection_params(self):
        """Configure les paramètres de connexion"""
        config = getattr(settings, 'RABBITMQ_CONFIG', {})
        
        if not config.get('PASSWORD'):
            raise ImproperlyConfigured("RABBITMQ_PASSWORD must be set in settings")
        
        self._connection_params = pika.ConnectionParameters(
            host=config.get('HOST', 'localhost'),
            port=config.get('PORT', 5672),
            virtual_host=config.get('VHOST', '/'),
            credentials=pika.PlainCredentials(
                username=config.get('USERNAME', 'guest'),
                password=config['PASSWORD']
            ),
            heartbeat=config.get('HEARTBEAT', 600),
            blocked_connection_timeout=config.get('BLOCKED_CONNECTION_TIMEOUT', 300),
        )
    
    @contextmanager
    def get_connection(self):
        """Context manager pour obtenir une connexion RabbitMQ"""
        connection = None
        try:
            connection = pika.BlockingConnection(self._connection_params)
            yield connection
        except Exception as e:
            logger.error(f"Erreur connexion RabbitMQ: {e}")
            raise
        finally:
            if connection and not connection.is_closed:
                try:
                    connection.close()
                except Exception as e:
                    logger.warning(f"Erreur fermeture connexion: {e}")
    
    def ensure_exchange(self, exchange_name: str, exchange_type: str = 'topic'):
        """S'assure que l'exchange existe"""
        with self.get_connection() as connection:
            channel = connection.channel()
            channel.exchange_declare(
                exchange=exchange_name, 
                exchange_type=exchange_type, 
                durable=True
            )
    
    def ensure_queue(self, queue_name: str, exchange_name: str = None, 
                    routing_key: str = None, **queue_args):
        """S'assure que la queue existe et est bindée si nécessaire"""
        with self.get_connection() as connection:
            channel = connection.channel()
            
            # Déclarer la queue
            channel.queue_declare(queue=queue_name, durable=True, arguments=queue_args)
            
            # Binder à l'exchange si spécifié
            if exchange_name and routing_key:
                channel.queue_bind(
                    exchange=exchange_name,
                    queue=queue_name,
                    routing_key=routing_key
                )

# Instance globale
rabbit_connection = RabbitMQConnection()