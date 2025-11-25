import redis.asyncio as aioredis
from typing import Optional
from core.config import settings


class RedisCache:
    def __init__(self):
        self.redis = None

    async def connect(self):
        try:
            self.redis = await aioredis.from_url(
                f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
                encoding="utf8",
                decode_responses=True
            )
            print('Redis подключен')
        except:
            print('Redis не подключен')
            self.redis = None

    async def disconnect(self):
        if self.redis:
            await self.redis.close()
            print('Redis отключен')

    async def set(self, key: str, value: str, ex: Optional[int] = None):
        if not self.redis:
            return
        try:
            if ex:
                await self.redis.setex(key, ex, value)
            else:
                await self.redis.set(key, value)
        except:
            print('Ошибка при записи в Redis')

    async def get(self, key: str):
        if not self.redis:
            return None
        try:
            return await self.redis.get(key)
        except:
            print('Ошибка при чтении из Redis')
            return None

    async def delete(self, key: str):
        if not self.redis:
            return
        try:
            await self.redis.delete(key)
        except:
            print('Ошибка при удалении из Redis')

    async def exists(self, key: str):
        if not self.redis:
            return False
        try:
            return bool(await self.redis.exists(key))
        except:
            print('Ошибка при проверке наличия в Redis')
            return False


cache = RedisCache()