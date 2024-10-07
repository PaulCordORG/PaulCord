import aiohttp

class AppEmojiManager:
    def __init__(self, client):
        self.client = client

    @classmethod
    def get_headers(cls, client):
        return {
            "Authorization": f"Bot {client.token}",
            "Content-Type": "application/json"
        }

    @classmethod
    async def list_application_emojis(cls, client):
        url = f"{client.base_url}/applications/{client.application_id}/emojis"
        async with client.session.get(url, headers=cls.get_headers(client)) as response:
            if response.status == 200:
                return await response.json()
            else:
                print(f"Failed to list emojis: {response.status} - {await response.text()}")
                return None

    @classmethod
    async def get_application_emoji(cls, client, emoji_id):
        url = f"{client.base_url}/applications/{client.application_id}/emojis/{emoji_id}"
        async with client.session.get(url, headers=cls.get_headers(client)) as response:
            if response.status == 200:
                return await response.json()
            else:
                print(f"Failed to retrieve emoji: {response.status} - {await response.text()}")
                return None

    @classmethod
    async def create_application_emoji(cls, client, name, image_data):
        url = f"{client.base_url}/applications/{client.application_id}/emojis"
        data = {
            "name": name,
            "image": image_data
        }
        async with client.session.post(url, headers=cls.get_headers(client), json=data) as response:
            if response.status == 201:
                return await response.json()
            else:
                print(f"Failed to create emoji: {response.status} - {await response.text()}")
                return None

    @classmethod
    async def modify_application_emoji(cls, client, emoji_id, name=None, image_data=None):
        url = f"{client.base_url}/applications/{client.application_id}/emojis/{emoji_id}"
        data = {}
        if name:
            data["name"] = name
        if image_data:
            data["image"] = image_data
        async with client.session.patch(url, headers=cls.get_headers(client), json=data) as response:
            if response.status == 200:
                return await response.json()
            else:
                print(f"Failed to modify emoji: {response.status} - {await response.text()}")
                return None

    @classmethod
    async def delete_application_emoji(cls, client, emoji_id):
        url = f"{client.base_url}/applications/{client.application_id}/emojis/{emoji_id}"
        async with client.session.delete(url, headers=cls.get_headers(client)) as response:
            if response.status == 204:
                print(f"Emoji {emoji_id} deleted successfully.")
                return True
            else:
                print(f"Failed to delete emoji: {response.status} - {await response.text()}")
                return False
