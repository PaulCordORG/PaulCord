import aiohttp

class EntitlementManager:
    def __init__(self, client):
        self.client = client
        self.base_url = f"{self.client.base_url}/entitlements"

    def get_headers(self):
        return {
            "Authorization": f"Bot {self.client.token}",
            "Content-Type": "application/json"
        }

    async def list_entitlements(self, application_id, sku_ids=None, user_id=None, guild_id=None):
        params = {"application_id": application_id}
        if sku_ids:
            params["sku_ids"] = ",".join(sku_ids)
        if user_id:
            params["user_id"] = user_id
        if guild_id:
            params["guild_id"] = guild_id

        url = f"{self.base_url}"
        async with self.client.session.get(url, headers=self.get_headers(), params=params) as response:
            if response.status == 200:
                return await response.json()
            else:
                print(f"Failed to list entitlements: {response.status} - {await response.text()}")
                return None

    async def consume_entitlement(self, entitlement_id):
        url = f"{self.base_url}/{entitlement_id}/consume"
        async with self.client.session.post(url, headers=self.get_headers()) as response:
            if response.status == 204:
                print(f"Entitlement {entitlement_id} consumed successfully.")
                return True
            else:
                print(f"Failed to consume entitlement: {response.status} - {await response.text()}")
                return False

    async def create_test_entitlement(self, application_id, sku_id, user_id, guild_id=None):
        url = f"{self.base_url}/test-entitlements"
        data = {
            "application_id": application_id,
            "sku_id": sku_id,
            "user_id": user_id,
            "guild_id": guild_id
        }

        async with self.client.session.post(url, headers=self.get_headers(), json=data) as response:
            if response.status == 200:
                return await response.json()
            else:
                print(f"Failed to create test entitlement: {response.status} - {await response.text()}")
                return None

    async def delete_test_entitlement(self, entitlement_id):
        url = f"{self.base_url}/test-entitlements/{entitlement_id}"
        async with self.client.session.delete(url, headers=self.get_headers()) as response:
            if response.status == 204:
                print(f"Test entitlement {entitlement_id} deleted successfully.")
                return True
            else:
                print(f"Failed to delete test entitlement: {response.status} - {await response.text()}")
                return False
