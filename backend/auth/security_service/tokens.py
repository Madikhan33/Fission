import jwt
from datetime import datetime, timedelta
from typing import Optional
from core.config import settings
from .schemas import TokenService


def create_access_token(token_service: TokenService) -> str:


    to_encode = {'sub': str(token_service.user_id), 'username': token_service.username, 'type': 'access'}

    if token_service.expires_delta:
        expire = datetime.utcnow() + token_service.expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    

    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(

        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def create_refresh_token(token_service: TokenService) -> str:

    to_encode = {'sub': str(token_service.user_id), 'username': token_service.username, 'type': 'refresh'}
    expier = datetime.utcnow() + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expier})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt



def decode_token(token: str) -> Optional[dict]:

    try:
        payload = jwt.decode(token,

        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM]

        )

        return payload

    except jwt.ExpiredSignatureError:
        return None

    except jwt.InvalidTokenError:
        return None



def get_token_expiry_minutes(token: str) -> Optional[int]:

    payload = decode_token(token)
    if not payload:
        return None

    exp_timestamp = payload.get('exp')
    if not exp_timestamp:
        return None

    now = datetime.utcnow().timestamp()
    remaining_seconds = exp_timestamp - now

    return max(0, int(remaining_seconds / 60))
    

    
   