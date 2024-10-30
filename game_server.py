
import asyncio, json
from collections import defaultdict
import websockets


class GameServer:

    port = 8675
    game_state = defaultdict(dict)

    @staticmethod
    async def handler(websocket, path):
        """Called when a request is received"""
        
        message = await websocket.recv()
        client_state = json.loads(message)
        pid = client_state["id"]
        GameServer.game_state[pid]['x'] = client_state['y']
        GameServer.game_state[pid]['y'] = client_state['y']
        await websocket.send(json.dumps(
            GameServer.game_state
        ))