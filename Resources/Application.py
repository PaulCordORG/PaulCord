import aiohttp

class Application:
    def __init__(self, client):
        self.client = client
        self.base_url = f"{self.client.base_url}/applications/{self.client.application_id}"

    @classmethod
    def get_headers(cls, client):
        return {
            "Authorization": f"Bot {client.token}",
            "Content-Type": "application/json"
        }

    @classmethod
    async def get_application_details(cls, client):
        url = f"{client.base_url}/applications/{client.application_id}"
        headers = {
            "Authorization": f"Bot {client.token}"
        }
        async with client.session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                print(f"Failed to fetch application details: {response.status} - {await response.text()}")
                return None

    @classmethod
    async def update_application(cls, client, **kwargs):
        url = f"{client.base_url}/applications/@me"
        async with client.session.patch(url, headers=cls.get_headers(client), json=kwargs) as response:
            if response.status == 200:
                return await response.json()
            else:
                print(f"Failed to update application: {response.status} - {await response.text()}")
                return None