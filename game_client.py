
import asyncio, json, random, time
from collections import defaultdict
import threading as t
import websockets


class GameClient:

    uri = ""
    server_socket = None
    game_state = defaultdict(dict)
    local_client_state = dict()
    pid = ""
    #the next amt of time to wait before retrying
    retry_pattern = lambda x: (0.01+x) if x < 3 else 0.001
    latency = -1 #in ms (-1 indicates retrying connection
    #-2 means connected but data is not being transferred yet)
    stop_flag = False #used to stop the indefinite retry loop
    sync_flag = False #ask the local client to refresh

    def __init__(self, uri, pid=None, retry_pattern=None):
        GameClient.uri = uri
        if pid is None:
            pid = str(random.randint(int(1e9), int(1e12)))
        GameClient.pid = pid
        if retry_pattern is not None:
            GameClient.retry_pattern = retry_pattern

    @staticmethod
    async def connect(ping_delay=20):
        #set retry status in latency var
        GameClient.latency = -1
        try:
            GameClient.server_socket = \
            await websockets.connect(GameClient.uri,
                                     ping_interval=ping_delay/1000)
            GameClient.latency = -2 #set success status
        except Exception as e:
            print(f"\nError[connect]: {e}\n")
            GameClient.server_socket = None

    @staticmethod
    async def exchange_states(data=None):

        s = time.time()

        if data is None:
            message = dict(GameClient.local_client_state)
            message["id"] = GameClient.pid
        else:
            message = data
        await GameClient.server_socket.send(
            json.dumps(message)
        )
        #print("Debug: Local client sent")

        recv_state = await GameClient.server_socket.recv()
        #print("Debug: Local client recv")
        recv_state = json.loads(recv_state)
        GameClient.game_state = recv_state
        GameClient.sync_flag = True #ask players to sync

        GameClient.latency = round(time.time() - s, 3) * 1000

    @staticmethod
    async def retry_exchange(timeout=None):

        time_taken = 0
        wait_time = 0.001 #start waiting from 1 sec

        while (timeout is None or time_taken + wait_time \
            <= timeout) and not(GameClient.stop_flag):

            try:
                await GameClient.exchange_states()
                #reset time vars
                time_taken = 0
                wait_time = 0.001
            except Exception as e:
                print(f"\nError[retry]: {e}\nRetrying in \
{wait_time*1000} ms...")
                await asyncio.sleep(wait_time)
                time_taken += wait_time
                wait_time = GameClient.retry_pattern(
                    wait_time
                )

                await GameClient.connect()
            print("Debug:", GameClient.latency, "ms")
        else:
            if GameClient.stop_flag:
                try:
                    await GameClient.server_socket.close()
                except:
                    pass