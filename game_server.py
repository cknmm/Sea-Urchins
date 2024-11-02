
import asyncio, json
from collections import defaultdict
import websockets


class GameServer:

    port = 12345
    game_state = defaultdict(dict)

    @staticmethod
    async def handler(websocket, path):
        """Called when a request is received"""
        
        while True:
            try:
                message = await websocket.recv()
            except websockets.exceptions.ConnectionClosedOK:
                break
            client_state = json.loads(message)
            pid = client_state["id"]
            print(f"Data received from {pid}: {client_state}")
            try:
                GameServer.game_state[pid]['x'] = client_state['x']
                GameServer.game_state[pid]['y'] = client_state['y']
                GameServer.game_state[pid]["color"] = \
                    client_state["color"]
            except KeyError:
                pass
            await websocket.send(json.dumps(
                GameServer.game_state
            ))

    @staticmethod
    async def main():
        async with websockets.serve(GameServer.handler, 
                                    "0.0.0.0",
                                    GameServer.port):
            print(f"Listening on port {GameServer.port}")
            await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(GameServer.main())