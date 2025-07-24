"""
HyperCLOVA X API 래퍼 – Chat Completions v3 + Function Calling
"""
import aiohttp, logging, json
from config import settings

class HyperClovaX:
    def __init__(self):
        self._url = f"{settings.CLOVA_ENDPOINT}/testapp/v1/chat-completions"
        self._headers = {
            "Authorization": f"Bearer {settings.HYPERCLOVA_X_API_KEY}",
            "Content-Type": "application/json"
        }

    async def chat(self, system: str, user: str, functions: list | None = None) -> dict:
        # NOTE: error-handling & retry omitted for brevity
        payload = {
            "model": "HyperCLOVA-X",
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ],
            "functions": functions or [],
            "temperature": 0.3
        }
        async with aiohttp.ClientSession() as s:
            async with s.post(self._url, headers=self._headers, json=payload) as r:
                if r.status != 200:
                    logging.error("HyperCLOVA X error %s", await r.text())
                return await r.json()
