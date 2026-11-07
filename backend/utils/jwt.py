from datetime import datetime, timedelta

import jwt

from config import settings


def create_access_token(user_id:int):
    """创建JWT token"""
    expire = datetime.now()+timedelta(hours = settings.JWT_EXPIRE_HOURS)
    payload = {
        "user_id": user_id,
        "exp": expire
    }
    jwt_token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return jwt_token
def decode_access_token(token:str):
    """解析jwttoken"""
    res = jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM]
    )
    return res