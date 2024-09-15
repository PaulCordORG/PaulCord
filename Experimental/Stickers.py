import requests

class StickerSender:
    def __init__(self, client):
        self.client = client

    def send_sticker(self, channel_id, sticker_id):
        url = f"{self.client.base_url}/channels/{channel_id}/messages"
        headers = {
            "Authorization": f"Bot {self.client.token}",
            "Content-Type": "application/json"
        }
        payload = {
            "sticker_ids": [sticker_id]
        }

        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            print("Sticker sent successfully!")
        else:
            print(f"Failed to send sticker: {response.status_code} - {response.text}")
