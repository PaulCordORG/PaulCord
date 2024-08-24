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
        
        for command in self.client.commands:
            payload = {
                "name": command["name"],
                "description": command["description"]
            }
            print(f"Registering command: {command['name']}")
            response = await self.send_request("POST", url, headers, json=payload)
            if response.status_code != 201:
                print(f"Failed to register command '{command['name']}': {response.status_code} {response.text}")
            else:
                print(f"Command '{command['name']}' registered successfully")


    async def sync_commands(self):
        url = f"{self.client.base_url}/applications/{self.client.application_id}/commands"
        headers = {
            "Authorization": f"Bot {self.client.token}",
            "Content-Type": "application/json"
        }

        response = await self.send_request("GET", url, headers)
        if response.status_code == 200:
            commands = response.json()
            for cmd in commands:
                cmd_id = cmd['id']
                delete_url = f"{url}/{cmd_id}"
                delete_response = await self.send_request("DELETE", delete_url, headers)
                if delete_response.status_code != 204:
                    print(f"Failed to delete command '{cmd_id}': {delete_response.status_code} {delete_response.text}")

        await self.register_commands()
