import aiohttp
import asyncio

class SlashCommand:
    def __init__(self, name, description, options=None, integration_types=False, version=1):
        self.name = name
        self.description = description
        self.options = options or []
        self.integration_types = integration_types
        self.version = version

class CommandRegistration:
    def __init__(self, client):
        self.client = client

    async def rate_limit_sleep(self, seconds):
        await asyncio.sleep(seconds)

    async def send_request(self, method, url, headers, json=None):
        async with self.client.session.request(method, url, headers=headers, json=json) as response:
            status_code = response.status
            response_text = await response.text()
            print(f"Request: {method} {url}, Status Code: {status_code}, Response: {response_text}")

            if status_code == 429:
                retry_after = (await response.json()).get('retry_after', 1)
                print(f"Rate limited. Sleeping for {retry_after} seconds.")
                await self.rate_limit_sleep(retry_after)
                return await self.send_request(method, url, headers, json)

            if response.content_type == 'application/json':
                return status_code, await response.json()
            else:
                return status_code, response_text

    async def get_existing_commands(self):
        url = f"{self.client.base_url}/applications/{self.client.application_id}/commands"
        headers = {
            "Authorization": f"Bot {self.client.token}"
        }

        status_code, response_data = await self.send_request("GET", url, headers)
        if status_code == 200:
            return response_data
        else:
            print("Failed to retrieve existing commands.")
            return []

    def commands_are_equal(self, existing_command, new_command):
        return (
            existing_command['name'] == new_command['name'] and
            existing_command['description'] == new_command['description'] and
            existing_command.get('options', []) == new_command.get('options', []) and
            existing_command.get('integration_types', []) == new_command.get('integration_types', []) and
            existing_command.get('version', 1) == new_command.get('version', 1)
        )

    async def register_commands(self):
        url = f"{self.client.base_url}/applications/{self.client.application_id}/commands"
        headers = {
            "Authorization": f"Bot {self.client.token}",
            "Content-Type": "application/json"
        }

        existing_commands = await self.get_existing_commands()

        for command in self.client.commands:
            payload = {
                "name": command["name"],
                "description": command["description"],
                "options": self.build_options(command.get("options", [])),
                "contexts": [0, 1, 2],
                "integration_types": [0, 1] if command.get("integration_types", False) else [0]
            }

            existing_command = next((cmd for cmd in existing_commands if cmd['name'] == command["name"]), None)
            if existing_command and self.commands_are_equal(existing_command, command):
                print(f"Command '{command['name']}' is already up to date. Skipping registration.")
                continue

            print(f"Registering or updating command: {command['name']}")
            status_code, response_data = await self.send_request("POST", url, headers, json=payload)
            if status_code not in [200, 201]:
                print(f"Failed to register command '{command['name']}': {status_code} {response_data}")
            else:
                print(f"Command '{command['name']}' updated or registered successfully")

    async def delete_command(self, command_id):
        url = f"{self.client.base_url}/applications/{self.client.application_id}/commands/{command_id}"
        headers = {
            "Authorization": f"Bot {self.client.token}"
        }

        status_code, response_data = await self.send_request("DELETE", url, headers)
        if status_code == 204:
            print(f"Command {command_id} deleted successfully.")
        else:
            print(f"Failed to delete command {command_id}: {status_code} {response_data}")

    async def sync_commands(self):
        existing_commands = await self.get_existing_commands()
        existing_commands_dict = {cmd['name']: cmd for cmd in existing_commands}

        for command in self.client.commands:
            command_payload = {
                "name": command["name"],
                "description": command["description"],
                "options": self.build_options(command.get("options", [])),
                "integration_types": [0, 1] if command.get("integration_types", False) else [0],
                "contexts": [0, 1, 2]
            }

            if command["name"] in existing_commands_dict:
                existing_command = existing_commands_dict[command["name"]]
                if self.commands_are_equal(existing_command, command):
                    continue

            print(f"Updating or registering command: {command['name']}")
            await self.send_request("POST", f"{self.client.base_url}/applications/{self.client.application_id}/commands", {
                "Authorization": f"Bot {self.client.token}",
                "Content-Type": "application/json"
            }, json=command_payload)

        for existing_command in existing_commands:
            if existing_command["name"] not in {cmd["name"] for cmd in self.client.commands}:
                print(f"Deleting command: {existing_command['name']}")
                await self.delete_command(existing_command['id'])

        await self.register_commands()

    def build_options(self, options):
        discord_options = []
        for option in options:
            discord_option = {
                "type": option["type"],
                "name": option["name"],
                "description": option["description"],
                "required": option.get("required", False)
            }
            discord_options.append(discord_option)
        return discord_options
