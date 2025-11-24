# apps/messaging/publishers.py - Version corrigée

import json
import logging
from typing import Dict, Any
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class EventPublisher:
    """Publisher pour envoyer des événements RabbitMQ avec lazy initialization"""
    
    def __init__(self):
        self._connection = None
    
    @property
    def connection(self):
        """Lazy loading de la connexion RabbitMQ"""
        if self._connection is None:
            from .rabbitmq import get_rabbit_connection
            self._connection = get_rabbit_connection()
        return self._connection
    
    def publish_event(self, exchange: str, routing_key: str, 
                     event_data: Dict[str, Any], ensure_delivery: bool = True):
        """
        Publie un événement avec pattern outbox pour garantir la livraison
        
        Args:
            exchange: Nom de l'exchange
            routing_key: Clé de routage
            event_data: Données de l'événement
            ensure_delivery: Si True, utilise le pattern outbox
        """
        # Enrichir l'événement avec metadata
        enriched_event = self._enrich_event(event_data)
        
        try:
            # Vérifier si RabbitMQ est disponible
            if not self.connection.is_connected():
                raise ConnectionError("RabbitMQ n'est pas disponible")
            
            self._send_message(exchange, routing_key, enriched_event)
            logger.info(f"Événement publié: {exchange}/{routing_key} - {enriched_event.get('event_id')}")
            
        except Exception as e:
            logger.error(f"Échec publication: {exchange}/{routing_key} - {e}")
            
            if ensure_delivery:
                # Stocker dans outbox pour retry
                self._store_in_outbox(exchange, routing_key, enriched_event)
                logger.info(f"Événement stocké dans outbox: {enriched_event.get('event_id')}")
            else:
                raise
    
    def _enrich_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrichit l'événement avec des métadonnées"""
        return {
            'event_id': str(uuid.uuid4()),
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'klivar-platform',
            **event_data
        }
    
    def _send_message(self, exchange: str, routing_key: str, message: Dict[str, Any]):
        """Envoie le message à RabbitMQ"""
        with self.connection.get_connection() as connection:
            channel = connection.channel()
            
            # S'assurer que l'exchange existe
            channel.exchange_declare(exchange=exchange, exchange_type='topic', durable=True)
            
            # Publier avec persistance
            import pika
            channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=json.dumps(message, default=str),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Message persistant
                    content_type='application/json',
                    timestamp=int(datetime.utcnow().timestamp())
                )
            )
    
    def _store_in_outbox(self, exchange: str, routing_key: str, event_data: Dict[str, Any]):
        """Stocke l'événement dans l'outbox pour retry"""
        try:
            # Import local pour éviter les imports circulaires
            from .models import OutboxEvent
            
            OutboxEvent.objects.create(
                event_id=event_data.get('event_id'),
                exchange=exchange,
                routing_key=routing_key,
                payload=event_data,
                status='pending'
            )
        except Exception as e:
            logger.error(f"Erreur stockage outbox: {e}")

# Instance globale avec lazy initialization
_event_publisher = None

def get_event_publisher():
    """Factory function pour obtenir l'instance publisher (lazy)"""
    global _event_publisher
    if _event_publisher is None:
        _event_publisher = EventPublisher()
    return _event_publisher

# Helpers pour les événements spécifiques
class KlivarEventPublisher:
    """Publisher spécialisé pour les événements Klivar"""
    
    @staticmethod
    def publish_user_event(event_type: str, user_data: Dict[str, Any]):
        """Publie un événement utilisateur"""
        try:
            publisher = get_event_publisher()
            publisher.publish_event(
                exchange='klivar.users',
                routing_key=f'user.{event_type}',
                event_data={
                    'event_type': f'user.{event_type}',
                    'user_data': user_data
                }
            )
        except Exception as e:
            logger.error(f"Erreur publication événement utilisateur {event_type}: {e}")
    
    @staticmethod
    def publish_risk_event(event_type: str, risk_data: Dict[str, Any]):
        """Publie un événement de risque"""
        try:
            publisher = get_event_publisher()
            publisher.publish_event(
                exchange='klivar.risks',
                routing_key=f'risk.{event_type}',
                event_data={
                    'event_type': f'risk.{event_type}',
                    'risk_data': risk_data
                }
            )
        except Exception as e:
            logger.error(f"Erreur publication événement risque {event_type}: {e}")
    
    @staticmethod
    def publish_notification_event(notification_type: str, notification_data: Dict[str, Any]):
        """Publie un événement de notification"""
        try:
            publisher = get_event_publisher()
            publisher.publish_event(
                exchange='klivar.notifications',
                routing_key=f'notification.{notification_type}',
                event_data={
                    'event_type': f'notification.{notification_type}',
                    'notification_data': notification_data
                }
            )
        except Exception as e:
            logger.error(f"Erreur publication événement notification {notification_type}: {e}")
    
    @staticmethod
    def publish_audit_event(action: str, audit_data: Dict[str, Any]):
        """Publie un événement d'audit"""
        try:
            publisher = get_event_publisher()
            publisher.publish_event(
                exchange='klivar.audit',
                routing_key=f'audit.{action}',
                event_data={
                    'event_type': f'audit.{action}',
                    'audit_data': audit_data
                }
            )
        except Exception as e:
            logger.error(f"Erreur publication événement audit {action}: {e}")

# Alias pour compatibilité (deprecated)
event_publisher = property(lambda self: get_event_publisher())