from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from rooms.schemas import (
    RoomCreate, 
    RoomResponse, 
    RoomUpdate,
    AddMemberRequest,
    UpdateMemberRoleRequest,
    RoomMemberDetailResponse,
    RoomMemberResponse
)
from rooms.dep import (
    create_room,
    get_room_by_id,
    update_room,
    delete_room,
    get_rooms,
    add_member_to_room,
    remove_member_from_room,
    update_member_role,
    get_room_members
)
from auth.dep import get_current_user
from core.database import get_db
from auth.models import User



router = APIRouter(prefix="/rooms", tags=["Rooms"])


# ============================================
# CRUD операции для комнат
# ============================================

@router.post("/create", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
async def create_new_room(
    room_data: RoomCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Создать новую комнату
    
    - Создатель автоматически становится владельцем (OWNER)
    """
    return await create_room(db, room_data, current_user.id)
    

@router.get("/get_all", response_model=list[RoomResponse])
async def get_all_rooms(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить список всех комнат, где пользователь является участником
    """
    return await get_rooms(db, current_user.id)


@router.get("/{room_id}", response_model=RoomResponse)
async def get_room(
    room_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить информацию о комнате по ID
    """
    return await get_room_by_id(db, room_id)


@router.put("/{room_id}", response_model=RoomResponse)
async def update_room_info(
    room_id: int,
    room_data: RoomUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Обновить информацию о комнате
    
    - Только владелец или админ могут обновлять комнату
    """
    return await update_room(db, room_id, room_data, current_user.id)


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room_by_id(
    room_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Удалить комнату
    
    - Только владелец может удалить комнату
    """
    await delete_room(db, room_id, current_user.id)
    return None


# ============================================
# Управление участниками комнаты
# ============================================

@router.get("/{room_id}/members", response_model=list[RoomMemberDetailResponse])
async def get_members(
    room_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить список участников комнаты
    
    - Доступно только участникам комнаты
    """
    return await get_room_members(db, room_id, current_user.id)


@router.post("/{room_id}/members", response_model=RoomMemberResponse, status_code=status.HTTP_201_CREATED)
async def add_member(
    room_id: int,
    member_data: AddMemberRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Добавить участника в комнату
    
    - Только владелец или админ могут добавлять участников
    - По умолчанию новый участник получает роль MEMBER
    """
    return await add_member_to_room(
        db, 
        room_id, 
        member_data.user_id, 
        current_user.id,
        member_data.role
    )


@router.delete("/{room_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    room_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Удалить участника из комнаты
    
    Права на удаление:
    - Владелец может удалить любого (кроме себя)
    - Админ может удалить обычных участников
    - Участник может удалить только себя
    - Нельзя удалить владельца
    """
    await remove_member_from_room(db, room_id, user_id, current_user.id)
    return None


@router.patch("/{room_id}/members/{user_id}/role", response_model=RoomMemberResponse)
async def change_member_role(
    room_id: int,
    user_id: int,
    role_data: UpdateMemberRoleRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Изменить роль участника комнаты
    
    - Только владелец может менять роли
    - Нельзя изменить роль владельца
    - Нельзя назначить нового владельца через этот эндпоинт
    """
    return await update_member_role(
        db,
        room_id,
        user_id,
        role_data.role,
        current_user.id
    )