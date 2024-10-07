import asyncio
import aiohttp

from .Core.CommandHandler import CommandHandler
from .Core.InteractionHandler import InteractionHandler
from .Core.WebSocketManager import WebSocketManager
from .Core.APIHelper import APIHelper
from .Core.Decorators import CommandDecorator
from .Core.Intents import Intents
from .Core.CommandRegistration import CommandRegistration

class Client:
    def __init__(self, token, application_id, shard_id=0, total_shards=1, intents=Intents.default):
        self.token = token
        self.application_id = application_id
        self.shard_id = shard_id
        self.base_url = "https://discord.com/api/v10"
        self.gateway_url = "wss://gateway.discord.gg/?v=10&encoding=json"
        self.session = None
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
        self.total_shards = total_shards
        self.events = {}

        self.command_handler = CommandHandler(self)
        self.interaction_handler = InteractionHandler(self)
        self.websocket_manager = WebSocketManager(self)
        self.command_decorator = CommandDecorator(self)
        self.api_helper = APIHelper(self)
        self.command_registration = CommandRegistration(self)

    async def dispatch_event(self, event_name, *args, **kwargs):
        event_handler = self.events.get(event_name)
        if event_handler:
            print(f"Dispatching event: {event_name} with args: {args} kwargs: {kwargs}")
            try:
                await event_handler(*args, **kwargs)
            except Exception as e:
                print(f"Error while dispatching event '{event_name}': {e}")
        else:
            print(f"No handler found for event: {event_name}")

    def event(self, func):  
        self.events[func.__name__] = func
        return func

    def slash_commands(self, name=None, description=None, options=None):
        return self.command_decorator.slash_commands(name, description, options)

    async def load_commands(self):
        print("Starting command registration and sync.")
        print(f"Commands before registration: {self.commands}")

        try:
            await self.command_registration.register_commands()
            print("Commands registered successfully.")
        except Exception as e:
            print(f"Error during command registration: {e}")

        try:
            await self.command_registration.sync_commands()
            print("Commands synchronized successfully.")
        except Exception as e:
            print(f"Error during command synchronization: {e}")

    async def run_async(self):
        self.session = aiohttp.ClientSession()
        
        await self.load_commands()
        
        try:
            await self.websocket_manager.connect()
            print("WebSocket connection established.")
        except Exception as e:
            print(f"Error during WebSocket connection: {e}")

        await self.session.close()

    def run(self):
        asyncio.run(self.run_async())
