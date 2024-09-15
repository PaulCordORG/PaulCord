import requests
import asyncio

class SlashCommand:
    def __init__(self, name, description, options=None):
        self.name = name
        self.description = description
        self.options = options or []


class CommandRegistration:
    def __init__(self, client):
        self.client = client

    async def rate_limit_sleep(self, seconds):
        await asyncio.sleep(seconds)

    async def send_request(self, method, url, headers, json=None):
        response = self.client.session.request(method, url, headers=headers, json=json)
        print(f"Request: {method} {url}, Status Code: {response.status_code}, Response: {response.text}")

        if response.status_code == 429:
            retry_after = response.json().get('retry_after', 1)
            print(f"Rate limited. Sleeping for {retry_after} seconds.")
            await self.rate_limit_sleep(retry_after)
            response = self.client.session.request(method, url, headers=headers, json=json)
            print(f"Retry Request: {method} {url}, Status Code: {response.status_code}, Response: {response.text}")

        return response
    
    def add_command_with_arguments(self, command_name, description, options):
        return {
            "name": command_name,
            "description": description,
            "options": options
        }

    async def register_commands(self):
        url = f"{self.client.base_url}/applications/{self.client.application_id}/commands"
        headers = {
            "Authorization": f"Bot {self.client.token}",
            "Content-Type": "application/json"
        }

        if not self.client.commands:
            print("No commands to register.")
            return

        for command in self.client.commands:
            payload = {
                "name": command["name"],
                "description": command["description"],
                "options": self.build_options(command["options"]),
                "integration_types": [0, 1],
                "contexts": [0, 1, 2]
            }

            print(f"Registering command: {command['name']}")
            response = await self.send_request("POST", url, headers, json=payload)
            if response.status_code != 201:
                print(f"Failed to register command '{command['name']}': {response.status_code} {response.text}")
            else:
                print(f"Command '{command['name']}' registered successfully")


    def build_command_payload(self, command):
        payload = {
            "name": command["name"],
            "description": command["description"],
            "options": []
        }

        if "options" in command:
            for option in command["options"]:
                option_payload = {
                    "type": option["type"],
                    "name": option["name"],
                    "description": option["description"]
                }

                if "options" in option:
                    option_payload["options"] = option["options"]

                payload["options"].append(option_payload)

        return payload

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
    
    async def sync_commands(self):
        url = f"{self.client.base_url}/applications/{self.client.application_id}/commands"
        headers = {
            "Authorization": f"Bot {self.client.token}",
            "Content-Type": "application/json"
        }

        response = await self.send_request("GET", url, headers)
        if response.status_code == 200:
            existing_commands = response.json()
        else:
            print("Failed to retrieve existing commands.")
            existing_commands = []

        existing_commands_dict = {cmd['name']: cmd for cmd in existing_commands}

        for command in self.client.commands:
            command_payload = {
                "name": command["name"],
                "description": command["description"],
                "options": self.build_options(command["options"]),
                "integration_types": [0, 1],
                "contexts": [0, 1, 2]
            }

            if command["name"] in existing_commands_dict:
                existing_command = existing_commands_dict[command["name"]]
                if existing_command["description"] == command["description"] and \
                   existing_command.get("options", []) == self.build_options(command["options"]):
                    continue

            print(f"Updated commands: {command['name']}")
            response = await self.send_request("POST", url, headers, json=command_payload)
            if response.status_code != 201:
                print(f"Failed to register command '{command['name']}': {response.status_code} {response.text}")
            else:
                print(f"'{command['name']}' registered!")

        
        await self.register_commands()
