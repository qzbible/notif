# apps/messaging/management/commands/consume_messages.py - Version corrigée

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import logging
import signal
import sys

from messaging.consumers import get_event_consumer, setup_default_handlers

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Démarre un consumer RabbitMQ pour une queue spécifique'

    def add_arguments(self, parser):
        parser.add_argument(
            'queue', 
            type=str, 
            help='Nom de la queue à consommer'
        )
        parser.add_argument(
            '--setup-handlers',
            action='store_true',
            help='Configure automatiquement les handlers par défaut'
        )
        parser.add_argument(
            '--max-retries',
            type=int,
            default=3,
            help='Nombre maximum de tentatives de reconnexion'
        )

    def handle(self, *args, **options):
        queue_name = options['queue']
        setup_handlers = options['setup_handlers']
        max_retries = options['max_retries']
        
        # Configuration du signal handler pour arrêt propre
        def signal_handler(sig, frame):
            self.stdout.write(self.style.WARNING('⛔ Arrêt du consumer demandé...'))
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        self.stdout.write(f"🐰 Démarrage consumer pour: {queue_name}")
        
        # Vérifier la configuration RabbitMQ
        rabbitmq_config = getattr(settings, 'RABBITMQ_CONFIG', {})
        if not rabbitmq_config.get('PASSWORD'):
            raise CommandError(
                "❌ Configuration RabbitMQ manquante. "
                "Vérifiez RABBITMQ_PASSWORD dans settings."
            )
        
        retry_count = 0
        
        while retry_count <= max_retries:
            try:
                # Import lazy pour éviter l'initialisation au démarrage
                 
                
                # Obtenir le consumer
                consumer = get_event_consumer()
                
                # Configuration automatique des handlers si demandé
                if setup_handlers:
                    setup_default_handlers()
                    self.stdout.write("✅ Handlers par défaut configurés")
                
                # Vérifier qu'un handler existe pour cette queue
                if queue_name not in consumer.handlers:
                    available_queues = list(consumer.handlers.keys())
                    if available_queues:
                        raise CommandError(
                            f"❌ Aucun handler pour '{queue_name}'. "
                            f"Queues disponibles: {', '.join(available_queues)}"
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f"⚠️  Aucun handler configuré. "
                                f"Utilisation du handler par défaut pour {queue_name}"
                            )
                        )
                        # Handler par défaut qui log juste le message
                        consumer.register_handler(queue_name, self._default_handler)
                
                # Démarrer la consommation
                self.stdout.write(f"🎯 Consommation démarrée: {queue_name}")
                consumer.start_consuming(queue_name)
                
                # Si on arrive ici, c'est un arrêt normal
                break
                
            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING("⛔ Arrêt demandé par l'utilisateur"))
                break
                
            except ConnectionError as e:
                retry_count += 1
                if retry_count <= max_retries:
                    self.stdout.write(
                        self.style.WARNING(
                            f"❌ Erreur connexion (tentative {retry_count}/{max_retries}): {e}"
                        )
                    )
                    self.stdout.write(f"🔄 Nouvelle tentative dans 5 secondes...")
                    import time
                    time.sleep(5)
                else:
                    raise CommandError(f"❌ Impossible de se connecter après {max_retries} tentatives")
                    
            except Exception as e:
                logger.error(f"Erreur consumer: {e}")
                raise CommandError(f"❌ Erreur consumer: {e}")
        
        self.stdout.write(self.style.SUCCESS("✅ Consumer arrêté proprement"))

    def _default_handler(self, message):
        """Handler par défaut qui log les messages"""
        logger.info(f"📨 Message reçu (handler par défaut): {message}")
        self.stdout.write(
            f"📨 Message: {message.get('event_id', 'unknown')} - "
            f"{message.get('event_type', 'unknown')}"
        )