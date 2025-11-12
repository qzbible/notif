import json
import logging
from kafka import KafkaProducer
from kafka.errors import KafkaError, NoBrokersAvailable
from django.conf import settings

logger = logging.getLogger(__name__)


class KafkaProducerClient:
    """
    Singleton Kafka Producer avec initialisation lazy
    """
    _instance = None
    _producer = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _init_producer(self):
        """Initialise le producer de manière lazy"""
        if self._initialized:
            return
        
        # Vérifier si Kafka est activé
        if not getattr(settings, 'KAFKA_ENABLED', True):
            logger.info("ℹ️ Kafka is disabled in settings")
            self._initialized = False
            return
        
        try:
            bootstrap_servers = getattr(settings, 'KAFKA_BOOTSTRAP_SERVERS', ['localhost:9092'])
            
            logger.info(f"🔄 Attempting to connect to Kafka: {bootstrap_servers}")
            
            self._producer = KafkaProducer(
                bootstrap_servers=bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                acks='all',
                retries=3,
                request_timeout_ms=10000,
                api_version_auto_timeout_ms=5000,
            )
            self._initialized = True
            logger.info("✅ Kafka Producer initialized successfully")
            
        except NoBrokersAvailable:
            logger.warning("⚠️ Kafka brokers not available. Producer disabled.")
            self._initialized = False
        except Exception as e:
            logger.error(f"❌ Failed to initialize Kafka Producer: {e}")
            self._initialized = False

    def send_message(self, topic, message, key=None):
        """
        Envoie un message à Kafka
        
        Returns:
            RecordMetadata ou None si Kafka n'est pas disponible
        """
        # Initialiser le producer si nécessaire
        if not self._initialized:
            self._init_producer()
        
        # Si toujours pas initialisé, logger et retourner
        if not self._initialized:
            logger.warning(f"⚠️ Kafka not available. Message not sent to {topic}")
            return None
        
        try:
            future = self._producer.send(topic=topic, value=message, key=key)
            record_metadata = future.get(timeout=10)
            
            logger.info(
                f"✅ Message sent to {topic} - "
                f"Partition: {record_metadata.partition}, "
                f"Offset: {record_metadata.offset}"
            )
            
            return record_metadata
            
        except KafkaError as e:
            logger.error(f"❌ Kafka error: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Failed to send message: {e}")
            return None

    def send_async(self, topic, message, key=None, callback=None):
        """Envoie un message de manière asynchrone"""
        if not self._initialized:
            self._init_producer()
        
        if not self._initialized:
            logger.warning(f"⚠️ Kafka not available. Async message not sent to {topic}")
            return

        def on_send_success(record_metadata):
            logger.info(
                f"✅ Async message sent - Topic: {record_metadata.topic}, "
                f"Partition: {record_metadata.partition}, Offset: {record_metadata.offset}"
            )
            if callback:
                callback(record_metadata)

        def on_send_error(excp):
            logger.error(f"❌ Async send failed: {excp}")

        try:
            self._producer.send(topic, value=message, key=key).add_callback(
                on_send_success
            ).add_errback(on_send_error)
        except Exception as e:
            logger.error(f"❌ Failed to send async message: {e}")

    def flush(self):
        """Force l'envoi de tous les messages en attente"""
        if self._producer:
            self._producer.flush()

    def close(self):
        """Ferme proprement le producer"""
        if self._producer:
            self._producer.close()
            logger.info("Kafka Producer closed")
            self._initialized = False


# Instance globale (mais PAS encore initialisée)
kafka_producer = KafkaProducerClient()
 