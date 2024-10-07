import asyncio

class CommandHandler:
    def __init__(self, client):
        self.client = client

    async def register_commands(self):
        pass

    async def sync_commands(self):
        pass

    async def reload_command(self, command_name, guild_id=None):
        command = next((cmd for cmd in self.client.commands if cmd['name'] == command_name), None)
        if command:
            await self.client.api_helper.update_guild_command(command, guild_id)
        else:
            print(f"Command '{command_name}' not found.")
