import aiohttp

class APIHelper:
    def __init__(self, client):
        self.client = client

    async def send_interaction_response(self, interaction_id, interaction_token, message=None, embed=None, ephemeral=False, components=None):
        url = f"https://discord.com/api/v10/interactions/{interaction_id}/{interaction_token}/callback"
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

        print(f"Sending interaction response: {json_data}")
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=json_data) as response:
                if response.status != 200:
                    text = await response.text()
                    print(f"Failed to send interaction response: {response.status} {text}")
                else:
                    print(f"Interaction response sent successfully for interaction {interaction_id}")
