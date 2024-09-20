import asyncio
import requests

from PaulCord.Utils.CommandRegistration import CommandRegistration
from PaulCord.Utils.WebSocketConnection import WebSocketConnection
from PaulCord.Utils.Decorators import CommandDecorator, ComponentHandlerDecorator
from PaulCord.Utils.Intents import Intents

class Client:
    def __init__(self, token, application_id, intents=Intents.default):
        self.token = token
        self.application_id = application_id
        self.base_url = "https://discord.com/api/v10"
        self.gateway_url = "wss://gateway.discord.gg/?v=10&encoding=json"
        self.session = requests.Session()
        self.ws = None
        self.sequence = None
        self.heartbeat_interval = None
        self.running = True
        self.commands = []
        self.component_handlers = {}
        self.last_heartbeat_ack = True
        self.session_id = None
        self.reconnect_attempts = 0
        self.intents = intents
        self.events = {}

        self.command_registration = CommandRegistration(self)
        self.websocket_connection = WebSocketConnection(self)
        self.command_decorator = CommandDecorator(self)
        self.component_handler_decorator = ComponentHandlerDecorator(self)

    def event(self, func):  
        self.events[func.__name__] = func
        return func

    def slash_commands(self, name=None, description=None):
        return self.command_decorator.slash_commands(name, description)

    def handle_component(self, interaction, custom_id):
        handler = self.component_handler_decorator.component_handlers.get(custom_id)
        if handler:
            handler(self, interaction)
        else:
            print(f"No handler found for component with custom_id: {custom_id}")
            self.send_interaction_response(interaction["id"], interaction["token"], message="No handler for this component.")

    async def handle_interaction(self, interaction):
        interaction_type = interaction['type']
        custom_id = interaction['data'].get('custom_id', '')

        if interaction_type == 2: 
            command_name = interaction['data']['name']
            command = next((cmd for cmd in self.commands if cmd['name'] == command_name), None)
            if command:
                await command['func'](self, interaction)
            else:
                await self.send_interaction_response(interaction["id"], interaction["token"], "Unknown command")

        elif interaction_type == 3:
            print(f"Handling component with custom_id: {custom_id}")
            handler = self.component_handler_decorator.component_handlers.get(custom_id)
            if handler:
                await handler(self, interaction)
            else:
                print(f"No handler found for component with custom_id: {custom_id}")
                await self.send_interaction_response(interaction["id"], interaction["token"], "No handler for this component.")

        elif interaction_type == 5:
            await self.handle_modal(interaction, custom_id)

        else:
            await self.send_interaction_response(interaction["id"], interaction["token"], "Unknown interaction type")

    async def dispatch_event(self, event_name, *args, **kwargs):
        if event_name in self.events:
            await self.events[event_name](*args, **kwargs)
        else:
            print(f"No handler for event: {event_name}")



    def send_interaction_response(self, interaction_id, interaction_token, message=None, embed=None, ephemeral=False, components=None):
        url = f"{self.base_url}/interactions/{interaction_id}/{interaction_token}/callback"
        json_data = {
            "type": 4, 
            "data": {}
        }
    
        if message:
            json_data["data"]["content"] = message
            if ephemeral:
                json_data["data"]["flags"] = 64
    
        if embed:
            json_data["data"]["embeds"] = [embed]
    
        if components:
            json_data["data"]["components"] = components
    
        response = self.session.post(url, json=json_data)
        if response.status_code != 200:
            print(f"Failed to send interaction response: {response.status_code} {response.text}")
        else:
            print("Interaction response sent successfully")


    async def main(self):
        print("Starting command registration and sync.")
        print(f"Commands before registration: {self.commands}")
    
        try:
            await self.command_registration.register_commands()
            print("Commands registered.")
        except Exception as e:
            print(f"Error during command registration: {e}")

        try:
            await self.command_registration.sync_commands()
            print("Commands synchronized.")
        except Exception as e:
            print(f"Error during command synchronization: {e}")

        try:
            await self.websocket_connection.connect()
            print("WebSocket connection established.")
        except Exception as e:
            print(f"Error during WebSocket connection: {e}")


    def run(self):
        asyncio.run(self.main())
