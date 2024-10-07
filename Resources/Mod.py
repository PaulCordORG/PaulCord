import datetime
import aiohttp

class ModerationManager:
    @classmethod
    async def ban(cls, client, guild_id, member_id, reason=None):
        url = f"{client.base_url}/guilds/{guild_id}/bans/{member_id}"
        headers = {
            "Authorization": f"Bot {client.token}",
            "Content-Type": "application/json"
        }
        json_data = {"reason": reason} if reason else {}

        try:
            async with client.session.put(url, headers=headers, json=json_data) as response:
                if response.status != 204: 
                    text = await response.text()
                    print(f"Failed to ban user: {response.status} {text}")
                    return None
                return response
        except aiohttp.ClientError as err:
            print(f"An error occurred while banning: {err}")
            return None

    @classmethod
    async def kick(cls, client, guild_id, member_id, reason=None):
        url = f"{client.base_url}/guilds/{guild_id}/members/{member_id}"
        headers = {
            "Authorization": f"Bot {client.token}",
            "Content-Type": "application/json"
        }
        json_data = {"reason": reason} if reason else {}

        try:
            async with client.session.delete(url, headers=headers, json=json_data) as response:
                if response.status != 204:
                    text = await response.text()
                    print(f"Failed to kick user: {response.status} {text}")
                    return None
                return response
        except aiohttp.ClientError as err:
            print(f"An error occurred while kicking: {err}")
            return None

    @classmethod
    async def timeout(cls, client, guild_id, member_id, duration, reason=None):
        url = f"{client.base_url}/guilds/{guild_id}/members/{member_id}"
        headers = {
            "Authorization": f"Bot {client.token}",
            "Content-Type": "application/json"
        }
        json_data = {
            "communication_disabled_until": (datetime.datetime.utcnow() + datetime.timedelta(seconds=duration)).isoformat()
        }
        if reason:
            json_data["reason"] = reason

        try:
            async with client.session.patch(url, headers=headers, json=json_data) as response:
                if response.status != 200:
                    text = await response.text()
                    print(f"Failed to timeout user: {response.status} {text}")
                    return None
                return response
        except aiohttp.ClientError as err:
            print(f"An error occurred while timing out: {err}")
            return None
