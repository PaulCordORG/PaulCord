import aiohttp

class InviteManager:
    @classmethod
    async def create(cls, client, channel_id, max_age=86400, max_uses=0, temporary=False, unique=True):
        url = f"{client.base_url}/channels/{channel_id}/invites"
        headers = {
            "Authorization": f"Bot {client.token}",
            "Content-Type": "application/json"
        }
        payload = {
            "max_age": max_age,
            "max_uses": max_uses,
            "temporary": temporary,
            "unique": unique
        }

        try:
            async with client.session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"Failed to create invite: {response.status} {await response.text()}")
                    return None
        except Exception as e:
            print(f"Error while creating invite: {e}")
            return None

    @classmethod
    async def delete(cls, client, invite_code):
        url = f"{client.base_url}/invites/{invite_code}"
        headers = {
            "Authorization": f"Bot {client.token}"
        }

        try:
            async with client.session.delete(url, headers=headers) as response:
                if response.status == 204:
                    print(f"Invite {invite_code} deleted successfully.")
                    return True
                else:
                    print(f"Failed to delete invite: {response.status} {await response.text()}")
                    return False
        except Exception as e:
            print(f"Error while deleting invite: {e}")
            return False

    @classmethod
    async def get_invite(cls, client, invite_code):
        url = f"{client.base_url}/invites/{invite_code}"
        headers = {
            "Authorization": f"Bot {client.token}"
        }

        try:
            async with client.session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"Failed to get invite info: {response.status} {await response.text()}")
                    return None
        except Exception as e:
            print(f"Error while fetching invite info: {e}")
            return None

    @classmethod
    async def get_channel(cls, client, channel_id):
        url = f"{client.base_url}/channels/{channel_id}/invites"
        headers = {
            "Authorization": f"Bot {client.token}"
        }

        try:
            async with client.session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"Failed to get channel invites: {response.status} {await response.text()}")
                    return None
        except Exception as e:
            print(f"Error while fetching channel invites: {e}")
            return None
