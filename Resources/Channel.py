class ChannelManager:
    def __init__(self, client):
        self.client = client

    def create_channel(self, name, type_):
        url = f"{self.client.base_url}/guilds/{self.client.get_guild_id()}/channels"
        headers = {
            "Authorization": f"Bot {self.client.token}",
            "Content-Type": "application/json"
        }
        json_data = {
            "name": name,
            "type": type_
        }
        response = self.client.session.post(url, headers=headers, json=json_data)
        if response.status_code == 201:
            return response.json()
        else:
            print(f"Failed to create channel: {response.status_code} {response.text}")
            return None

    def edit_channel(self, channel_id, new_name):
        url = f"{self.client.base_url}/channels/{channel_id}"
        headers = {
            "Authorization": f"Bot {self.client.token}",
            "Content-Type": "application/json"
        }
        json_data = {
            "name": new_name
        }
        response = self.client.session.patch(url, headers=headers, json=json_data)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to edit channel: {response.status_code} {response.text}")
            return None

    def delete_channel(self, channel_id):
        url = f"{self.client.base_url}/channels/{channel_id}"
        headers = {
            "Authorization": f"Bot {self.client.token}"
        }
        response = self.client.session.delete(url, headers=headers)
        if response.status_code == 204:
            return {"status": "Channel deleted successfully"}
        else:
            print(f"Failed to delete channel: {response.status_code} {response.text}")
            return None

    def list_channels(self):
        url = f"{self.client.base_url}/guilds/{self.client.get_guild_id()}/channels"
        headers = {
            "Authorization": f"Bot {self.client.token}"
        }
        response = self.client.session.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to list channels: {response.status_code} {response.text}")
            return None
