import requests

class EmojiManager:
    def __init__(self, client):
        self.client = client

    def get_emojis(self, guild_id):
        url = f"{self.client.base_url}/guilds/{guild_id}/emojis"
        headers = {
            "Authorization": f"Bot {self.client.token}"
        }

        response = self.client.session.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get emojis: {response.status_code} {response.text}")
            return None

    def add_emoji(self, guild_id, name, image_base64):
        url = f"{self.client.base_url}/guilds/{guild_id}/emojis"
        headers = {
            "Authorization": f"Bot {self.client.token}",
            "Content-Type": "application/json"
        }
        json_data = {
            "name": name,
            "image": image_base64
        }

        response = self.client.session.post(url, headers=headers, json=json_data)
        if response.status_code == 201:
            print(f"Successfully added emoji: {name}")
            return response.json()
        else:
            print(f"Failed to add emoji: {response.status_code} {response.text}")
            return None

    def update_emoji(self, guild_id, emoji_id, name=None, image_base64=None):
        url = f"{self.client.base_url}/guilds/{guild_id}/emojis/{emoji_id}"
        headers = {
            "Authorization": f"Bot {self.client.token}",
            "Content-Type": "application/json"
        }
        json_data = {}
        if name:
            json_data["name"] = name
        if image_base64:
            json_data["image"] = image_base64

        response = self.client.session.patch(url, headers=headers, json=json_data)
        if response.status_code == 200:
            print(f"Successfully updated emoji: {emoji_id}")
            return response.json()
        else:
            print(f"Failed to update emoji: {response.status_code} {response.text}")
            return None

    def delete_emoji(self, guild_id, emoji_id):
        url = f"{self.client.base_url}/guilds/{guild_id}/emojis/{emoji_id}"
        headers = {
            "Authorization": f"Bot {self.client.token}"
        }

        response = self.client.session.delete(url, headers=headers)
        if response.status_code == 204:
            print(f"Successfully deleted emoji: {emoji_id}")
        else:
            print(f"Failed to delete emoji: {response.status_code} {response.text}")
