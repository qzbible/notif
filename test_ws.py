import asyncio
import websockets
import json

async def test():
    uri = "ws://localhost:8083/ws/notifications/"
    
    try:
        async with websockets.connect(uri) as ws:
            print("Connecté!")
            
            # Recevoir le message de bienvenue
            msg = await ws.recv()
            print(f"Reçu: {msg}")
            
            # Envoyer un ping
            await ws.send(json.dumps({"type": "ping", "timestamp": 12345}))
            
            # Recevoir le pong
            msg = await ws.recv()
            print(f"Reçu: {msg}")
            
    except Exception as e:
        print(f"Erreur: {e}")

asyncio.run(test())