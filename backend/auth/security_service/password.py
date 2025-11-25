import bcrypt
from core.config import settings



def hash_password(password: str) -> str:
    password_bytes = password.encode('utf-8')[:72]

    salt = bcrypt.gensalt(rounds=settings.BCRYPT_ROUNDS)
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    
    return hashed_password.decode('utf-8')
    



def verify_password(password: str, hashed_password: str) -> bool:
    
    password_bytes = password.encode('utf-8')[:72]
    hashed_password_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_password_bytes)
    

