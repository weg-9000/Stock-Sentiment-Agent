"""
MCP(JSON-RPC 2.0 over HTTP/SSE) 공통 클라이언트
"""
import aiohttp, asyncio, logging, json

class MCPClient:
    def __init__(self) -> None:
        self._session: aiohttp.ClientSession | None = None
        self._tools: dict[str, dict[str, str]] = {}

    async def __aenter__(self):
        self._session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
        await self._discover()
        return self

    async def __aexit__(self, *exc):
        if self._session:
            await self._session.close()

    # ---------------------------------------------------------- #
    #                  PUBLIC  METHODS                           #
    # ---------------------------------------------------------- #
    async def call(self, server: str, tool: str, params: dict) -> dict:
        """
        MCP JSON-RPC 2.0 표준 호출
        """
        if server not in self._tools or tool not in self._tools[server]:
            raise ValueError(f"Tool {server}.{tool} not registered")
        url = self._tools[server][tool]
        payload = {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                   "params": {"name": tool, "arguments": params}}
        async with self._session.post(url, json=payload) as r:
            return await r.json()

    # ---------------------------------------------------------- #
    #                  INTERNAL HELPERS                          #
    # ---------------------------------------------------------- #
    async def _discover(self):
        """
        서버 엔드포인트·메타데이터 동적 검색  
        TODO: 실제 discovery URL 또는 static config 사용
        """
        self._tools = {
            "twitter": {
                "search_tweets": "http://localhost:8010",      # stub
                "get_trending_topics": "http://localhost:8010"
            },
            "alpha_vantage": {
                "get_quote": "http://localhost:8020",
                "get_news": "http://localhost:8020"
            }
        }
        logging.info("MCP tool discovery completed")
