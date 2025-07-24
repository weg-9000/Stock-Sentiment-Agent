import asyncio, logging, sys
from agent import StockSentimentAgent
from scheduler import CollectorScheduler

logging.basicConfig(level=logging.INFO)

async def main(symbols: list[str]):
    agent = StockSentimentAgent()
    await agent.start()
    try:
        scheduler = CollectorScheduler(agent)
        await scheduler.run_forever(symbols)
    finally:
        await agent.stop()

if __name__ == "__main__":
    asyncio.run(main(sys.argv[1:] or ["AAPL","TSLA"]))
