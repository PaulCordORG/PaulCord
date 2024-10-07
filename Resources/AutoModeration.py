import aiohttp

class AutoModerationManager:
    def __init__(self, client):
        self.client = client
        self.base_url = f"{self.client.base_url}/guilds"

    @classmethod
    def get_headers(cls, client):
        return {
            "Authorization": f"Bot {client.token}",
            "Content-Type": "application/json"
        }

    @classmethod
    async def create_rule(cls, client, guild_id, name, event_type, trigger_type, trigger_metadata, actions, exempt_roles=None, exempt_channels=None):
        url = f"{client.base_url}/guilds/{guild_id}/auto-moderation/rules"
        payload = {
            "name": name,
            "event_type": event_type,
            "trigger_type": trigger_type,
            "trigger_metadata": trigger_metadata,
            "actions": actions,
            "exempt_roles": exempt_roles if exempt_roles else [],
            "exempt_channels": exempt_channels if exempt_channels else []
        }
        
        async with client.session.post(url, headers=cls.get_headers(client), json=payload) as response:
            if response.status == 200 or response.status == 201:
                rule = await response.json()
                print(f"Successfully created rule: {rule}") 
                return rule
            else:
                print(f"Failed to create rule: {response.status} - {await response.text()}")
                return None

    @classmethod
    async def get_rules(cls, client, guild_id):
        url = f"{client.base_url}/guilds/{guild_id}/auto-moderation/rules"
        async with client.session.get(url, headers=cls.get_headers(client)) as response:
            if response.status == 200:
                return await response.json()
            else:
                print(f"Failed to fetch rules: {response.status} - {await response.text()}")
                return None

    @classmethod
    async def get_rule(cls, client, guild_id, rule_id):
        url = f"{client.base_url}/guilds/{guild_id}/auto-moderation/rules/{rule_id}"
        async with client.session.get(url, headers=cls.get_headers(client)) as response:
            if response.status == 200:
                return await response.json()
            else:
                print(f"Failed to fetch rule: {response.status} - {await response.text()}")
                return None

    @classmethod
    async def modify_rule(cls, client, guild_id, rule_id, name=None, enabled=None, actions=None):
        url = f"{client.base_url}/guilds/{guild_id}/auto-moderation/rules/{rule_id}"
        data = {}
        if name:
            data["name"] = name
        if enabled is not None:
            data["enabled"] = enabled
        if actions:
            data["actions"] = actions

        async with client.session.patch(url, headers=cls.get_headers(client), json=data) as response:
            if response.status == 200:
                return await response.json()
            else:
                print(f"Failed to modify rule: {response.status} - {await response.text()}")
                return None

    @classmethod
    async def delete_rule(cls, client, guild_id, rule_id):
        url = f"{client.base_url}/guilds/{guild_id}/auto-moderation/rules/{rule_id}"
        async with client.session.delete(url, headers=cls.get_headers(client)) as response:
            if response.status == 204:
                print(f"Rule {rule_id} deleted successfully.")
                return True
            else:
                print(f"Failed to delete rule: {response.status} - {await response.text()}")
                return False
