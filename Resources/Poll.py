import aiohttp

class PollManager:
    def __init__(self, client):
        self.client = client
        self.base_url = f"{self.client.base_url}/channels"

    def get_headers(self):
        return {
            "Authorization": f"Bot {self.client.token}",
            "Content-Type": "application/json"
        }

    async def create_poll(self, channel_id, question, answers, duration=None, allow_multiselect=False, layout_type=1):
        url = f"{self.base_url}/{channel_id}/messages"
        data = {
            "content": "New Poll",
            "poll": {
                "question": {"text": question},
                "answers": [{"text": answer} for answer in answers],
                "allow_multiselect": allow_multiselect,
                "layout_type": layout_type,
            }
        }

        if duration:
            data["poll"]["duration"] = duration * 3600

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=self.get_headers(), json=data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"Failed to create poll: {response.status} - {await response.text()}")
                    return None

    async def get_answer_voters(self, channel_id, message_id, answer_id, limit=25, after=None):
        url = f"{self.base_url}/{channel_id}/polls/{message_id}/answers/{answer_id}"
        params = {
            "limit": limit,
        }
        if after:
            params["after"] = after

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.get_headers(), params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"Failed to retrieve answer voters: {response.status} - {await response.text()}")
                    return None

    async def end_poll(self, channel_id, message_id):
        url = f"{self.base_url}/{channel_id}/polls/{message_id}/expire"

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=self.get_headers()) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"Failed to end poll: {response.status} - {await response.text()}")
                    return None

    async def get_poll_results(self, channel_id, message_id):
        url = f"{self.base_url}/{channel_id}/polls/{message_id}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.get_headers()) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"Failed to retrieve poll results: {response.status} - {await response.text()}")
                    return None

    async def delete_poll(self, channel_id, message_id):
        url = f"{self.base_url}/{channel_id}/polls/{message_id}"

        async with aiohttp.ClientSession() as session:
            async with session.delete(url, headers=self.get_headers()) as response:
                if response.status == 204:
                    print(f"Poll {message_id} deleted successfully.")
                    return True
                else:
                    print(f"Failed to delete poll: {response.status} - {await response.text()}")
                    return False
