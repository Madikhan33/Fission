from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=72)  # bcrypt max 72 bytes



class UserResponse(UserBase):
    id: int
    is_active: bool
    is_lead: bool
    created_at: datetime
    updated_at: datetime



    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenRefresh(BaseModel):
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8, max_length=72)  # bcrypt max 72 bytes


class SessionResponse(BaseModel):
    """Response model for user sessions"""
    id: int
    device_name: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime
    last_used_at: datetime  # Changed from last_used to match DB column
    expires_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True


