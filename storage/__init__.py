# storage/__init__.py
"""
Stock Sentiment Agent Storage Layer
- Hot: PostgreSQL + Redis (24시간)  
- Warm: InfluxDB + OpenSearch (30일)
- Cold: NAVER Cloud Object Storage (무제한)
"""

from .hot_db import HotDB
from .warm_db import WarmDB
from .cold_db import ColdStorage
from .vector_search import VectorSearch

__all__ = ['HotDB', 'WarmDB', 'ColdStorage', 'VectorSearch']

class StorageManager:
    """통합 스토리지 관리자"""
    
    def __init__(self):
        self.hot = HotDB()
        self.warm = WarmDB()
        self.cold = ColdStorage()
        self.vector = VectorSearch()
    
    async def startup(self):
        """모든 스토리지 초기화"""
        await self.hot.startup()
        await self.warm.startup()
        await self.cold.startup()
        # await self.vector.startup()  # 필요시 구현
    
    async def shutdown(self):
        """모든 스토리지 연결 종료"""
        await self.warm.shutdown()
        # Hot DB와 Cold Storage는 자동 정리
