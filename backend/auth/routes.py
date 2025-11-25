from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import get_db
from auth.security_service import (
    create_access_token, create_refresh_token, decode_token, get_token_expiry_minutes,
    TokenService, get_password_hash, verify_password, create_refresh_session, SessionService
)
from auth.models import User
from auth.schemas import UserCreate, UserResponse, UserLogin, TokenResponse
from auth.dep import (
    get_current_user,
    get_lead_user,
    get_is_active_user
)
from datetime import timedelta

router = APIRouter()

@router.post('/register', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    query = select(User).where(User.email == user_data.email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    
    query = select(User).where(User.username == user_data.username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    
    hashed_password = get_password_hash(user_data.password)
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        is_lead=user_data.is_lead,
        is_active=user_data.is_active
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


@router.post('/login', response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(credentials: UserLogin, request: Request, db: AsyncSession = Depends(get_db)):
    query = select(User).where((User.email == credentials.email) | (User.username == credentials.username))
    
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not active")
    
    access_token = create_access_token(TokenService(user_id=user.id, username=user.username))
    refresh_token = create_refresh_token(TokenService(user_id=user.id, username=user.username))

    client_host = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")

    session_service = SessionService(
        user_id=user.id,
        access_token=access_token,
        refresh_token=refresh_token,
        ip_address=client_host,
        user_agent=user_agent
    )

    await create_refresh_session(
        session=session_service,
        db=db
    )
    
    expires_in = get_token_expiry_minutes(access_token)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=expires_in or 0
    )