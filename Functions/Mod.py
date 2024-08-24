import datetime

class ModerationManager:
    @classmethod
    def ban(cls, client, member_id, reason=None):
        url = f"{client.base_url}/guilds/{client.get_guild_id()}/bans/{member_id}"
        headers = {
            "Authorization": f"Bot {client.token}",
            "Content-Type": "application/json"
        }
        json_data = {"reason": reason} if reason else {}
        response = client.session.put(url, headers=headers, json=json_data)
        return response

    @classmethod
    def kick(cls, client, member_id, reason=None):
        url = f"{client.base_url}/guilds/{client.get_guild_id()}/members/{member_id}"
        headers = {
            "Authorization": f"Bot {client.token}",
            "Content-Type": "application/json"
        }
        json_data = {"reason": reason} if reason else {}
        response = client.session.delete(url, headers=headers, json=json_data)
        return response

    @classmethod
    def timeout(cls, client, member_id, duration, reason=None):
        url = f"{client.base_url}/guilds/{client.get_guild_id()}/members/{member_id}"
        headers = {
            "Authorization": f"Bot {client.token}",
            "Content-Type": "application/json"
        }
        json_data = {
            "communication_disabled_until": (datetime.datetime.utcnow() + datetime.timedelta(seconds=duration)).isoformat()
        }
        if reason:
            json_data["reason"] = reason
        response = client.session.patch(url, headers=headers, json=json_data)
        return response
