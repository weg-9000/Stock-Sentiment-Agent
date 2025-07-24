import logging, asyncio
from mcp_client import MCPClient
from data_streamer import Streamer
from sentiment_analyzer import quick_sentiment, clova_sentiment
from storage.hot_db import HotDB

class StockSentimentAgent:
    def __init__(self):
        self.mcp: MCPClient | None = None
        self.stream = Streamer()
        self.db = HotDB()

    async def start(self):
        self.mcp = await MCPClient().__aenter__()
        await self.db.startup()
        logging.info("Agent up")

    async def stop(self):
        if self.mcp:
            await self.mcp.__aexit__()
        self.stream.producer.close()

    # ---------------- Core Logic ---------------- #
    async def collect(self, symbol: str):
        # 1. 데이터 수집
        tweets = await self.mcp.call("twitter", "search_tweets", {"query": symbol})
        quote  = await self.mcp.call("alpha_vantage", "get_quote", {"symbol": symbol})

        texts = [t["text"] for t in tweets.get("tweets", [])]
        # 2-1. 빠른 감정 (stream quality guard)
        base = [quick_sentiment(t) for t in texts]
        avg  = sum(b["score"] for b in base)/len(base) if base else .5

        # 2-2. HyperCLOVA X 정밀 분석
        detailed = await clova_sentiment(texts, quote)
        score = detailed.get("sentiment_score", avg)
        label = detailed.get("sentiment_label", "neutral")
        conf  = detailed.get("confidence", 0.5)

        # 3. 저장 + 스트림
        await self.db.put(symbol, score, label, conf)
        await self.stream.send("stock-sentiment",
                               key=symbol,
                               value={"symbol": symbol, "score": score,
                                      "label": label, "confidence": conf})

        logging.info("%s %.2f %s", symbol, score, label)