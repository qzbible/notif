# services/firebase_notification_service_v1.py

import json
import requests
from django.conf import settings
from typing import Dict, List, Optional
import logging
from google.oauth2 import service_account
from google.auth.transport.requests import Request
import time

logger = logging.getLogger(__name__)



class FirebaseNotificationService:
    """
    Service pour envoyer des notifications Firebase avec la nouvelle API v1
    """
    
    def __init__(self):
        self.project_id = getattr(settings, 'FIREBASE_PROJECT_ID', 'evangelists-febb9')
        self.service_account_path = getattr(settings, 'FIREBASE_SERVICE_ACCOUNT_PATH', None)
        self.fcm_url = f'https://fcm.googleapis.com/v1/projects/{self.project_id}/messages:send'
        
        # Cache pour le token d'accès
        self._access_token = None
        self._token_expiry = 0
        
        if not self.service_account_path:
            logger.warning("FIREBASE_SERVICE_ACCOUNT_PATH non configuré, utilisation de l'ancienne API")
            # Fallback vers l'ancienne API si pas de service account
            self.server_key = getattr(settings, 'FIREBASE_SERVER_KEY', None)
            self.legacy_fcm_url = 'https://fcm.googleapis.com/fcm/send'
    
    def _get_access_token(self) -> str:
        """
        Obtient un token d'accès OAuth2 pour Firebase v1 API
        """
        # Vérifier si le token est encore valide
        if self._access_token and time.time() < self._token_expiry:
            return self._access_token
        
        try:
            # Charger les credentials du service account
            credentials = service_account.Credentials.from_service_account_file(
                self.service_account_path,
                scopes=['https://www.googleapis.com/auth/firebase.messaging']
            )
            
            # Refresher le token
            request = Request()
            credentials.refresh(request)
            
            self._access_token = credentials.token
            # Token valide pour ~3600 secondes, on garde 5 minutes de marge
            self._token_expiry = time.time() + 3300
            
            return self._access_token
            
        except Exception as e:
            logger.error(f"Erreur lors de l'obtention du token OAuth2: {e}")
            raise Exception(f"Impossible d'obtenir le token d'accès: {e}")
    
    def send_to_token(self, 
                     fcm_token: str, 
                     title: str, 
                     body: str, 
                     data: Optional[Dict] = None,
                     image_url: Optional[str] = None) -> Dict:
        """
        Envoie une notification à un token FCM spécifique (API v1)
        """
        
        # Construire le payload v1
        message = {
            "token": fcm_token,
            "notification": {
                "title": title,
                "body": body
            }
        }
        
        # Ajouter l'image si fournie
        if image_url:
            message["notification"]["image"] = image_url
        
        # Ajouter les données personnalisées
        if data:
            # Firebase v1 nécessite que toutes les valeurs data soient des strings
            string_data = {k: str(v) for k, v in data.items()}
            message["data"] = string_data
        
        # Configuration spécifique Android/iOS
        message["android"] = {
            "priority": "high",
            "notification": {
                "sound": "default",
                "click_action": "FLUTTER_NOTIFICATION_CLICK"
            }
        }
        
        message["apns"] = {
            "payload": {
                "aps": {
                    "sound": "default"
                }
            }
        }
        
        payload = {"message": message}
 
        
        return self._send_request_v1(payload)
    
    def send_to_topic(self, 
                     topic: str, 
                     title: str, 
                     body: str, 
                     data: Optional[Dict] = None,
                     image_url: Optional[str] = None) -> Dict:
        """
        Envoie une notification à un topic Firebase (API v1)
        """
        
        message = {
            "topic": topic,
            "notification": {
                "title": title,
                "body": body
            }
        }
        
        if image_url:
            message["notification"]["image"] = image_url
        
        if data:
            string_data = {k: str(v) for k, v in data.items()}
            message["data"] = string_data
        
        # Configuration Android/iOS
        message["android"] = {
            "priority": "high",
            "notification": {
                "sound": "default"
            }
        }
        
        message["apns"] = {
            "payload": {
                "aps": {
                    "sound": "default"
                }
            }
        }
        
        payload = {"message": message}
        
        return self._send_request_v1(payload)
    
    def send_to_multiple_tokens(self, 
                               fcm_tokens: List[str], 
                               title: str, 
                               body: str, 
                               data: Optional[Dict] = None,
                               image_url: Optional[str] = None) -> Dict:
        """
        Envoie une notification à plusieurs tokens (batch avec v1)
        """
        success_count = 0
        failure_count = 0
        errors = []
        
        for token in fcm_tokens:
            result = self.send_to_token(token, title, body, data, image_url)
            if result['success']:
                success_count += 1
            else:
                failure_count += 1
                errors.append(f"Token {token[:20]}...: {result['error']}")
        
        return {
            'success': failure_count == 0,
            'message': f"{success_count} envois réussis, {failure_count} échecs",
            'success_count': success_count,
            'failure_count': failure_count,
            'errors': errors
        }
    
    def _send_request_v1(self, payload: Dict) -> Dict:
        """
        Envoie la requête à Firebase FCM v1 API
        """
        try:
            # Obtenir le token d'accès
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
            
            logger.info(f"Notification v1 envoyée avec succès: {result}")
            return {
                'success': True,
                'message_id': result.get('name'),  # v1 utilise 'name' au lieu de 'message_id'
                'response': result
            }
            
        except requests.exceptions.HTTPError as e:
            error_detail = e.response.text if e.response else str(e)
            logger.error(f"Erreur HTTP lors de l'envoi v1: {e} - {error_detail}")
            return {
                'success': False,
                'error': f"HTTP {e.response.status_code}: {error_detail}",
                'response': None
            }
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de la notification v1: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': None
            }
    
    def _send_request_legacy(self, payload: Dict) -> Dict:
        """
        Fallback vers l'ancienne API si service account non configuré
        """
        if not self.server_key:
            return {
                'success': False,
                'error': 'Ni service account ni server key configurés',
                'response': None
            }
        
        headers = {
            'Authorization': f'key={self.server_key}',
            'Content-Type': 'application/json',
        }
        
        try:
            response = requests.post(
                self.legacy_fcm_url,
                headers=headers,
                data=json.dumps(payload),
                timeout=10
            )
            
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"Notification legacy envoyée: {result}")
            return {
                'success': True,
                'message_id': result.get('multicast_id') or result.get('message_id'),
                'response': result
            }
            
        except Exception as e:
            logger.error(f"Erreur legacy API: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': None
            }
    
    # 📱 Méthodes spécifiques à BibleCouple (mises à jour pour v1)
    
    def send_reading_reminder(self, 
                             fcm_token: str, 
                             reading_plan_id: str, 
                             day_number: int,
                             chapter: str,
                             user_name: str = ""):
        """
        Envoie un rappel de lecture quotidienne
        """
        title = "📖 Temps de lecture" + (f" {user_name}" if user_name else "")
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
        """
        Envoie le verset du jour à un topic
        """
        title = "✨ Verset du jour"
        body = f"{verse[:80]}..." if len(verse) > 80 else verse
        
        data = {
            "type": "verse_of_day",
            "verse": verse,
            "reference": reference,
            "screen": "verse_of_day"
        }
        
        return self.send_to_topic(topic, title, body, data)
    
    def send_couple_notification(self, 
                                couple_id: str, 
                                partner_name: str, 
                                action: str,
                                partner_fcm_token: str):
        """
        Envoie une notification de couple
        """
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
    
    def send_achievement_notification(self, 
                                    fcm_token: str, 
                                    achievement_id: str, 
                                    achievement_name: str):
        """
        Envoie une notification de réussite débloquée
        """
        title = "🏆 Félicitations !"
        body = f"Vous avez débloqué: {achievement_name}"
        
        data = {
            "type": "achievement_unlocked",
            "achievement_id": achievement_id,
            "achievement_name": achievement_name,
            "screen": "achievements"
        }
        
        return self.send_to_token(fcm_token, title, body, data)
    
    def _create_temp_service_account(self, json_content):
        """Crée un fichier temporaire depuis la variable d'environnement"""
        import tempfile
        import json
        
        service_account_data = json.loads(json_content)
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(service_account_data, f)
            return f.name


# Singleton instance
firebase_service = FirebaseNotificationService()