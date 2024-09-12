import asyncio
import json
import websockets

class WebSocketConnection:
    def __init__(self, client):
        self.client = client

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
        while self.client.running:
            try:
                async with websockets.connect(self.client.gateway_url) as ws:
                    self.client.ws = ws
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
                            print("Heartbeat acknowledged")

                        elif op_code == 0:
                            self.client.sequence = payload['s']
                            if event == 'READY':
                                print("Bot connected to Discord Gateway")
                                self.client.session_id = payload['d']['session_id']
                                self.client.user_id = payload['d']['user']['id']
                            elif event == 'RESUMED':
                                print("Connection to the Discord Gateway has resumed.")
                            elif event == 'INTERACTION_CREATE':
                                interaction = payload['d']
                                await self.client.handle_interaction(interaction)
                            else:
                                print(f"Unhandled event: {event}")

                        else:
                            print(f"Unhandled opcode: {op_code}")

            except Exception as e:
                print(f"Error during WebSocket connection: {e}")
                await asyncio.sleep(5)

    async def identify(self):
        payload = {
            "op": 2,
            "d": {
                "token": self.client.token,
                "intents": 8,
                "properties": {
                    "$os": "linux",
                    "$browser": "PaulCLIClient",
                    "$device": "PaulCLIClient"
                }
            }
        }
        print("Sending identify payload")
        if self.client.ws:
            try:
                await self.client.ws.send(json.dumps(payload))
            except Exception as e:
                print(f"Error sending identify payload: {e}")
