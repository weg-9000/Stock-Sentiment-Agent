"""
백그라운드 수집·집계 스케줄러 (apscheduler / asyncio tasks)
"""
import asyncio, logging
from datetime import timedelta

class CollectorScheduler:
    def __init__(self, agent):
        self.agent = agent

    async def run_forever(self, symbols: list[str]):
        while True:
            await asyncio.gather(*(self.agent.collect(symbol) for symbol in symbols))
            await asyncio.sleep(60)   # 1 분 주기
