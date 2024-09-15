import requests
import asyncio

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
            payload = self.build_command_payload(command)
            print(f"Registering command: {command['name']}")
            
            response = await self.send_request("POST", url, headers, json=payload)
            if response.status_code in [200, 201]:
                print(f"Command '{command['name']}' registered successfully")
            else:
                print(f"Failed to register command '{command['name']}': {response.status_code} {response.text}")

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
            return

        existing_commands_dict = {cmd['name']: cmd for cmd in existing_commands}

        for command in self.client.commands:
            command_payload = self.build_command_payload(command)

            if command["name"] in existing_commands_dict:
                existing_command = existing_commands_dict[command["name"]]
                if existing_command["description"] == command["description"] and \
                   existing_command.get("options", []) == command_payload["options"]:
                    continue 

            print(f"Updating or registering command: {command['name']}")
            response = await self.send_request("POST", url, headers, json=command_payload)
            if response.status_code in [200, 201]:
                print(f"Command '{command['name']}' updated or registered successfully")
            else:
                print(f"Failed to update or register command '{command['name']}': {response.status_code} {response.text}")

    def build_command_payload(self, command):
        payload = {
            "name": command["name"],
            "description": command["description"],
            "options": self.build_options(command["options"]) if "options" in command else []
        }
        return payload

    def build_options(self, options):
        discord_options = []
        for option in options:
            discord_option = {
                "type": option.get("type", 1),
                "name": option["name"],
                "description": option["description"]
            }
            if "options" in option:
                discord_option["options"] = self.build_options(option["options"])
            discord_options.append(discord_option)
        return discord_options
