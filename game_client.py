
import asyncio, json, random
from collections import defaultdict
import threading as t
import websockets


class GameClient:

    uri = ""
    server_socket = None
    game_state = defaultdict(dict)
    pid = ""
    retry_pattern = lambda x: 2*x #the next amt of time to wait
    latency = 0.0 #in ms    

    def __init__(self, pid=None, retry_pattern=None):
        if pid is None:
            pid = str(random.randint(int(1e9), int(1e12)))
        GameClient.pid = pid
        if retry_pattern is not None:
            GameClient.retry_pattern = retry_pattern

    @staticmethod
    async def connect(ping_delay=20):
        try:
            GameClient.server_socket = \
            await websockets.connect(GameClient.uri,
                                     ping_interval=ping_delay)
        except:
            GameClient.server_socket = None

    @staticmethod
    async def exchange_states():

        message = GameClient.game_state[
            GameClient.pid
        ]
        message["id"] = GameClient.pid
        await GameClient.server_socket.send(
            json.dumps(message)
        )

        recv_state = await GameClient.server_socket.recv()
        recv_state = json.loads(recv_state)
        GameClient.game_state = recv_state

    