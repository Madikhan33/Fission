from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from core.cache import cache
from .token_models import TokenBlacklist
from .schemas import BlacklistService
from .tokens import decode_token


async def is_token_blacklisted(tb: BlacklistService, db: AsyncSession) -> bool:
     
    # Проверка в кэше
    if await cache.get(f"blacklist:{tb.token}"):
        return True
    
    # Проверка в базе данных
    try:
        query = select(TokenBlacklist).where(TokenBlacklist.token == tb.token)
        result = await db.execute(query)
        token = result.scalar_one_or_none()

        # Добавляем в кэш
        if token:
            expire_in = int((token.expires_at - datetime.utcnow()).total_seconds())
            if expire_in > 0:
                # Используем префикс blacklist: для согласованности и аргумент ex
                await cache.set(f"blacklist:{tb.token}", "true", ex=expire_in)
            return True
        
        return False
        
    except Exception as e:
        print(f"Error checking blacklist in DB: {e}")
        # Возвращаем False при ошибке - токен считается не в blacklist
        return False


async def blacklist_token(tb: BlacklistService, db: AsyncSession) ->  TokenBlacklist:

    payload = decode_token(tb.token)
    if not payload:
        raise ValueError("Невалидный токен")


    expires_at = datetime.fromtimestamp(payload['exp'])
    expire_in = int((expires_at - datetime.utcnow()).total_seconds())
    if expire_in > 0:
        # Исправлен аргумент на ex (согласно core/cache.py)
        await cache.set(f'blacklist:{tb.token}', 'true', ex=expire_in)


    blacklist_entry = TokenBlacklist(
        token=tb.token,
        user_id=tb.user_id,
        token_type=tb.token_type,
        reason=tb.reason,
        expires_at=expires_at
    )
    db.add(blacklist_entry)
    await db.commit()
    await db.refresh(blacklist_entry)

    return blacklist_entry  




async def cleanup_expired_blacklist(db: AsyncSession) -> int:

    now = datetime.utcnow()
    
    query = delete(TokenBlacklist).where(TokenBlacklist.expires_at < now)
    result = await db.execute(query)
    await db.commit()
    return result.rowcount
