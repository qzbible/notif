# notification/consumers.py

import json
import hashlib
from channels.generic.websocket import AsyncWebsocketConsumer
from urllib.parse import parse_qs

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Connexion WebSocket avec récupération des paramètres"""
        
        print(f"🔍 Nouvelle connexion WebSocket")
        
        # Récupérer les paramètres de la query string
        query_string = self.scope.get('query_string', b'').decode()
        query_params = parse_qs(query_string)
        
        # Extraire user_name et room_group
        self.user_name = query_params.get('user_name', ['Anonyme'])[0]
        self.room_group = query_params.get('room_group', [None])[0]
        
        print(f"   Utilisateur: {self.user_name}")
        print(f"   Groupe demandé: {self.room_group}")
        
        # Créer le nom du groupe
        if self.room_group:
            # Utiliser le groupe fourni (déjà sanitizé côté frontend)
            self.room_group_name = self.room_group[:99]  # Limiter à 99 caractères
        else:
            # Fallback: créer un groupe unique
            channel_hash = hashlib.md5(self.channel_name.encode()).hexdigest()[:16]
            self.room_group_name = f'user_test_{channel_hash}'
        
        print(f"   Groupe final: {self.room_group_name}")
        
        # Rejoindre le groupe
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # Accepter la connexion
        await self.accept()
        
        print(f"✅ {self.user_name} connecté au groupe {self.room_group_name}")
        
        # Envoyer un message de confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': f'Bienvenue {self.user_name}',
            'user_name': self.user_name,
            'room_group': self.room_group_name,
        }))
        
        # Notifier les autres membres du groupe
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_joined',
                'user_name': self.user_name,
                'channel_name': self.channel_name,
            }
        )
    
    async def disconnect(self, close_code):
        """Déconnexion WebSocket"""
        print(f"🔴 {self.user_name} déconnecté (code: {close_code})")
        
        if hasattr(self, 'room_group_name'):
            # Notifier les autres avant de partir
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_left',
                    'user_name': self.user_name,
                }
            )
            
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """Recevoir un message du client"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            print(f"📨 {self.user_name} -> {message_type}")
            
            if message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': data.get('timestamp'),
                }))
            
            elif message_type == 'send_message':
                # Diffuser à tout le groupe
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message_id': data.get('message_id'),
                        'conversation_id': data.get('conversation_id'),
                        'content': data.get('content'),
                        'sender_name': self.user_name,
                    }
                )
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
    
    # Handlers pour les événements du groupe
    async def user_joined(self, event):
        """Un utilisateur a rejoint"""
        if event.get('channel_name') != self.channel_name:
            await self.send(text_data=json.dumps({
                'type': 'user_joined',
                'user_name': event['user_name'],
                'message': f"{event['user_name']} a rejoint",
            }))
    
    async def user_left(self, event):
        """Un utilisateur est parti"""
        await self.send(text_data=json.dumps({
            'type': 'user_left',
            'user_name': event['user_name'],
            'message': f"{event['user_name']} est parti",
        }))
    
    async def chat_message(self, event):
        """Diffuser un message de chat - Ne pas renvoyer à l'expéditeur"""
        # Ne pas s'envoyer son propre message
        if event['sender_name'] != self.user_name:
            await self.send(text_data=json.dumps({
                'type': 'new_message',
                'message_id': event['message_id'],
                'conversation_id': event['conversation_id'],
                'content': event['content'],
                'sender_name': event['sender_name'],
            }))

    async def user_typing(self, event):
        """Notifier qu'un utilisateur tape"""
        print("user_typing===========")
        # Ne pas s'envoyer à soi-même
        if event['user_name'] != self.user_name:
            await self.send(text_data=json.dumps({
                'type': 'user_typing',
                'user_name': event['user_name'],
                'conversation_id': event['conversation_id'],
                'is_typing': event['is_typing'],
            }))