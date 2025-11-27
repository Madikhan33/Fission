from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from rooms.models import Room, RoomMember, RoomRole 
from rooms.schemas import RoomCreate
from auth.models import User


async def get_room_by_id(session: AsyncSession, room_id: int) -> Room:
    try:
        query = (
            select(Room)
            .options(selectinload(Room.members)) 
            .where(Room.id == room_id)
        )
        result = await session.execute(query)
        room = result.scalar_one_or_none()

        if room is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Room with id {room_id} not found"
            )

        return room

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while fetching room"
        )


async def create_room(session: AsyncSession, room_data: RoomCreate, user_id: int) -> Room:
    try:
        user = await session.get(User, user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            )

        new_room = Room(
            name=room_data.name,
            description=room_data.description,
            created_by_id=user_id
        )
   
        owner_member = RoomMember(
            user_id=user_id,
            role=RoomRole.OWNER,
            room=new_room
        )

        session.add(new_room)
        session.add(owner_member)

        await session.commit()
        await session.refresh(new_room)
        
        # Загружаем members для правильной сериализации
        return await get_room_by_id(session, new_room.id)

    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create room: {str(e)}"
        )


async def update_room(session: AsyncSession, room_id: int, room_data, user_id: int) -> Room:
    """Обновить информацию о комнате"""
    try:
        room = await get_room_by_id(session, room_id)
        
        member = await session.execute(
            select(RoomMember).where(
                RoomMember.room_id == room_id,
                RoomMember.user_id == user_id
            )
        )
        member = member.scalar_one_or_none()
        
        if not member or member.role not in [RoomRole.OWNER, RoomRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only room owner or admin can update room information"
            )
        
        update_data = room_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(room, field, value)
        
        await session.commit()
        
        # Возвращаем комнату с загруженными members
        return await get_room_by_id(session, room_id)
        
    except HTTPException:
        await session.rollback()
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update room: {str(e)}"
        )


async def delete_room(session: AsyncSession, room_id: int, user_id: int) -> None:
    try:
        room = await get_room_by_id(session, room_id)
        
        if room.created_by_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not the owner of this room"
            )

        await session.delete(room)
        await session.commit()

    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete room: {str(e)}"
        )


async def get_rooms(session: AsyncSession, user_id: int) -> list[Room]:
    """Получить все комнаты, где пользователь является участником"""
    try:
        rooms = await session.execute(
            select(Room)
            .join(RoomMember, Room.id == RoomMember.room_id)
            .options(selectinload(Room.members))
            .where(RoomMember.user_id == user_id)
        )
        return rooms.scalars().all()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get rooms: {str(e)}"
        )


async def add_member_to_room(
    session: AsyncSession, 
    room_id: int, 
    new_user_id: int, 
    inviter_id: int,
    role: RoomRole = RoomRole.MEMBER
) -> RoomMember:
    """Добавить участника в комнату"""
    try:
        room = await get_room_by_id(session, room_id)
        
        inviter_member = await session.execute(
            select(RoomMember).where(
                RoomMember.room_id == room_id,
                RoomMember.user_id == inviter_id
            )
        )
        inviter_member = inviter_member.scalar_one_or_none()
        
        if not inviter_member or inviter_member.role not in [RoomRole.OWNER, RoomRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only room owner or admin can add members"
            )
        
        new_user = await session.get(User, new_user_id)
        if not new_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {new_user_id} not found"
            )
        
        existing_member = await session.execute(
            select(RoomMember).where(
                RoomMember.room_id == room_id,
                RoomMember.user_id == new_user_id
            )
        )
        if existing_member.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member of this room"
            )
        
        new_member = RoomMember(
            room_id=room_id,
            user_id=new_user_id,
            role=role,
            invited_by_id=inviter_id
        )
        
        session.add(new_member)
        await session.commit()
        await session.refresh(new_member)
        
        return new_member
        
    except HTTPException:
        await session.rollback()
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add member: {str(e)}"
        )


async def remove_member_from_room(
    session: AsyncSession,
    room_id: int,
    user_id_to_remove: int,
    remover_id: int
) -> None:
    """Удалить участника из комнаты"""
    try:
        room = await get_room_by_id(session, room_id)
        
        remover_member = await session.execute(
            select(RoomMember).where(
                RoomMember.room_id == room_id,
                RoomMember.user_id == remover_id
            )
        )
        remover_member = remover_member.scalar_one_or_none()
        
        member_to_remove = await session.execute(
            select(RoomMember).where(
                RoomMember.room_id == room_id,
                RoomMember.user_id == user_id_to_remove
            )
        )
        member_to_remove = member_to_remove.scalar_one_or_none()
        
        if not member_to_remove:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User is not a member of this room"
            )
        
        if member_to_remove.role == RoomRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot remove room owner"
            )
        
        if remover_id == user_id_to_remove:
            pass
        elif remover_member and remover_member.role == RoomRole.OWNER:
            pass
        elif remover_member and remover_member.role == RoomRole.ADMIN:
            if member_to_remove.role != RoomRole.MEMBER:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin can only remove regular members"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to remove this member"
            )
        
        await session.delete(member_to_remove)
        await session.commit()
        
    except HTTPException:
        await session.rollback()
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove member: {str(e)}"
        )


async def update_member_role(
    session: AsyncSession,
    room_id: int,
    user_id: int,
    new_role: RoomRole,
    updater_id: int
) -> RoomMember:
    """Изменить роль участника комнаты"""
    try:
        room = await get_room_by_id(session, room_id)
        
        updater_member = await session.execute(
            select(RoomMember).where(
                RoomMember.room_id == room_id,
                RoomMember.user_id == updater_id
            )
        )
        updater_member = updater_member.scalar_one_or_none()
        
        if not updater_member or updater_member.role != RoomRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only room owner can change member roles"
            )
        
        member = await session.execute(
            select(RoomMember).where(
                RoomMember.room_id == room_id,
                RoomMember.user_id == user_id
            )
        )
        member = member.scalar_one_or_none()
        
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User is not a member of this room"
            )
        
        if member.role == RoomRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot change owner role"
            )
        
        if new_role == RoomRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot assign owner role. Use transfer ownership instead"
            )
        
        member.role = new_role
        await session.commit()
        await session.refresh(member)
        
        return member
        
    except HTTPException:
        await session.rollback()
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update member role: {str(e)}"
        )


async def get_room_members(session: AsyncSession, room_id: int, user_id: int) -> list[RoomMember]:
    """Получить список участников комнаты"""
    try:
        room = await get_room_by_id(session, room_id)
        
        user_member = await session.execute(
            select(RoomMember).where(
                RoomMember.room_id == room_id,
                RoomMember.user_id == user_id
            )
        )
        if not user_member.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You must be a member of the room to view its members"
            )
        
        members = await session.execute(
            select(RoomMember)
            .options(selectinload(RoomMember.user))
            .where(RoomMember.room_id == room_id)
        )
        
        return list(members.scalars().all())
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get room members: {str(e)}"
        )


async def check_room_access(session: AsyncSession, room_id: int, user_id: int) -> RoomMember:
    """Проверить доступ пользователя к комнате"""
    member = await session.execute(
        select(RoomMember).where(
            RoomMember.room_id == room_id,
            RoomMember.user_id == user_id
        )
    )
    member = member.scalar_one_or_none()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this room"
        )
    
    return member



