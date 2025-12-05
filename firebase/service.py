# services/firebase_notification_service_individual.py

import os
import logging
from google.oauth2 import service_account
from google.auth.transport.requests import Request
import requests
import time
import json

logger = logging.getLogger(__name__)

class FirebaseNotificationService:
    """
    Service Firebase utilisant des variables d'environnement individuelles
    Plus fiable avec Docker Compose
    """
    
    def __init__(self):
        self.project_id = 'evangelists-febb9'
        self.fcm_url = f'https://fcm.googleapis.com/v1/projects/{self.project_id}/messages:send'
        
        # Cache pour le token d'accès
        self._access_token = None
        self._token_expiry = 0
        self._credentials = None
        
        # Initialiser depuis variables individuelles
        self._init_credentials_from_individual_vars()
    
    def _init_credentials_from_individual_vars(self):
        """Utilise directement les variables Vault individuelles"""
        
        # Récupérer toutes les variables Firebase
        firebase_vars = {
            'type': os.getenv('FIREBASE_TYPE', 'service_account'),
            'project_id': os.getenv('FIREBASE_PROJECT_ID', self.project_id),
            'private_key_id': os.getenv('FIREBASE_PRIVATE_KEY_ID'),
            'private_key': os.getenv('FIREBASE_PRIVATE_KEY', ''),
            'client_email': os.getenv('FIREBASE_CLIENT_EMAIL'),
            'client_id': os.getenv('FIREBASE_CLIENT_ID'),
            'auth_uri': os.getenv('FIREBASE_AUTH_URI', 'https://accounts.google.com/o/oauth2/auth'),
            'token_uri': os.getenv('FIREBASE_TOKEN_URI', 'https://oauth2.googleapis.com/token'),
            'auth_provider_x509_cert_url': os.getenv('FIREBASE_AUTH_PROVIDER_X509_CERT_URL', 'https://www.googleapis.com/oauth2/v1/certs'),
            'client_x509_cert_url': os.getenv('FIREBASE_CLIENT_X509_CERT_URL'),
            'universe_domain': os.getenv('FIREBASE_UNIVERSE_DOMAIN', 'googleapis.com')
        }
        
        # Nettoyer la clé privée (remplacer \\n par \n)
        if firebase_vars['private_key']:
            firebase_vars['private_key'] = firebase_vars['private_key'].replace('\\n', '\n')
        
        # Valider les champs critiques
        required_fields = ['private_key_id', 'private_key', 'client_email', 'client_id']
        missing_fields = [field for field in required_fields if not firebase_vars.get(field)]
        
        if missing_fields:
            logger.error(f"❌ Variables Firebase manquantes: {missing_fields}")
            # Afficher les variables disponibles (masquées)
            for key, value in firebase_vars.items():
                if value and 'private_key' not in key:
                    logger.info(f"✅ {key}: {value}")
                elif value:
                    logger.info(f"✅ {key}: ***MASQUÉ***")
                else:
                    logger.warning(f"❌ {key}: MANQUANT")
            
            raise ValueError(f"Variables Firebase manquantes: {missing_fields}")
        
        try:
            # Créer les credentials Google
            self._credentials = service_account.Credentials.from_service_account_info(
                firebase_vars,
                scopes=['https://www.googleapis.com/auth/firebase.messaging']
            )
            
            logger.info("✅ Firebase credentials chargées depuis variables individuelles")
            logger.info(f"📧 Client email: {firebase_vars.get('client_email')}")
            logger.info(f"🆔 Project ID: {firebase_vars.get('project_id')}")
            
        except Exception as e:
            logger.error(f"❌ Erreur création credentials Firebase: {e}")
            logger.error(f"❌ Type: {type(e).__name__}")
            raise
    
    def _get_access_token(self) -> str:
        """Obtient un token d'accès OAuth2"""
        if not self._credentials:
            raise Exception("Firebase credentials non configurées")
        
        # Vérifier si le token est encore valide
        if self._access_token and time.time() < self._token_expiry:
            return self._access_token
        
        try:
            request = Request()
            self._credentials.refresh(request)
            
            self._access_token = self._credentials.token
            self._token_expiry = time.time() + 3300  # 55 minutes
            
            logger.debug("🔑 Token d'accès Firebase renouvelé")
            return self._access_token
            
        except Exception as e:
            logger.error(f"❌ Erreur renouvellement token: {e}")
            raise
    
    def send_to_token(self, fcm_token: str, title: str, body: str, data: dict = None, image_url: str = None) -> dict:
        """Envoie une notification à un token FCM"""
        message = {
            "token": fcm_token,
            "notification": {"title": title, "body": body}
        }
        
        if image_url:
            message["notification"]["image"] = image_url
        
        if data:
            message["data"] = {k: str(v) for k, v in data.items()}
        
        # Configuration Android/iOS
        message["android"] = {
            "priority": "high",
            "notification": {
                "sound": "default",
                "click_action": "FLUTTER_NOTIFICATION_CLICK"
            }
        }
        
        message["apns"] = {
            "payload": {"aps": {"sound": "default"}}
        }
        
        return self._send_request_v1({"message": message})
    
    def send_to_topic(self, topic: str, title: str, body: str, data: dict = None, image_url: str = None) -> dict:
        """Envoie une notification à un topic"""
        message = {
            "topic": topic,
            "notification": {"title": title, "body": body}
        }
        
        if image_url:
            message["notification"]["image"] = image_url
        
        if data:
            message["data"] = {k: str(v) for k, v in data.items()}
        
        message["android"] = {"priority": "high", "notification": {"sound": "default"}}
        message["apns"] = {"payload": {"aps": {"sound": "default"}}}
        
        return self._send_request_v1({"message": message})
    
    def _send_request_v1(self, payload: dict) -> dict:
        """Envoie la requête à Firebase"""
        try:
            access_token = self._get_access_token()
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
            }
            
            response = requests.post(
                self.fcm_url,
                headers=headers,
                data=json.dumps(payload),
                timeout=10
            )
            
            response.raise_for_status()
            result = response.json()
            
            logger.info("✅ Notification Firebase envoyée avec succès")
            return {
                'success': True,
                'message_id': result.get('name'),
                'response': result
            }
            
        except requests.exceptions.HTTPError as e:
            error_detail = e.response.text if e.response else str(e)
            logger.error(f"❌ Erreur HTTP Firebase: {error_detail}")
            return {
                'success': False,
                'error': f"HTTP {e.response.status_code if e.response else 'Unknown'}: {error_detail}",
                'response': None
            }
        except Exception as e:
            logger.error(f"❌ Erreur Firebase: {e}")
            return {'success': False, 'error': str(e), 'response': None}
    
    # Méthodes BibleCouple
    def send_reading_reminder(self, fcm_token: str, reading_plan_id: str, day_number: int, chapter: str, user_name: str = ""):
        """Rappel de lecture BibleCouple"""
        title = f"📖 Temps de lecture{' ' + user_name if user_name else ''}"
        body = f"Il est temps de lire {chapter} - Jour {day_number}"
        data = {
            "type": "reading_reminder",
            "reading_plan_id": reading_plan_id,
            "day_number": str(day_number),
            "chapter": chapter,
            "screen": "reading"
        }
        return self.send_to_token(fcm_token, title, body, data)
    
    def send_verse_of_day(self, topic: str, verse: str, reference: str):
        """Verset du jour"""
        title = "✨ Verset du jour"
        body = f"{verse[:80]}..." if len(verse) > 80 else verse
        data = {
            "type": "verse_of_day",
            "verse": verse,
            "reference": reference,
            "screen": "verse_of_day"
        }
        return self.send_to_topic(topic, title, body, data)
    
    def send_couple_notification(self, couple_id: str, partner_name: str, action: str, partner_fcm_token: str):
        """Notification de couple"""
        action_messages = {
            'completed_reading': f"{partner_name} a terminé sa lecture quotidienne",
            'started_plan': f"{partner_name} a commencé un nouveau plan de lecture", 
            'achievement_unlocked': f"{partner_name} a débloqué une nouvelle réussite"
        }
        
        title = "💑 Activité de couple"
        body = action_messages.get(action, f"{partner_name} a une nouvelle activité")
        data = {
            "type": "couple_notification",
            "couple_id": couple_id,
            "partner_name": partner_name,
            "action": action,
            "screen": "couple_activity"
        }
        return self.send_to_token(partner_fcm_token, title, body, data)


# Singleton
firebase_service = FirebaseNotificationService()