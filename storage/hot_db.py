import asyncpg, aioredis, logging
from config import settings

class HotDB:
    """
    PostgreSQL + Redis 캐시 (24h)
    """
    async def startup(self):
        self.pg = await asyncpg.create_pool(settings.POSTGRES_URL, min_size=1, max_size=5)
        self.cache = await aioredis.from_url(settings.REDIS_URL)
        await self._init_table()

    async def _init_table(self):
        async with self.pg.acquire() as c:
            await c.execute("""
            CREATE TABLE IF NOT EXISTS sentiment(
              id serial primary key,
              symbol varchar(10),
              score  float,
              label  varchar(20),
              confidence float,
              ts timestamp default now()
            );
            CREATE INDEX IF NOT EXISTS idx_symbol_ts ON sentiment(symbol, ts desc);
            """)

    async def put(self, symbol: str, score: float, label: str, confidence: float):
        async with self.pg.acquire() as c:
            await c.execute("INSERT INTO sentiment(symbol,score,label,confidence) VALUES ($1,$2,$3,$4)",
                            symbol, score, label, confidence)
        await self.cache.setex(f"sent:{symbol}", 300,
                               f"{score}|{label}|{confidence}")

    async def get_latest(self, symbol: str) -> tuple | None:
        cached = await self.cache.get(f"sent:{symbol}")
        if cached:
            s, l, c = cached.decode().split("|")
            return float(s), l, float(c)

        async with self.pg.acquire() as c:
            row = await c.fetchrow("SELECT score,label,confidence FROM sentiment"
                                   " WHERE symbol=$1 ORDER BY ts DESC LIMIT 1", symbol)
            return (row["score"], row["label"], row["confidence"]) if row else None