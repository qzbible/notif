import json
import logging
from kafka import KafkaProducer
from kafka.errors import KafkaError
from django.conf import settings

logger = logging.getLogger(__name__)

class KafkaProducerClient:
    _instance = None
    _producer = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._producer is None:
            try:
                self._producer = KafkaProducer(**settings.KAFKA_PRODUCER_CONFIG)
                logger.info("✅ Kafka Producer initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Kafka Producer: {e}")
                raise

    def send_message(self, topic, message, key=None):
        """
        Envoie un message à Kafka
        
        Args:
            topic (str): Nom du topic
            message (dict): Message à envoyer
            key (str, optional): Clé de partition
        
        Returns:
            RecordMetadata: Métadonnées du message envoyé
        """
        try:
            future = self._producer.send(
                topic=topic,
                value=message,
                key=key
            )
            
            # Attendre la confirmation (bloquant)
            record_metadata = future.get(timeout=10)
            
            logger.info(
                f"✅ Message sent to {topic} - "
                f"Partition: {record_metadata.partition}, "
                f"Offset: {record_metadata.offset}"
            )
            
            return record_metadata
            
        except KafkaError as e:
            logger.error(f"❌ Kafka error: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Failed to send message: {e}")
            raise

    def send_async(self, topic, message, key=None, callback=None):
        """
        Envoie un message de manière asynchrone
        """
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
        self._producer.flush()

    def close(self):
        """Ferme proprement le producer"""
        if self._producer:
            self._producer.close()
            logger.info("Kafka Producer closed")


# Instance globale
kafka_producer = KafkaProducerClient()