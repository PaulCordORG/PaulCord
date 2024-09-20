import requests

class Guild:
    def __init__(self, client, guild_id):
        self.client = client
        self.guild_id = guild_id

    def fetch_member(self, user_id):
        url = f"{self.client.base_url}/members/{user_id}"
        headers = {
            "Authorization": f"Bot {self.client.token}"
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            member_data = response.json()
            return member_data
        else:
            print(f"Failed to fetch member {user_id}: {response.status_code} - {response.text}")
            return None

    def fetch_guild(self):
        url = self.base_url
        headers = {
            "Authorization": f"Bot {self.client.token}"
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            guild_data = response.json()
            return guild_data
        else:
            print(f"Failed to fetch guild {self.guild_id}: {response.status_code} - {response.text}")
            return None

    def get_display_name(self, member_data):
        return member_data.get('nick') or member_data['user']['username']

    def get_username(self, member_data):
        return member_data['user']['username']

    def get_profile_avatar(self, member_data):
        avatar = member_data['user'].get('avatar')
        if avatar:
            return f"https://cdn.discordapp.com/avatars/{member_data['user']['id']}/{avatar}.png"
        return None
