from django.test import TestCase
from django.conf import settings

from kafka_app.consumers import KafkaConsumerClient
from kafka_app.producers import KafkaProducerClient
 

class KafkaIntegrationTest(TestCase):
    
    def test_send_message(self):
        """Test d'envoi d'un message"""
        topic = settings.KAFKA_TOPICS['NOTIFICATION_EVENTS']
        message = {
            'event_type': 'order.test',
            'order_id': '123',
            'test': True
        }
        
        # Envoyer le message
        result = KafkaProducerClient.send_message(topic, message, key='123')
        
        self.assertIsNotNone(result)
        self.assertEqual(result.topic, topic)
    
    def test_consumer_connection(self):
        """Test de connexion du consumer"""
        topics = [settings.KAFKA_TOPICS['NOTIFICATION_EVENTS']]
        
        consumer = KafkaConsumerClient(topics, group_id='test-group')
        
        self.assertIsNotNone(consumer.consumer)
        consumer.close()