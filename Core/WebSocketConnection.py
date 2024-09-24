import asyncio
import json
import websockets
import time

class WebSocketConnection:
    def __init__(self, client):
        self.client = client
        self.last_ping = None
        self.ping_timestamp = None
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.reconnect_interval = 5

    async def heartbeat(self):
        while self.client.running:
            if self.client.heartbeat_interval is None:
                await asyncio.sleep(5)
                continue

            if not self.client.last_heartbeat_ack:
                print("Heartbeat timeout. Reconnecting...")
                if self.client.ws:
                    try:
                        await self.client.ws.close()
                    except Exception as e:
                        print(f"Error closing WebSocket connection: {e}")
                break

            self.client.last_heartbeat_ack = False
            self.ping_timestamp = time.time()
            payload = {
                "op": 1,
                "d": self.client.sequence if self.client.sequence is not None else 0
            }
            if self.client.ws:
                try:
                    await self.client.ws.send(json.dumps(payload))
                except Exception as e:
                    print(f"Error sending heartbeat: {e}")
                    break
            print(f"Sending heartbeat with sequence: {self.client.sequence}")
            await asyncio.sleep(self.client.heartbeat_interval / 1000)

    async def connect(self):
        while self.client.running and self.reconnect_attempts < self.max_reconnect_attempts:
            try:
                async with websockets.connect(self.client.gateway_url) as ws:
                    self.client.ws = ws
                    self.reconnect_attempts = 0
                    await self.identify()
                    asyncio.create_task(self.heartbeat())

                    async for message in ws:
                        payload = json.loads(message)
                        op_code = payload.get('op')
                        event = payload.get('t', 'UNKNOWN')

                        if op_code == 10:
                            self.client.heartbeat_interval = payload['d']['heartbeat_interval']
                            print(f"Received HELLO, heartbeat_interval set to: {self.client.heartbeat_interval}")

                        elif op_code == 11:
                            self.client.last_heartbeat_ack = True
                            if self.ping_timestamp:
                                self.last_ping = (time.time() - self.ping_timestamp) * 1000
                                print(f"Ping: {self.last_ping:.2f} ms")
                            print("Heartbeat acknowledged")

                        if event == 'READY':
                            print("Bot connected to Discord Gateway")
                            self.client.session_id = payload['d']['session_id']
                            self.client.user_id = payload['d']['user']['id']
                            await self.client.dispatch_event('on_ready')
                        elif event == 'PRESENCE_UPDATE':
                            await self.client.dispatch_event('on_presence_update', payload['d'])
                        elif event == 'GUILD_CREATE':
                            await self.client.dispatch_event('on_guild_create', payload['d'])
                        elif event == 'MESSAGE_CREATE':
                            await self.client.dispatch_event('on_message', payload['d'])
                        elif event == 'MESSAGE_UPDATE':
                            await self.client.dispatch_event('on_message_update', payload['d'])
                        elif event == 'MESSAGE_DELETE':
                            await self.client.dispatch_event('on_message_delete', payload['d'])
                        elif event == 'GUILD_ROLE_CREATE':
                            await self.client.dispatch_event('on_guild_role_create', payload['d'])
                        elif event == 'GUILD_ROLE_UPDATE':
                            await self.client.dispatch_event('on_guild_role_update', payload['d'])
                        elif event == 'GUILD_ROLE_DELETE':
                            await self.client.dispatch_event('on_guild_role_delete', payload['d'])
                        elif event == 'INTERACTION_CREATE':
                            interaction = payload['d']
                            await self.client.handle_interaction(interaction)
                        else:
                            if event:
                                await self.client.dispatch_event(event.lower(), payload['d'])
                            else:
                                print("Received event with no name:", payload)

            except (websockets.exceptions.ConnectionClosed, websockets.exceptions.InvalidStatusCode) as e:
                self.reconnect_attempts += 1
                print(f"WebSocket connection error: {e}. Attempting reconnect ({self.reconnect_attempts}/{self.max_reconnect_attempts})")
                await asyncio.sleep(self.reconnect_interval * self.reconnect_attempts)
            except Exception as e:
                print(f"Error during WebSocket connection: {e}")
                await asyncio.sleep(5)

        if self.reconnect_attempts >= self.max_reconnect_attempts:
            print("Max reconnect attempts reached. Stopping bot.")
            self.client.running = False

    async def identify(self):
        payload = {
            "op": 2,
            "d": {
                "token": self.client.token,
                "intents": self.client.intents,
                "properties": {
                    "$os": "linux",
                    "$browser": "PaulCLIClient",
                    "$device": "PaulCLIClient"
                }
            }
        }
        print("Sending identify payload with intents:", self.client.intents)
        if self.client.ws:
            try:
                await self.client.ws.send(json.dumps(payload))
            except Exception as e:
                print(f"Error sending identify payload: {e}")
