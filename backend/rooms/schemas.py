from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
from fastapi import Query
from rooms.models import RoomRole


# ============================================
# Room Create Schema
# ============================================

class RoomCreate(BaseModel):
    """Схема для создания комнаты"""
    name: str = Field(..., min_length=1, max_length=255, description="Название комнаты")
    description: str | None = Field(None, description="Описание комнаты")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Проект Alpha",
                "description": "Разработка новой функциональности"
            }
        }


# ============================================
# Room Member Schemas
# ============================================

class RoomMemberResponse(BaseModel):
    """Схема ответа для участника комнаты"""
    room_id: int
    user_id: int
    role: RoomRole
    joined_at: datetime
    invited_by_id: int | None = None
    
    class Config:
        from_attributes = True
        use_enum_values = True  # Сериализуем enum как строки


# ============================================
# Room Response Schema
# ============================================

class RoomResponse(BaseModel):
    """Схема ответа для комнаты"""
    id: int
    name: str
    description: str | None = None
    created_at: datetime
    created_by_id: int
    members: list[RoomMemberResponse] = []

    class Config:
        from_attributes = True


# ============================================
# Room Update Schema
# ============================================

class RoomUpdate(BaseModel):
    """Схема для обновления комнаты"""
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None


# ============================================
# User Brief Schema
# ============================================

class UserBrief(BaseModel):
    """Краткая информация о пользователе"""
    id: int
    username: str
    email: str
    
    class Config:
        from_attributes = True


# ============================================
# Room Member Management Schemas
# ============================================

class AddMemberRequest(BaseModel):
    """Запрос на добавление участника в комнату"""
    user_id: int = Field(..., gt=0, description="ID пользователя для добавления")
    role: RoomRole = Field(default=RoomRole.MEMBER, description="Роль участника")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 2,
                "role": "member"
            }
        }


class UpdateMemberRoleRequest(BaseModel):
    """Запрос на изменение роли участника"""
    role: RoomRole = Field(..., description="Новая роль участника")
    
    class Config:
        json_schema_extra = {
            "example": {
                "role": "admin"
            }
        }


# ============================================
# Extended Room Member Response
# ============================================

class RoomMemberDetailResponse(BaseModel):
    """Детальная информация об участнике комнаты"""
    room_id: int
    user_id: int
    role: RoomRole
    joined_at: datetime
    invited_by_id: int | None = None
    user: UserBrief
    
    class Config:
        from_attributes = True
        use_enum_values = True

