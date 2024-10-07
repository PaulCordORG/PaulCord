import asyncio
import json
import aiohttp
import time

class WebSocketManager:
    def __init__(self, client, shard_id=0, total_shards=1):
        self.client = client
        self.shard_id = shard_id
        self.total_shards = total_shards
        self.last_ping = None
        self.ping_timestamp = None
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.reconnect_interval = 5
        self.max_heartbeat_failures = 3
        self.failed_heartbeats = 0      
        self.session = None

    async def init_session(self):
        self.session = aiohttp.ClientSession()

    async def close(self):
        if self.session:
            await self.session.close()

    async def heartbeat(self):
        while self.client.running:
            if self.client.heartbeat_interval is None:
                await asyncio.sleep(5)
                continue

            if not self.client.last_heartbeat_ack:
                self.failed_heartbeats += 1
                print(f"Shard {self.shard_id}: Heartbeat timeout ({self.failed_heartbeats}/{self.max_heartbeat_failures}). Reconnecting...")

                if self.failed_heartbeats >= self.max_heartbeat_failures:
                    if self.client.ws:
                        try:
                            await self.client.ws.close()
                        except Exception as e:
                            print(f"Shard {self.shard_id}: Error closing WebSocket connection: {e}")
                    break

            self.failed_heartbeats = 0
            self.client.last_heartbeat_ack = False
            self.ping_timestamp = time.time()

            payload = {
                "op": 1,
                "d": self.client.sequence if self.client.sequence is not None else 0
            }

            if self.client.ws:
                try:
                    await self.client.ws.send_json(payload)
                    print(f"Shard {self.shard_id}: Sending heartbeat with sequence: {self.client.sequence}")
                except Exception as e:
                    print(f"Shard {self.shard_id}: Error sending heartbeat: {e}")
                    break

            await asyncio.sleep(self.client.heartbeat_interval / 1000)


    async def reset_connection(self):
        print(f"Shard {self.shard_id}: Resetting WebSocket connection to initial state.")
        await self.close()
        
        self.reconnect_attempts = 0
        self.failed_heartbeats = 0
        self.client.sequence = None
        self.client.session_id = None
        self.client.last_heartbeat_ack = True
        self.client.ws = None

        await self.connect()

    async def connect(self):
        if self.session is None:
            await self.init_session()

        while self.client.running and (self.reconnect_attempts < self.max_reconnect_attempts or self.max_reconnect_attempts is None):
            try:
                async with self.session.ws_connect(self.client.gateway_url) as ws:
                    self.client.ws = ws
                    self.reconnect_attempts = 0
                    await self.identify()
                    asyncio.create_task(self.heartbeat())
                    print("WebSocket connected.")
                    await self.listen()

            except aiohttp.ClientConnectionError as e:
                self.reconnect_attempts += 1
                retry_delay = self.reconnect_interval * self.reconnect_attempts
                print(f"Shard {self.shard_id}: WebSocket connection error: {e}. Attempting reconnect ({self.reconnect_attempts}/{self.max_reconnect_attempts}) in {retry_delay} seconds.")
                await asyncio.sleep(retry_delay)

                if self.reconnect_attempts >= self.max_reconnect_attempts:
                    print(f"Shard {self.shard_id}: Reached max reconnect attempts. Performing full reset.")
                    await self.reset_connection()
                    return

            except Exception as e:
                print(f"Shard {self.shard_id}: Error during WebSocket connection: {e}")
                await asyncio.sleep(5)

        if self.reconnect_attempts >= self.max_reconnect_attempts:
            print("Max reconnect attempts reached. Stopping bot.")
            self.client.running = False

    async def identify(self):
        payload = {
            "op": 2,
            "d": {
                "token": self.client.token,
                "intents": self.client.intents.value,
                "properties": {
                    "$os": "linux",
                    "$browser": "PaulCLIClient",
                    "$device": "PaulCLIClient"
                },
                "shard": [self.shard_id, self.total_shards]
            }
        }
        print(f"Identify payload: {payload}")
        if self.client.ws:
            try:
                await self.client.ws.send_json(payload)
            except Exception as e:
                print(f"Shard {self.shard_id}: Error sending identify payload: {e}")

    async def listen(self):
        async for msg in self.client.ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                try:
                    data = msg.json()
                    print(f"Received WebSocket message: {data}")

                    if 'd' in data and data.get('t') == 'INTERACTION_CREATE':
                        await self.client.interaction_handler.handle_interaction(data['d'])
                    else:
                        print(f"Skipping non-interaction message: {data}")
                except Exception as e:
                    print(f"Error while processing WebSocket message: {e}")
            elif msg.type == aiohttp.WSMsgType.CLOSED:
                print("WebSocket closed.")
                break
            elif msg.type == aiohttp.WSMsgType.ERROR:
                print(f"WebSocket error: {msg.data}")
                break
