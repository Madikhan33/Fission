from typing import Optional
from datetime import timedelta
from pydantic import BaseModel


class BlacklistService(BaseModel):

    token: str
    user_id: int
    token_type: str
    reason: Optional[str] = None



class TokenService(BaseModel):
    user_id: int
    username: str
    expires_delta: Optional[timedelta] = None



class SessionService(BaseModel):
    user_id: int
    access_token: str
    refresh_token: str
    device_name: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

