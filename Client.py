import asyncio
import requests

from PaulCord.CommandRegistration import CommandRegistration
from PaulCord.WebSocketConnection import WebSocketConnection
from PaulCord.Decorators import CommandDecorator, ComponentHandlerDecorator

class Client:
    def __init__(self, token, application_id):
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

        self.command_registration = CommandRegistration(self)
        self.websocket_connection = WebSocketConnection(self)
        self.command_decorator = CommandDecorator(self)
        self.component_handler_decorator = ComponentHandlerDecorator(self)

    def slash_commands(self, name=None, description=None):
        return self.command_decorator.slash_commands(name, description)

    def component_handler(self, custom_id=None):
        return self.component_handler_decorator.component_handler(custom_id)

    def handle_interaction(self, interaction):
        interaction_type = interaction['type']
        custom_id = interaction['data'].get('custom_id', '')

        if interaction_type == 2:   
            command_name = interaction['data']['name']
            print(f"Command received: {command_name}")
            command = next((cmd for cmd in self.commands if cmd['name'] == command_name), None)
            if command:
                command['func'](self, interaction)
            else:
                self.send_interaction_response(interaction["id"], interaction["token"], "Unknown command")

        elif interaction_type == 3:
            self.handle_component(interaction, custom_id)

        elif interaction_type == 5: 
            self.handle_modal(interaction, custom_id)

        else:
            self.send_interaction_response(interaction["id"], interaction["token"], "Unknown interaction type")

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
        await self.command_registration.register_commands()
        await self.command_registration.sync_commands()
        await self.websocket_connection.connect()


    def run(self):
        asyncio.run(self.main())
