# apps/messaging/consumers.py - Version corrigée avec lazy initialization

import json
import logging
from typing import Dict, Any, Callable

logger = logging.getLogger(__name__)

class EventConsumer:
    """Consumer pour recevoir des événements RabbitMQ avec lazy initialization"""
    
    def __init__(self):
        self._connection = None
        self.handlers = {}
    
    @property
    def connection(self):
        """Lazy loading de la connexion RabbitMQ"""
        if self._connection is None:
            from .rabbitmq import get_rabbit_connection
            self._connection = get_rabbit_connection()
        return self._connection
    
    def register_handler(self, queue_name: str, handler: Callable[[Dict[str, Any]], None]):
        """Enregistre un handler pour une queue"""
        self.handlers[queue_name] = handler
    
    def start_consuming(self, queue_name: str):
        """Démarre la consommation d'une queue"""
        if queue_name not in self.handlers:
            raise ValueError(f"Aucun handler enregistré pour {queue_name}")
        
        handler = self.handlers[queue_name]
        
        try:
            with self.connection.get_connection() as connection:
                channel = connection.channel()
                
                # S'assurer que la queue existe
                channel.queue_declare(queue=queue_name, durable=True)
                
                # Configuration QoS
                channel.basic_qos(prefetch_count=1)
                
                def callback(ch, method, properties, body):
                    try:
                        message = json.loads(body.decode('utf-8'))
                        logger.info(f"Message reçu sur {queue_name}: {message.get('event_id', 'unknown')}")
                        
                        # Traiter le message
                        handler(message)
                        
                        # Acquitter
                        ch.basic_ack(delivery_tag=method.delivery_tag)
                        logger.debug(f"Message acquitté: {message.get('event_id', 'unknown')}")
                        
                    except json.JSONDecodeError as e:
                        logger.error(f"Erreur décodage JSON {queue_name}: {e}")
                        # Rejeter définitivement les messages mal formés
                        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                    except Exception as e:
                        logger.error(f"Erreur traitement message {queue_name}: {e}")
                        # Rejeter et requeue (ou DLQ après max attempts)
                        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                
                channel.basic_consume(queue=queue_name, on_message_callback=callback)
                
                logger.info(f"🐰 Démarrage consommation: {queue_name}")
                try:
                    channel.start_consuming()
                except KeyboardInterrupt:
                    logger.info("⛔ Arrêt demandé par l'utilisateur")
                    channel.stop_consuming()
                except Exception as e:
                    logger.error(f"❌ Erreur dans le consumer: {e}")
                    raise
                    
        except Exception as e:
            logger.error(f"❌ Erreur démarrage consumer {queue_name}: {e}")
            raise

# Instance globale avec lazy initialization
_event_consumer = None

def get_event_consumer():
    """Factory function pour obtenir l'instance consumer (lazy)"""
    global _event_consumer
    if _event_consumer is None:
        _event_consumer = EventConsumer()
    return _event_consumer

# Handlers spécialisés pour Klivar
def handle_user_created(message: Dict[str, Any]):
    """Handler pour événement utilisateur créé"""
    try:
        user_data = message.get('user_data', {})
        logger.info(f"📧 Traitement utilisateur créé: {user_data.get('email')}")
        
        # Import local pour éviter les imports circulaires
        from apps.notifications.tasks import send_welcome_email
        
        # Déclencher email de bienvenue
        send_welcome_email.delay(
            email=user_data.get('email'),
            username=user_data.get('username'),
            organization=user_data.get('organization_id')
        )
        
        logger.info(f"✅ Email de bienvenue planifié pour {user_data.get('email')}")
        
    except Exception as e:
        logger.error(f"❌ Erreur traitement utilisateur créé: {e}")
        raise

def handle_user_updated(message: Dict[str, Any]):
    """Handler pour événement utilisateur mis à jour"""
    try:
        user_data = message.get('user_data', {})
        changes = message.get('changes', {})
        
        logger.info(f"🔄 Utilisateur mis à jour: {user_data.get('email')}")
        logger.debug(f"Changements: {changes}")
        
        # Ici vous pouvez ajouter la logique spécifique
        # Par exemple, invalider le cache utilisateur
        
        logger.info(f"✅ Mise à jour utilisateur traitée pour {user_data.get('email')}")
        
    except Exception as e:
        logger.error(f"❌ Erreur traitement utilisateur mis à jour: {e}")
        raise

def handle_risk_escalated(message: Dict[str, Any]):
    """Handler pour escalation de risque"""
    try:
        risk_data = message.get('risk_data', {})
        logger.info(f"⚠️  Escalation de risque: {risk_data.get('risk_id')}")
        
        # Import local pour éviter les imports circulaires
        from apps.notifications.tasks import send_risk_escalation_alert
        
        # Alerter les responsables
        send_risk_escalation_alert.delay(
            risk_id=risk_data.get('risk_id'),
            severity=risk_data.get('severity'),
            organization_id=risk_data.get('organization_id')
        )
        
        logger.info(f"✅ Alerte escalation envoyée pour risque {risk_data.get('risk_id')}")
        
    except Exception as e:
        logger.error(f"❌ Erreur traitement escalation risque: {e}")
        raise

def handle_audit_log(message: Dict[str, Any]):
    """Handler pour logs d'audit"""
    try:
        audit_data = message.get('audit_data', {})
        logger.info(f"📝 Log audit: {audit_data.get('action')}")
        
        # Import local pour éviter les imports circulaires
        from apps.risks.models import AuditLog
        
        # Créer entrée audit
        AuditLog.objects.create(
            event_id=message.get('event_id'),
            action=audit_data.get('action'),
            user_id=audit_data.get('user_id'),
            resource_type=audit_data.get('resource_type'),
            resource_id=audit_data.get('resource_id'),
            organization_id=audit_data.get('organization_id'),
            metadata=audit_data
        )
        
        logger.info(f"✅ Log audit créé: {message.get('event_id')}")
        
    except Exception as e:
        logger.error(f"❌ Erreur traitement log audit: {e}")
        raise

def handle_email_notification(message: Dict[str, Any]):
    """Handler pour notifications email"""
    try:
        notification_data = message.get('notification_data', {})
        logger.info(f"📧 Notification email: {notification_data.get('recipient')}")
        
        # Import local
        from apps.notifications.services import EmailService
        
        email_service = EmailService()
        email_service.send_email(
            to=notification_data.get('recipient'),
            subject=notification_data.get('subject'),
            template=notification_data.get('template'),
            context=notification_data.get('context', {})
        )
        
        logger.info(f"✅ Email envoyé à {notification_data.get('recipient')}")
        
    except Exception as e:
        logger.error(f"❌ Erreur envoi email: {e}")
        raise

# Configuration des handlers par défaut
def setup_default_handlers():
    """Configure les handlers par défaut"""
    consumer = get_event_consumer()
    
    # Enregistrer les handlers
    consumer.register_handler('user.created', handle_user_created)
    consumer.register_handler('user.updated', handle_user_updated)
    consumer.register_handler('risk.escalated', handle_risk_escalated)
    consumer.register_handler('audit.logged', handle_audit_log)
    consumer.register_handler('email.queue', handle_email_notification)
    
    logger.info("✅ Handlers par défaut configurés")

# Alias pour compatibilité (deprecated)
event_consumer = property(lambda self: get_event_consumer())