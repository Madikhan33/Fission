from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import get_db
from auth.security_service import (
    create_access_token, create_refresh_token, decode_token, get_token_expiry_minutes,
    TokenService, get_password_hash, verify_password, create_refresh_session, SessionService,
    deactivate_session
)
from auth.security_service.token_models import RefreshTokenSession
from auth.models import User
from auth.schemas import UserCreate, UserResponse, UserLogin, TokenResponse, SessionResponse, TokenRefresh
from auth.dep import (
    get_current_user,
    get_lead_user,
    get_is_active_user,
    security  # Import security instance
)
from datetime import timedelta, datetime

router = APIRouter(prefix='/auth')

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
        is_active=True,
        is_lead=False
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


@router.post('/login', response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(credentials: UserLogin, request: Request, db: AsyncSession = Depends(get_db)):
    query = select(User).where(User.username == credentials.username)
    
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


@router.get('/me', response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current authenticated user information"""
    return current_user


@router.post('/logout', status_code=status.HTTP_200_OK)
async def logout(
    current_user: User = Depends(get_current_user),
    credentials: HTTPBearer = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    #Получаем токен
    access_token = credentials.credentials
    
    # Найти сессию по токену
    query = select(RefreshTokenSession).where(
        RefreshTokenSession.token == access_token,
        RefreshTokenSession.user_id == current_user.id,
        RefreshTokenSession.is_active == True
    )
    result = await db.execute(query)
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid or expired token"
        )
    
    # Деактивируем сессию вместо удаления (лучше для аудита)
    session.is_active = False
    await db.commit()
    
    return {"message": "Logout successful"}






@router.post('/refresh', response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def refresh_token(token_data: TokenRefresh, db: AsyncSession = Depends(get_db)):
    # 1. Проверяем валидность refresh токена (подпись и срок действия)
    payload = decode_token(token_data.refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
        
    user_id = int(payload.get("sub"))
    username = payload.get("username")
    
    # 2. Ищем активную сессию в БД по этому refresh токену
    query = select(RefreshTokenSession).where(
        RefreshTokenSession.refresh_token == token_data.refresh_token,
        RefreshTokenSession.is_active == True
    )
    result = await db.execute(query)
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session not found or expired"
        )
        
    # 3. Генерируем новые токены (Refresh Token Rotation)
    token_service = TokenService(user_id=user_id, username=username)
    new_access_token = create_access_token(token_service)
    new_refresh_token = create_refresh_token(token_service)
    
    # 4. Обновляем сессию в БД новыми данными
    # Важно обновить и access token (поле token), так как проверка сессии идет по нему
    session.token = new_access_token
    session.refresh_token = new_refresh_token
    
    # Обновляем время истечения сессии (берем из нового refresh токена)
    new_refresh_payload = decode_token(new_refresh_token)
    session.expires_at = datetime.fromtimestamp(new_refresh_payload['exp'])
    session.last_used_at = datetime.utcnow()
    
    await db.commit()
    
    expires_in = get_token_expiry_minutes(new_access_token)
    
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        expires_in=expires_in or 0
    )


@router.get('/sessions', response_model=list[SessionResponse], status_code=status.HTTP_200_OK)
async def get_user_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    #Получаем все сессии текущего пользователя
    query = select(RefreshTokenSession).where(
        RefreshTokenSession.user_id == current_user.id
    ).order_by(RefreshTokenSession.created_at.desc())
    
    result = await db.execute(query)
    sessions = result.scalars().all()
    
    return sessions


@router.post('/logout-all', status_code=status.HTTP_200_OK)
async def logout_all_devices(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    #Выходим из всех устройств деактивируя все сессии пользователя
    query = select(RefreshTokenSession).where(
        RefreshTokenSession.user_id == current_user.id,
        RefreshTokenSession.is_active == True
    )
    result = await db.execute(query)
    sessions = result.scalars().all()
    
    count = 0
    for session in sessions:
        session.is_active = False
        count += 1
    
    await db.commit()
    
    return {
        "message": f"Logged out from {count} device(s)",
        "sessions_terminated": count
    }


@router.delete('/sessions/{session_id}', status_code=status.HTTP_200_OK)
async def logout_specific_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    #Выходим из конкретной сессии по ID
    query = select(RefreshTokenSession).where(
        RefreshTokenSession.id == session_id,
        RefreshTokenSession.user_id == current_user.id
    )
    result = await db.execute(query)
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    if not session.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session is already inactive"
        )
    
    session.is_active = False
    await db.commit()
    
    return {"message": "Session terminated successfully"}


@router.get('/users', response_model=list[UserResponse], status_code=status.HTTP_200_OK)
async def get_all_users(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all users - This endpoint returns ALL users (not recommended for teams page)"""
    query = select(User).where(User.is_active == True)
    result = await db.execute(query)
    users = result.scalars().all()
    return users


@router.get('/team-members', response_model=list[UserResponse], status_code=status.HTTP_200_OK)
async def get_team_members(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get team members - users who are in the same rooms as the current user.
    This is the correct endpoint to use for the Teams page.
    """
    from rooms.models import RoomMember
    
    # Get all room IDs where current user is a member
    rooms_query = select(RoomMember.room_id).where(
        RoomMember.user_id == current_user.id
    )
    rooms_result = await db.execute(rooms_query)
    user_room_ids = [row[0] for row in rooms_result.all()]
    
    if not user_room_ids:
        # User is not in any rooms, return empty list
        return []
    
    # Get all user IDs who are members of those rooms
    members_query = select(RoomMember.user_id).where(
        RoomMember.room_id.in_(user_room_ids)
    ).distinct()
    members_result = await db.execute(members_query)
    team_user_ids = [row[0] for row in members_result.all()]
    
    # Get user details for those IDs
    users_query = select(User).where(
        User.id.in_(team_user_ids),
        User.is_active == True
    )
    users_result = await db.execute(users_query)
    users = users_result.scalars().all()
    
    return users

