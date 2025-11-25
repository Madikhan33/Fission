from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .token_models import RefreshTokenSession
from .tokens import decode_token
from .schemas import SessionService

#Создает запись сессии refresh токена.
async def create_refresh_session(session: SessionService, db: AsyncSession) -> Optional[RefreshTokenSession]:


    if not db:
        return None


    payload = decode_token(session.refresh_token)
    if not payload:
        return None


    expires_at = datetime.fromtimestamp(payload['exp'])
    
    session = RefreshTokenSession(
        user_id=session.user_id,
        access_token=session.access_token,
        refresh_token=session.refresh_token,
        expires_at=expires_at,
        device_name=session.device_name,
        ip_address=session.ip_address,
        user_agent=session.user_agent
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


#Обновляет время последнего использования сессии.
async def update_session_last_used(refresh_token: str, db: AsyncSession) -> Optional[RefreshTokenSession]:
    query = select(RefreshTokenSession).where(
        RefreshTokenSession.refresh_token == refresh_token,
        RefreshTokenSession.is_active == True
    )
    result = await db.execute(query)
    session = result.scalar_one_or_none()
    if session:
        session.last_used = datetime.utcnow()
        await db.commit()
        await db.refresh(session)
    
    return session
    


async def get_user_session(user_id: int, db: AsyncSession) -> Optional[RefreshTokenSession]:
    query = select(RefreshTokenSession).where(
        RefreshTokenSession.user_id == user_id,
        RefreshTokenSession.is_active == True,
        RefreshTokenSession.expires_at > datetime.utcnow()
    )
    result = await db.execute(query)
    session = result.scalar_one_or_none()
    return session


async def deactivate_session(refresh_token: str, db: AsyncSession) -> bool:
    query = select(RefreshTokenSession).where(
        RefreshTokenSession.refresh_token == refresh_token
    )
    result = await db.execute(query)
    session = result.scalar_one_or_none()
    if session:
        session.is_active = False
        await db.commit()
        return True
    return False



async def deactivate_all_user_sessions(user_id: str, db: AsyncSession, except_current: Optional[str] = None) -> bool:
    query = select(RefreshTokenSession).where(
        RefreshTokenSession.user_id == user_id,
        RefreshTokenSession.is_active == True,

    )

    if except_current:
        query = query.where(
            RefreshTokenSession.refresh_token != except_current
        )

    result = await db.execute(query)
    sessions = result.scalars().all()
   
    for session in sessions:
        session.is_active = False
        db.add(session)
    await db.commit()
    return len(sessions)
    
