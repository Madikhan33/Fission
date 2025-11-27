from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from .security_service import decode_token
from auth.models import User
from sqlalchemy import select
from .security_service import is_token_blacklisted
from .security_service.schemas import BlacklistService
from .security_service.token_models import RefreshTokenSession

security = HTTPBearer()





#Получаем текущего пользователя
async def get_current_user(credentials: HTTPBearer = Depends(security), db: AsyncSession = Depends(get_db)) -> User:


    token = credentials.credentials


    blacklist_check = BlacklistService(
        token=token,
        user_id=0,
        token_type="access"
    )


    if await is_token_blacklisted(blacklist_check, db):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")

    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
    
    token_type = payload.get("type")
    if token_type != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")

    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
    


    try:
        user_id = int(user_id_str)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
    

    try:
        query = select(User).where(User.id == user_id)
        result = await db.execute(query)
        user = result.scalar_one_or_none()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not active")

    # Check if the session is still active
    

    return user

        


#Получаем текущего лидера
async def get_lead_user(current_user: Depends(get_current_user)) -> User:

    if not current_user.is_lead:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not a lead")
    
    return current_user


#Получаем текущего активного пользователя
async def get_is_active_user(current_user: Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not active")
    
    return current_user
    

