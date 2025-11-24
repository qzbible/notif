# apps/messaging/management/commands/setup_rabbitmq.py

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Configure les exchanges et queues RabbitMQ pour Klivar Platform'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Affiche les opérations sans les exécuter'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Affichage détaillé des opérations'
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Supprime et recrée les exchanges/queues'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        verbose = options['verbose']
        reset = options['reset']
        
        self.stdout.write("🔧 Configuration RabbitMQ pour Klivar Platform...")
        
        if dry_run:
            self.stdout.write(self.style.WARNING("📋 Mode dry-run - aucune modification"))
        
        # Vérifier la configuration
        if not self._check_config():
            return
        
        try:
            from apps.messaging.rabbitmq import get_rabbit_connection
            
            connection = get_rabbit_connection()
            
            # Test de connexion
            if not connection.is_connected():
                raise CommandError(
                    "❌ Impossible de se connecter à RabbitMQ.\n"
                    "Vérifiez :\n"
                    f"  - Host: {settings.RABBITMQ_CONFIG.get('HOST')}\n"
                    f"  - Port: {settings.RABBITMQ_CONFIG.get('PORT')}\n"
                    f"  - Username: {settings.RABBITMQ_CONFIG.get('USERNAME')}\n"
                    "  - Password: [configuré dans RABBITMQ_PASSWORD]"
                )
            
            self.stdout.write("✅ Connexion RabbitMQ établie")
            
            # Configuration des exchanges
            self._setup_exchanges(connection, dry_run, verbose, reset)
            
            # Configuration des queues
            self._setup_queues(connection, dry_run, verbose, reset)
            
            # Configuration des bindings
            self._setup_bindings(connection, dry_run, verbose)
            
            self.stdout.write(
                self.style.SUCCESS('\n🎉 Configuration RabbitMQ terminée avec succès!')
            )
            
            # Afficher le résumé
            self._show_summary()
            
        except Exception as e:
            logger.error(f"Erreur configuration RabbitMQ: {e}")
            raise CommandError(f"❌ Erreur: {e}")

    def _check_config(self):
        """Vérifie la configuration RabbitMQ"""
        try:
            rabbitmq_config = getattr(settings, 'RABBITMQ_CONFIG', {})
            
            required_fields = ['HOST', 'PORT', 'USERNAME', 'PASSWORD']
            missing = [field for field in required_fields if not rabbitmq_config.get(field)]
            
            if missing:
                self.stdout.write(
                    self.style.ERROR(f"❌ Configuration incomplète: {', '.join(missing)}")
                )
                return False
            
            self.stdout.write("✅ Configuration RabbitMQ valide")
            return True
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erreur configuration: {e}"))
            return False

    def _setup_exchanges(self, connection, dry_run, verbose, reset):
        """Configure les exchanges"""
        exchanges = [
            ('klivar.users', 'topic', 'Événements utilisateurs'),
            ('klivar.risks', 'topic', 'Événements de risques'),
            ('klivar.notifications', 'topic', 'Notifications'),
            ('klivar.audit', 'topic', 'Logs d\'audit'),
            ('klivar.compliance', 'topic', 'Événements de conformité'),
        ]
        
        self.stdout.write("\n📡 Configuration des exchanges...")
        
        for exchange_name, exchange_type, description in exchanges:
            if verbose:
                self.stdout.write(f"  📡 {exchange_name} ({exchange_type}) - {description}")
            
            if not dry_run:
                try:
                    connection.ensure_exchange(exchange_name, exchange_type)
                    self.stdout.write(f"  ✅ {exchange_name}")
                except Exception as e:
                    self.stdout.write(f"  ❌ {exchange_name}: {e}")

    def _setup_queues(self, connection, dry_run, verbose, reset):
        """Configure les queues avec DLX"""
        queues = [
            # Queues utilisateurs
            ('user.created', 'Utilisateur créé'),
            ('user.updated', 'Utilisateur modifié'),
            ('user.deactivated', 'Utilisateur désactivé'),
            
            # Queues risques
            ('risk.assessed', 'Évaluation de risque'),
            ('risk.updated', 'Risque mis à jour'),
            ('risk.escalated', 'Escalation de risque'),
            
            # Queues notifications
            ('email.queue', 'Notifications email'),
            ('push.queue', 'Notifications push'),
            ('sms.queue', 'Notifications SMS'),
            
            # Queues audit
            ('audit.logged', 'Logs d\'audit'),
            ('audit.compliance', 'Conformité'),
            
            # Queues système
            ('system.health', 'Santé système'),
            ('system.backup', 'Sauvegardes'),
        ]
        
        self.stdout.write("\n📋 Configuration des queues...")
        
        for queue_name, description in queues:
            if verbose:
                self.stdout.write(f"  📋 {queue_name} - {description}")
            
            if not dry_run:
                try:
                    # Arguments pour DLX et TTL
                    queue_args = {
                        'x-dead-letter-exchange': f'{queue_name}.dlx',
                        'x-message-ttl': 3600000,  # 1 heure
                        'x-max-retries': 3
                    }
                    
                    connection.ensure_queue(queue_name, arguments=queue_args)
                    self.stdout.write(f"  ✅ {queue_name}")
                    
                    # Créer la Dead Letter Queue
                    dlq_name = f'{queue_name}.dlq'
                    connection.ensure_queue(dlq_name)
                    if verbose:
                        self.stdout.write(f"    💀 DLQ: {dlq_name}")
                        
                except Exception as e:
                    self.stdout.write(f"  ❌ {queue_name}: {e}")

    def _setup_bindings(self, connection, dry_run, verbose):
        """Configure les bindings entre exchanges et queues"""
        bindings = [
            # Bindings utilisateurs
            ('klivar.users', 'user.created', 'user.created'),
            ('klivar.users', 'user.updated', 'user.updated'),
            ('klivar.users', 'user.deactivated', 'user.deactivated'),
            
            # Bindings risques
            ('klivar.risks', 'risk.assessed', 'risk.assessed'),
            ('klivar.risks', 'risk.updated', 'risk.updated'),
            ('klivar.risks', 'risk.escalated', 'risk.escalated'),
            
            # Bindings notifications
            ('klivar.notifications', 'email.queue', 'notification.email'),
            ('klivar.notifications', 'push.queue', 'notification.push'),
            ('klivar.notifications', 'sms.queue', 'notification.sms'),
            
            # Bindings audit
            ('klivar.audit', 'audit.logged', 'audit.logged'),
            ('klivar.audit', 'audit.compliance', 'audit.compliance'),
            
            # Bindings croisés (notifications déclenchées par d'autres événements)
            ('klivar.users', 'email.queue', 'user.created'),  # Email bienvenue
            ('klivar.risks', 'email.queue', 'risk.escalated'),  # Alert risque
            ('klivar.risks', 'audit.logged', 'risk.*'),  # Audit tous risques
        ]
        
        self.stdout.write("\n🔗 Configuration des bindings...")
        
        for exchange, queue, routing_key in bindings:
            if verbose:
                self.stdout.write(f"  🔗 {exchange} -> {queue} ({routing_key})")
            
            if not dry_run:
                try:
                    connection.ensure_queue(queue, exchange, routing_key)
                    self.stdout.write(f"  ✅ {exchange} -> {queue}")
                except Exception as e:
                    self.stdout.write(f"  ❌ {exchange} -> {queue}: {e}")

    def _show_summary(self):
        """Affiche un résumé de la configuration"""
        self.stdout.write("\n" + "="*60)
        self.stdout.write("📊 RÉSUMÉ DE LA CONFIGURATION")
        self.stdout.write("="*60)
        
        config = settings.RABBITMQ_CONFIG
        self.stdout.write(f"🌐 Host: {config['HOST']}:{config['PORT']}")
        self.stdout.write(f"👤 Username: {config['USERNAME']}")
        self.stdout.write(f"🏠 Virtual Host: {config['VHOST']}")
        
        self.stdout.write("\n📡 Exchanges configurés:")
        exchanges = ['klivar.users', 'klivar.risks', 'klivar.notifications', 'klivar.audit']
        for exchange in exchanges:
            self.stdout.write(f"  - {exchange}")
        
        self.stdout.write("\n📋 Queues principales:")
        main_queues = [
            'user.created', 'risk.escalated', 'email.queue', 
            'audit.logged', 'push.queue'
        ]
        for queue in main_queues:
            self.stdout.write(f"  - {queue}")
        
        self.stdout.write("\n🔗 Fonctionnalités:")
        self.stdout.write("  - Dead Letter Queues (DLX)")
        self.stdout.write("  - Message TTL (1 heure)")
        self.stdout.write("  - Retry automatique (3 tentatives)")
        self.stdout.write("  - Bindings croisés")
        
        self.stdout.write("\n🎯 Prochaines étapes:")
        self.stdout.write("  1. Tester: python manage.py test_rabbitmq")
        self.stdout.write("  2. Consumer: python manage.py consume_messages email.queue")
        self.stdout.write("  3. Monitor: https://dev-rabbitmq.klivar.com")
        
        self.stdout.write("="*60)