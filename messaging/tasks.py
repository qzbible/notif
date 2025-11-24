# apps/messaging/tasks.py - Version corrigée

from celery import shared_task
from django.utils import timezone
from django.db import models
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

@shared_task
def process_outbox_events():
    """Tâche Celery pour traiter les événements outbox en attente"""
    
    try:
        # Import local pour éviter les problèmes d'initialisation
        from .models import OutboxEvent
        from .publishers import get_event_publisher
        
        # Récupérer les événements à traiter
        events = OutboxEvent.objects.filter(
            status__in=['pending', 'failed'],
            attempts__lt=models.F('max_attempts')
        ).filter(
            models.Q(next_retry_at__isnull=True) | 
            models.Q(next_retry_at__lte=timezone.now())
        )[:100]  # Traiter par batch
        
        processed = 0
        failed = 0
        
        # Obtenir le publisher de manière lazy
        publisher = get_event_publisher()
        
        for event in events:
            try:
                # Marquer comme en cours
                event.status = 'processing'
                event.attempts += 1
                event.save(update_fields=['status', 'attempts'])
                
                # Tenter l'envoi
                publisher._send_message(
                    exchange=event.exchange,
                    routing_key=event.routing_key,
                    message=event.payload
                )
                
                # Marquer comme terminé
                event.status = 'completed'
                event.save(update_fields=['status'])
                
                processed += 1
                logger.info(f"Événement outbox traité: {event.event_id}")
                
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Échec traitement outbox {event.event_id}: {error_msg}")
                
                # Programmer retry ou marquer comme échec final
                if event.attempts >= event.max_attempts:
                    event.status = 'failed'
                    event.error_message = error_msg
                else:
                    event.status = 'pending'
                    # Backoff exponentiel: 2^attempts minutes
                    retry_delay = timedelta(minutes=min(2**event.attempts, 60))
                    event.next_retry_at = timezone.now() + retry_delay
                
                event.error_message = error_msg
                event.save()
                failed += 1
        
        logger.info(f"Traitement outbox terminé: {processed} traités, {failed} échecs")
        return {'processed': processed, 'failed': failed}
        
    except Exception as e:
        logger.error(f"Erreur traitement batch outbox: {e}")
        return {'error': str(e)}

@shared_task
def cleanup_old_outbox_events():
    """Nettoie les anciens événements outbox"""
    
    try:
        from .models import OutboxEvent
        
        # Supprimer les événements terminés de plus de 7 jours
        cutoff_date = timezone.now() - timedelta(days=7)
        
        deleted_count, _ = OutboxEvent.objects.filter(
            status='completed',
            created_at__lt=cutoff_date
        ).delete()
        
        logger.info(f"Nettoyage outbox: {deleted_count} événements supprimés")
        return {'deleted': deleted_count}
        
    except Exception as e:
        logger.error(f"Erreur nettoyage outbox: {e}")
        return {'error': str(e)}

@shared_task
def test_rabbitmq_connection():
    """Tâche pour tester la connexion RabbitMQ"""
    
    try:
        from .rabbitmq import get_rabbit_connection
        
        connection = get_rabbit_connection()
        
        if connection.is_connected():
            logger.info("✅ Test connexion RabbitMQ: SUCCESS")
            return {'status': 'connected', 'message': 'RabbitMQ is available'}
        else:
            logger.warning("❌ Test connexion RabbitMQ: FAILED")
            return {'status': 'disconnected', 'message': 'RabbitMQ is not available'}
            
    except Exception as e:
        logger.error(f"❌ Erreur test RabbitMQ: {e}")
        return {'status': 'error', 'message': str(e)}

@shared_task
def send_test_message(exchange='test', routing_key='test', message='Hello World'):
    """Tâche pour envoyer un message de test"""
    
    try:
        from .publishers import get_event_publisher
        
        publisher = get_event_publisher()
        publisher.publish_event(
            exchange=exchange,
            routing_key=routing_key,
            event_data={'test_message': message, 'timestamp': timezone.now().isoformat()}
        )
        
        logger.info(f"✅ Message test envoyé: {exchange}/{routing_key}")
        return {'status': 'sent', 'exchange': exchange, 'routing_key': routing_key}
        
    except Exception as e:
        logger.error(f"❌ Erreur envoi message test: {e}")
        return {'status': 'error', 'message': str(e)}

@shared_task
def retry_failed_outbox_events():
    """Force le retry des événements outbox en échec"""
    
    try:
        from .models import OutboxEvent
        
        # Remettre en pending les événements failed avec peu de tentatives
        updated = OutboxEvent.objects.filter(
            status='failed',
            attempts__lt=3
        ).update(
            status='pending',
            next_retry_at=timezone.now()
        )
        
        logger.info(f"🔄 {updated} événements outbox remis en pending")
        return {'retried': updated}
        
    except Exception as e:
        logger.error(f"❌ Erreur retry outbox: {e}")
        return {'error': str(e)}