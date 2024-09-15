import requests

class WebhookManager:
    def __init__(self, client):
        self.client = client
        self.base_url = f"{self.client.base_url}/channels"

    def get_headers(self):
        return {
            "Authorization": f"Bot {self.client.token}",
            "Content-Type": "application/json"
        }

    def create_webhook(self, channel_id, name, avatar=None):
        url = f"{self.base_url}/{channel_id}/webhooks"
        data = {
            "name": name,
            "avatar": avatar
        }
        response = requests.post(url, headers=self.get_headers(), json=data)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to create webhook: {response.status_code} - {response.text}")
            return None

    def edit_webhook(self, webhook_id, name=None, avatar=None, channel_id=None):
        url = f"{self.client.base_url}/webhooks/{webhook_id}"
        data = {}
        if name:
            data["name"] = name
        if avatar:
            data["avatar"] = avatar
        if channel_id:
            data["channel_id"] = channel_id
        
        response = requests.patch(url, headers=self.get_headers(), json=data)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to edit webhook: {response.status_code} - {response.text}")
            return None

    def get_webhook(self, webhook_id):
        url = f"{self.client.base_url}/webhooks/{webhook_id}"
        response = requests.get(url, headers=self.get_headers())
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to retrieve webhook: {response.status_code} - {response.text}")
            return None

    def delete_webhook(self, webhook_id):
        url = f"{self.client.base_url}/webhooks/{webhook_id}"
        response = requests.delete(url, headers=self.get_headers())
        if response.status_code == 204:
            print(f"Webhook {webhook_id} deleted successfully.")
            return True
        else:
            print(f"Failed to delete webhook: {response.status_code} - {response.text}")
            return False

    def send_webhook_message(self, webhook_id, webhook_token, content, embeds=None, username=None, avatar_url=None):
        url = f"{self.client.base_url}/webhooks/{webhook_id}/{webhook_token}"
        data = {
            "content": content,
            "embeds": embeds or [],
            "username": username,
            "avatar_url": avatar_url
        }
        response = requests.post(url, json=data)
        if response.status_code == 204 or response.status_code == 200:
            print("Message sent successfully.")
        else:
            print(f"Failed to send message: {response.status_code} - {response.text}")
