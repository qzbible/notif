import signal
import sys
from django.core.management.base import BaseCommand
from django.conf import settings

from kafka_app.consumers import KafkaConsumerClient, handle_notification_event, handle_order_event, handle_user_event
# from apps.kafka_app.consumers import (
#     KafkaConsumerClient,
#     handle_user_event,
#     handle_order_event,
#     handle_notification_event
# )

class Command(BaseCommand):
    help = 'Run Kafka consumer'

    def add_arguments(self, parser):
        parser.add_argument(
            '--topic',
            type=str,
            help='Topic to consume (user_events, order_events, notification_events, all)',
            default='all'
        )
        parser.add_argument(
            '--group',
            type=str,
            help='Consumer group ID',
            default=None
        )

    def handle(self, *args, **options):
        topic_arg = options['topic']
        group_id = options['group']

        # Mapping des topics et handlers
        topic_handlers = {
            'user_events': (
                [settings.KAFKA_TOPICS['USER_EVENTS']],
                handle_user_event
            ),
            'order_events': (
                [settings.KAFKA_TOPICS['ORDER_EVENTS']],
                handle_order_event
            ),
            'notification_events': (
                [settings.KAFKA_TOPICS['NOTIFICATION_EVENTS']],
                handle_notification_event
            ),
            'all': (
                list(settings.KAFKA_TOPICS.values()),
                self.handle_all_events
            )
        }

        if topic_arg not in topic_handlers:
            self.stdout.write(
                self.style.ERROR(f'Invalid topic: {topic_arg}')
            )
            return

        topics, handler = topic_handlers[topic_arg]

        self.stdout.write(
            self.style.SUCCESS(f'Starting Kafka consumer for: {topics}')
        )

        # Gestion du signal d'arrêt
        def signal_handler(sig, frame):
            self.stdout.write(
                self.style.WARNING('\n⏹️  Stopping consumer...')
            )
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Démarrer le consumer
        consumer = KafkaConsumerClient(topics, group_id=group_id)
        consumer.consume_messages(handler)

    def handle_all_events(self, message):
        """Router les messages vers le bon handler"""
        topic = message.topic
        
        handlers = {
            settings.KAFKA_TOPICS['USER_EVENTS']: handle_user_event,
            settings.KAFKA_TOPICS['ORDER_EVENTS']: handle_order_event,
            settings.KAFKA_TOPICS['NOTIFICATION_EVENTS']: handle_notification_event,
        }
        
        handler = handlers.get(topic)
        if handler:
            handler(message)
        else:
            self.stdout.write(
                self.style.WARNING(f'No handler for topic: {topic}')
            )