# apps/kafka_app/monitoring.py
import logging
from django.core.management.base import BaseCommand
from kafka.admin import KafkaAdminClient, NewTopic
from django.conf import settings

logger = logging.getLogger(__name__)

class KafkaMonitor:
    def __init__(self):
        self.admin_client = KafkaAdminClient(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS
        )
    
    def create_topic(self, topic_name, num_partitions=3, replication_factor=1):
        """Créer un topic"""
        topic = NewTopic(
            name=topic_name,
            num_partitions=num_partitions,
            replication_factor=replication_factor
        )
        
        try:
            self.admin_client.create_topics([topic])
            logger.info(f"✅ Topic created: {topic_name}")
        except Exception as e:
            logger.error(f"❌ Failed to create topic: {e}")
    
    def list_topics(self):
        """Lister tous les topics"""
        return self.admin_client.list_topics()
    
    def delete_topic(self, topic_name):
        """Supprimer un topic"""
        self.admin_client.delete_topics([topic_name])